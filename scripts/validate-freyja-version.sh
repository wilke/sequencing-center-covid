#!/bin/bash
# validate-freyja-version.sh - Quick validation script for Freyja container versions
# Usage: ./validate-freyja-version.sh <version>

VERSION=${1:-latest}
CONFIG_DIR="/local/incoming/covid/config"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "==================================="
echo "Freyja Version Validation Script"
echo "==================================="
echo ""

# Determine container path
if [ "$VERSION" = "latest" ]; then
    CONTAINER="${CONFIG_DIR}/freyja_latest.sif"
else
    # Try different naming patterns
    if [ -f "${CONFIG_DIR}/freyja.${VERSION}.sif" ]; then
        CONTAINER="${CONFIG_DIR}/freyja.${VERSION}.sif"
    elif [ -f "${CONFIG_DIR}/freyja_${VERSION}.sif" ]; then
        CONTAINER="${CONFIG_DIR}/freyja_${VERSION}.sif"
    else
        # Look for version with timestamp
        CONTAINER=$(ls ${CONFIG_DIR}/freyja*${VERSION}*.sif 2>/dev/null | head -n1)
    fi
fi

# Check if container exists
if [ ! -f "$CONTAINER" ]; then
    echo -e "${RED}ERROR: Container not found for version ${VERSION}${NC}"
    echo "Searched for: ${CONTAINER}"
    echo ""
    echo "Available versions:"
    ls ${CONFIG_DIR}/freyja*.sif 2>/dev/null | xargs -n1 basename
    exit 1
fi

echo -e "${GREEN}✓${NC} Container found: $(basename $CONTAINER)"
echo "  Size: $(ls -lh $CONTAINER | awk '{print $5}')"
echo "  Date: $(ls -lh $CONTAINER | awk '{print $6, $7, $8}')"
echo ""

# Test basic Freyja commands
echo "Testing Freyja commands..."
echo "--------------------------"

# Test version command
echo -n "1. Version check... "
if singularity exec $CONTAINER freyja --version &>/dev/null; then
    VERSION_OUTPUT=$(singularity exec $CONTAINER freyja --version 2>&1)
    echo -e "${GREEN}✓${NC} $VERSION_OUTPUT"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test help command
echo -n "2. Help command... "
if singularity exec $CONTAINER freyja --help &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test variants command availability
echo -n "3. Variants command... "
if singularity exec $CONTAINER freyja variants --help &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test demix command availability
echo -n "4. Demix command... "
if singularity exec $CONTAINER freyja demix --help &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Failed${NC}"
fi

# Test plot command availability
echo -n "5. Plot command... "
if singularity exec $CONTAINER freyja plot --help &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Not available (may be expected)${NC}"
fi

# Check for database files
echo ""
echo "Checking database files..."
echo "--------------------------"
echo -n "Barcodes... "
if singularity exec $CONTAINER ls /data/usher_barcodes.csv &>/dev/null || \
   singularity exec $CONTAINER ls /usr/local/lib/python*/site-packages/freyja/data/usher_barcodes.csv &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ May need update${NC}"
fi

echo ""
echo "==================================="
echo -e "${GREEN}Validation complete!${NC}"
echo "==================================="