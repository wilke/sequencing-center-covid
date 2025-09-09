# Software Engineering Plan: Freyja Version Parameterization

## Validation of Approach

### ✅ Good Practices We're Following:
1. **Modify existing files** instead of creating duplicates
2. **Feature branching** for isolated development
3. **Atomic commits** for clear history
4. **Backward compatibility** maintained
5. **Documentation within code** (not separate files)
6. **Test-driven development** approach

### ❌ Anti-patterns We're Avoiding:
1. Creating `Makefile.parameterized` (duplicate file)
2. Creating `process-covid-run-parameterized` (duplicate script)
3. Proliferation of documentation files
4. Breaking existing workflows
5. Large monolithic commits

## GitHub Workflow Plan

### 1. Issue Creation
```markdown
Title: Add Freyja version parameterization to COVID pipeline

## Description
Enable flexible Freyja version selection for testing and validation while maintaining backward compatibility.

## Acceptance Criteria
- [ ] Pipeline accepts optional version parameter
- [ ] Environment variable support
- [ ] Default behavior unchanged
- [ ] Provenance tracking implemented
- [ ] Tests pass for all versions

## Technical Approach
- Modify existing Makefile to accept FREYJA_VERSION parameter
- Update process-covid-run to pass version through
- Add validation and logging

Labels: enhancement, pipeline, testing
Milestone: v2.1.0
```

### 2. Branch Strategy
```bash
# Create feature branch
git checkout -b feature/freyja-version-control

# Or more specific
git checkout -b feature/issue-123-freyja-parameterization
```

### 3. Implementation Plan (Clean Repo Approach)

#### Commit 1: Add version parameter to Makefile
```bash
# Modify EXISTING /local/incoming/covid/config/Makefile
git add config/Makefile
git commit -m "feat(makefile): add FREYJA_VERSION parameter support

- Add FREYJA_VERSION variable with 'latest' default
- Direct path construction using freyja_${FREYJA_VERSION}.sif
- Add version validation before execution
- Add provenance tracking for reproducibility

Refs: #123"
```

#### Commit 2: Update process-covid-run script
```bash
# Modify EXISTING scripts/process-covid-run
git add scripts/process-covid-run
git commit -m "feat(pipeline): add optional freyja version parameter

- Add third optional parameter for version selection
- Priority: CLI > env var > default
- Add version validation with helpful error messages
- Maintain backward compatibility

Refs: #123"
```

#### Commit 3: Update process-run.sh for version passing
```bash
# Modify EXISTING scripts/process-run.sh
git add scripts/process-run.sh
git commit -m "feat(process-run): respect FREYJA_VERSION environment variable

- Use FREYJA_VERSION if set in environment
- Log version information to summary files
- No breaking changes to existing usage

Refs: #123"
```

#### Commit 4: Add tests
```bash
# Create tests IN EXISTING test directory structure
git add tests/test_freyja_versions.sh
git commit -m "test: add Freyja version switching tests

- Test default behavior unchanged
- Test version parameter passing
- Test environment variable precedence
- Test invalid version handling

Refs: #123"
```

#### Commit 5: Update documentation
```bash
# Update EXISTING README.md - don't create new docs
git add README.md
git commit -m "docs: document Freyja version control usage

- Add version parameter to usage examples
- Document environment variable option
- Add troubleshooting section
- Update requirements section

Refs: #123"
```

### 4. File Modifications (NOT New Files)

#### `/local/incoming/covid/config/Makefile`
```diff
+ # Version configuration - backward compatible
+ FREYJA_VERSION ?= latest
- SINGULARITY := /local/incoming/covid/config/freyja_latest.sif
+ SINGULARITY := /local/incoming/covid/config/freyja_$(FREYJA_VERSION).sif

+ # Validation before execution
+ $(VARIANTS): validate-version

+ .PHONY: validate-version
+ validate-version:
+     @test -f "$(SINGULARITY)" || (echo "ERROR: $(SINGULARITY) not found" && exit 1)
```

#### `/nfs/seq-data/covid/sequencing-center-covid/scripts/process-covid-run`
```diff
  primer=$2
+ # Optional version parameter (backward compatible)
+ freyja_version=${3:-${FREYJA_VERSION:-latest}}

+ # Validate version exists
+ if [ ! -f "/local/incoming/covid/config/freyja_${freyja_version}.sif" ]; then
+     echo "ERROR: Freyja version '${freyja_version}' not found"
+     exit 1
+ fi

+ # Pass version to process-run
+ export FREYJA_VERSION=${freyja_version}
  sh /local/incoming/covid/scripts/process-run.sh ${covid_run_dir}
```

### 5. Testing Strategy

Create a SINGLE test file in existing test structure:
```bash
#!/bin/bash
# tests/test_freyja_versions.sh

# Test 1: Default behavior unchanged
./process-covid-run test_data qiagen
assert_uses_latest

# Test 2: Specific version
./process-covid-run test_data qiagen 2.0.0
assert_uses_version "2.0.0"

# Test 3: Environment variable
FREYJA_VERSION=1.5.3 ./process-covid-run test_data qiagen
assert_uses_version "1.5.3"

# Test 4: CLI overrides env
FREYJA_VERSION=1.5.3 ./process-covid-run test_data qiagen 2.0.0
assert_uses_version "2.0.0"
```

### 6. Pull Request Template
```markdown
## Description
Adds flexible Freyja version selection to COVID pipeline while maintaining full backward compatibility.

## Type of Change
- [ ] Bug fix
- [x] New feature (backward compatible)
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Modified Makefile to accept FREYJA_VERSION parameter
- Updated process-covid-run to pass version through
- Added validation and error handling
- Implemented provenance tracking

## Testing
- [x] Tested with default (latest) version
- [x] Tested with explicit version 1.5.3
- [x] Tested with explicit version 2.0.0
- [x] Tested environment variable precedence
- [x] Tested invalid version handling
- [x] Verified backward compatibility

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Comments added for complex sections
- [x] Documentation updated
- [x] No new warnings generated
- [x] Tests pass locally
- [x] Dependent changes merged

Closes #123
```

### 7. Git Tags for Releases
```bash
# After merge to main
git tag -a v2.1.0 -m "Add Freyja version parameterization

Features:
- Flexible version selection
- Environment variable support
- Provenance tracking
- Backward compatible"

git push origin v2.1.0
```

## Clean Repository Benefits

1. **Single Source of Truth**: One Makefile, one process-covid-run script
2. **Clear Git History**: Atomic commits show evolution
3. **Easy Rollback**: Can revert single commits if needed
4. **Reduced Confusion**: No duplicate files with similar names
5. **Maintainability**: Updates go to one place
6. **Documentation**: Inline with code, not scattered

## GitHub Contribution Metrics

This approach generates:
- 1 Issue (created and closed)
- 1 Feature branch
- 5-6 Atomic commits
- 1 Pull request
- 1 Version tag
- Multiple file modifications (counts as contributions)

## Anti-patterns Avoided

❌ **DON'T**:
```bash
# Creating duplicate files
cp Makefile Makefile.parameterized
cp process-covid-run process-covid-run-v2
```

✅ **DO**:
```bash
# Modify existing files
git diff Makefile  # Shows changes to existing file
```

❌ **DON'T**:
```bash
# One giant commit
git add -A
git commit -m "Add version support"
```

✅ **DO**:
```bash
# Atomic commits
git add Makefile
git commit -m "feat(makefile): add version parameter"
```

## Implementation Order

1. **Create GitHub issue** for tracking
2. **Create feature branch** from main
3. **Modify Makefile** (existing file)
4. **Test locally** with different versions
5. **Modify process-covid-run** (existing file)
6. **Test integration** end-to-end
7. **Update README** (existing file)
8. **Create pull request** with template
9. **Code review** and iterate
10. **Merge and tag** release

## Success Criteria

- ✅ Zero new script files created
- ✅ Existing workflows continue unchanged
- ✅ Clear commit history
- ✅ Comprehensive test coverage
- ✅ Documentation in-place
- ✅ Clean pull request