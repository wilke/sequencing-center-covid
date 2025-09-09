# Validation Checklist for Freyja Version Parameterization

## Critical Gaps Identified

### 1. Missing Components
- [ ] **process-run.sh not modified** - It also references freyja_latest.sif directly
- [ ] **create-pileups.sh not modified** - Hard-coded freyja_latest.sif reference
- [ ] **No version in Makefile symlink** - Using freyja.1.5.3 format vs 1.5.3
- [ ] **Missing midnight primer support** - process-covid-run doesn't handle it

### 2. Syntax Issues to Check
- [ ] Makefile tab vs space indentation (critical for Make)
- [ ] Shell script quote escaping in error messages
- [ ] Variable expansion in Makefile
- [ ] Symlink resolution logic

### 3. Testing Requirements
- [ ] Test with actual sample data
- [ ] Test with each primer type (qiagen, swift, midnight)
- [ ] Test version validation with non-existent version
- [ ] Test symlink warning for latest
- [ ] Test provenance file creation

### 4. Integration Points
- [ ] assembly.sh compatibility
- [ ] Database update mechanism
- [ ] Output file version tracking
- [ ] Log file generation

## GitHub Issues to Create

### Core Implementation
1. **Fix Makefile syntax and validation logic**
   - Validate tab indentation
   - Test variable expansion
   - Verify validate-version target

2. **Update process-run.sh for version support**
   - Use FREYJA_VERSION environment variable
   - Log version information

3. **Update create-pileups.sh for version support**
   - Replace hard-coded container path
   - Use FREYJA_VERSION variable

4. **Add midnight primer support**
   - Update process-covid-run validation
   - Test with midnight primer samples

### Testing
5. **Create test dataset for validation**
   - Small FASTQ files for quick testing
   - Sample mapping file
   - Known expected outputs

6. **Implement integration tests**
   - End-to-end pipeline test
   - Version switching test
   - Error handling test

### Documentation
7. **Update inline documentation**
   - Add comments to Makefile
   - Document version format requirements
   - Add troubleshooting section

### Validation
8. **Syntax validation suite**
   - Makefile syntax checker
   - Shell script validation
   - YAML/JSON config validation

## Validation Commands

```bash
# Check Makefile syntax
make -n -f /local/incoming/covid/config/Makefile validate-version

# Check shell script syntax
bash -n /nfs/seq-data/covid/sequencing-center-covid/scripts/process-covid-run

# Test variable expansion
FREYJA_VERSION=test make -n -f /local/incoming/covid/config/Makefile validate-version 2>&1

# Check if tabs are correct in Makefile
cat -A /local/incoming/covid/config/Makefile | grep -E "^\t"
```

## Acceptance Test Plan

### Phase 1: Syntax Validation
1. Validate Makefile syntax
2. Validate shell script syntax
3. Check variable expansion

### Phase 2: Unit Testing
1. Test version validation function
2. Test environment variable handling
3. Test parameter precedence

### Phase 3: Integration Testing
1. Run with tiny test dataset
2. Verify output files created
3. Check version tracking files
4. Validate provenance records

### Phase 4: Acceptance Testing
1. Run with real sample (1 file)
2. Compare outputs with production
3. Verify no regression
4. Check performance impact