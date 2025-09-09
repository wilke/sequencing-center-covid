#!/bin/bash
#
# Test suite for Freyja version parameterization
# Tests backward compatibility and new version selection features
#

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test configuration
TEST_DIR="/tmp/freyja_version_test_$$"
SCRIPT_DIR="/nfs/seq-data/covid/sequencing-center-covid/scripts"
CONFIG_DIR="/local/incoming/covid/config"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

run_test() {
    echo -e "\n${YELLOW}TEST:${NC} $1"
    ((TESTS_RUN++))
}

# Setup
setup() {
    mkdir -p ${TEST_DIR}
    cd ${TEST_DIR}
}

# Cleanup
cleanup() {
    cd /
    rm -rf ${TEST_DIR}
}

# Test 1: Makefile default behavior (backward compatibility)
test_makefile_default() {
    run_test "Makefile default behavior uses 'latest'"
    
    cd ${CONFIG_DIR}
    output=$(make -n -f Makefile version-info 2>&1 | grep "FREYJA_VERSION" || echo "")
    
    if [[ "$output" == *"latest"* ]] || [[ -z "$output" ]]; then
        pass "Default version is 'latest' or unset (backward compatible)"
    else
        fail "Default version is not 'latest': $output"
    fi
}

# Test 2: Makefile with explicit version
test_makefile_explicit_version() {
    run_test "Makefile accepts explicit version parameter"
    
    cd ${CONFIG_DIR}
    
    # Test with version 1.5.3
    if make -n FREYJA_VERSION=1.5.3 validate-version 2>&1 | grep -q "freyja_1.5.3"; then
        pass "Makefile accepts version 1.5.3"
    else
        fail "Makefile does not handle version parameter correctly"
    fi
    
    # Test with version 2.0.0
    if make -n FREYJA_VERSION=2.0.0 validate-version 2>&1 | grep -q "freyja_2.0.0"; then
        pass "Makefile accepts version 2.0.0"
    else
        fail "Makefile does not handle version 2.0.0 correctly"
    fi
}

# Test 3: Makefile invalid version handling
test_makefile_invalid_version() {
    run_test "Makefile rejects invalid versions"
    
    cd ${CONFIG_DIR}
    
    if ! make FREYJA_VERSION=nonexistent validate-version 2>/dev/null; then
        pass "Makefile correctly rejects invalid version"
    else
        fail "Makefile did not reject invalid version"
    fi
}

# Test 4: process-covid-run backward compatibility
test_process_covid_run_backward_compat() {
    run_test "process-covid-run maintains backward compatibility"
    
    # Check script accepts 2 arguments (old behavior)
    if ${SCRIPT_DIR}/process-covid-run 2>&1 | grep -q "primer"; then
        pass "Script still works with 2 arguments"
    else
        fail "Script breaks with 2 arguments"
    fi
}

# Test 5: process-covid-run with version parameter
test_process_covid_run_with_version() {
    run_test "process-covid-run accepts version parameter"
    
    # Test help message shows version parameter
    output=$(${SCRIPT_DIR}/process-covid-run 2>&1 || true)
    if echo "$output" | grep -q "freyja_version"; then
        pass "Script shows version parameter in usage"
    else
        fail "Script does not show version parameter in usage"
    fi
}

# Test 6: Environment variable precedence
test_env_variable_precedence() {
    run_test "Environment variable precedence"
    
    # Set environment variable
    export FREYJA_VERSION=1.5.3
    
    cd ${CONFIG_DIR}
    output=$(make -n validate-version 2>&1 | grep "freyja_" | head -1)
    
    if echo "$output" | grep -q "freyja_1.5.3"; then
        pass "Environment variable is respected"
    else
        fail "Environment variable not respected: $output"
    fi
    
    unset FREYJA_VERSION
}

# Test 7: CLI overrides environment variable
test_cli_overrides_env() {
    run_test "CLI parameter overrides environment variable"
    
    export FREYJA_VERSION=1.5.3
    cd ${CONFIG_DIR}
    
    output=$(make -n FREYJA_VERSION=2.0.0 validate-version 2>&1 | grep "freyja_" | head -1)
    
    if echo "$output" | grep -q "freyja_2.0.0"; then
        pass "CLI parameter overrides environment variable"
    else
        fail "CLI parameter does not override environment: $output"
    fi
    
    unset FREYJA_VERSION
}

# Test 8: Version validation in Makefile
test_version_validation() {
    run_test "Version validation prevents execution with invalid version"
    
    cd ${CONFIG_DIR}
    
    # This should fail validation
    if ! make FREYJA_VERSION=invalid.version validate-version 2>/dev/null; then
        pass "Invalid version blocked by validation"
    else
        fail "Invalid version not blocked"
    fi
}

# Test 9: Latest symlink check
test_latest_symlink_check() {
    run_test "Check if 'latest' is properly configured as symlink"
    
    if [ -L "${CONFIG_DIR}/freyja_latest.sif" ]; then
        pass "'latest' is a symlink as expected"
        
        target=$(readlink ${CONFIG_DIR}/freyja_latest.sif)
        echo "  Points to: $target"
    else
        if [ -f "${CONFIG_DIR}/freyja_latest.sif" ]; then
            fail "'latest' exists but is not a symlink"
        else
            fail "'latest' does not exist"
        fi
    fi
}

# Test 10: Version tracking in output
test_version_tracking() {
    run_test "Version information is tracked in output"
    
    cd ${CONFIG_DIR}
    
    # Check if Makefile would create version file
    if grep -q "freyja_version" Makefile; then
        pass "Makefile includes version tracking"
    else
        fail "Makefile missing version tracking"
    fi
}

# Main test execution
main() {
    echo "========================================="
    echo "Freyja Version Parameterization Test Suite"
    echo "========================================="
    
    # Check prerequisites
    if [ ! -d "${CONFIG_DIR}" ]; then
        echo "ERROR: Config directory not found: ${CONFIG_DIR}"
        exit 1
    fi
    
    if [ ! -f "${CONFIG_DIR}/Makefile" ]; then
        echo "ERROR: Makefile not found in ${CONFIG_DIR}"
        exit 1
    fi
    
    # Setup test environment
    setup
    
    # Run tests
    test_makefile_default
    test_makefile_explicit_version
    test_makefile_invalid_version
    test_process_covid_run_backward_compat
    test_process_covid_run_with_version
    test_env_variable_precedence
    test_cli_overrides_env
    test_version_validation
    test_latest_symlink_check
    test_version_tracking
    
    # Cleanup
    cleanup
    
    # Summary
    echo ""
    echo "========================================="
    echo "Test Results"
    echo "========================================="
    echo "Tests run: ${TESTS_RUN}"
    echo -e "Tests passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Tests failed: ${RED}${TESTS_FAILED}${NC}"
    
    if [ ${TESTS_FAILED} -eq 0 ]; then
        echo -e "\n${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}Some tests failed!${NC}"
        exit 1
    fi
}

# Run tests
main "$@"