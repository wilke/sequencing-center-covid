# Freyja Version Parameterization Analysis

## Proposed Approach

1. Use "latest" as default version instead of specific version numbers
2. Allow version setting via environment variable
3. Pass version through command line from process-covid-run

## Analysis of Counterpoints and Considerations

### 1. Using "latest" as Default

**Benefits**:
- ✅ Follows existing convention (current symlink: freyja_latest.sif)
- ✅ Zero changes for existing users
- ✅ Automatic updates when symlink changes
- ✅ Production continuity maintained

**Counterpoints/Risks**:
- ⚠️ **Reproducibility Issue**: "latest" changes over time, making results non-reproducible
- ⚠️ **Audit Trail**: Difficult to track which version was used for specific runs
- ⚠️ **Unexpected Changes**: Silent updates could introduce breaking changes
- ⚠️ **Debugging Complexity**: Hard to diagnose issues without knowing exact version

**Mitigation**:
```bash
# Log the actual version being used
ACTUAL_VERSION=$(readlink /local/incoming/covid/config/freyja_${FREYJA_VERSION}.sif)
echo "Using Freyja: ${ACTUAL_VERSION}" >> ${LOG_FILE}
```

### 2. Environment Variable Approach

**Benefits**:
- ✅ Clean separation of configuration from code
- ✅ Easy cluster-wide configuration
- ✅ Works well with job schedulers (SLURM, etc.)
- ✅ No command line changes needed

**Counterpoints/Risks**:
- ⚠️ **Hidden Configuration**: Not obvious which version is running
- ⚠️ **Environment Pollution**: Could conflict with other tools
- ⚠️ **Inheritance Issues**: Child processes might not inherit variable
- ⚠️ **Documentation Burden**: Users need to know about env var

**Example Issue**:
```bash
# User sets environment variable
export FREYJA_VERSION=2.0.0

# But forgets it's set, runs pipeline days later
./process-covid-run  # Unexpectedly uses 2.0.0
```

### 3. Command Line Parameter Approach

**Benefits**:
- ✅ Explicit version selection
- ✅ Self-documenting commands
- ✅ Clear in logs and history
- ✅ No hidden state

**Counterpoints/Risks**:
- ⚠️ **Breaking Change**: Modifies existing command interface
- ⚠️ **Backward Compatibility**: Existing scripts would break
- ⚠️ **Parameter Proliferation**: Adding more parameters makes CLI complex
- ⚠️ **Default Handling**: Need logic for optional parameter

### 4. Order of Precedence Issues

**Proposed Precedence**:
1. Command line parameter (highest priority)
2. Environment variable
3. Default "latest" (lowest priority)

**Potential Confusion**:
```bash
export FREYJA_VERSION=1.5.3
./process-covid-run /data qiagen 2.0.0  # Which wins?
```

**Counterpoint**: Multiple override levels increase complexity and debugging difficulty.

## Alternative Approaches to Consider

### A. Configuration File Approach
```yaml
# /local/incoming/covid/config/pipeline.conf
freyja:
  version: latest
  fallback: 1.5.3
  allowed: [1.5.3, 2.0.0]
```

**Pros**: Centralized config, validation, versioning
**Cons**: Additional file to maintain, parsing overhead

### B. Symlink-per-Environment
```bash
freyja_production.sif -> freyja_1.5.3.sif
freyja_testing.sif -> freyja_2.0.0.sif
freyja_latest.sif -> freyja_production.sif
```

**Pros**: Clear environment separation
**Cons**: More symlinks to manage

### C. Version Locking Mechanism
```bash
# .freyja-version file in run directory
echo "1.5.3" > .freyja-version
```

**Pros**: Run-specific versioning, git-trackable
**Cons**: Another file to manage

## Recommended Implementation Strategy

### Hybrid Approach (Best of All Worlds)

```bash
# 1. Makefile changes
FREYJA_VERSION ?= latest  # Default to latest
FREYJA_SIF := freyja_$(FREYJA_VERSION).sif

# Handle special case for "latest"
ifeq ($(FREYJA_VERSION),latest)
    SINGULARITY := /local/incoming/covid/config/freyja_latest.sif
else
    SINGULARITY := /local/incoming/covid/config/freyja_$(FREYJA_VERSION).sif
endif

# 2. process-covid-run changes
# Make version optional third parameter
primer=$2
version=${3:-${FREYJA_VERSION:-latest}}  # CLI > ENV > default

# 3. Version logging
echo "Freyja version requested: ${version}" >> run.log
echo "Freyja file used: $(readlink -f ${SINGULARITY})" >> run.log
```

## Critical Counterpoints Summary

### 1. **Reproducibility Concern** (HIGHEST PRIORITY)
**Issue**: Using "latest" makes experiments non-reproducible
**Solution**: Always log actual version used, not just "latest"

### 2. **Breaking Changes Risk**
**Issue**: Existing pipelines might break with parameter changes
**Solution**: Make version parameter optional, maintain backward compatibility

### 3. **Version Validation**
**Issue**: User might specify non-existent version
**Solution**: Add validation check:
```bash
if [ ! -f "/local/incoming/covid/config/freyja_${version}.sif" ]; then
    echo "Error: Freyja version ${version} not found"
    echo "Available versions:"
    ls /local/incoming/covid/config/freyja_*.sif
    exit 1
fi
```

### 4. **Parallel Execution Conflicts**
**Issue**: Environment variable could affect parallel runs
**Solution**: Use command-line parameter for explicit control

### 5. **Audit and Compliance**
**Issue**: Regulatory requirements might need version tracking
**Solution**: Create version manifest file for each run:
```json
{
  "run_id": "20250909_batch_001",
  "freyja_version": "2.0.0",
  "freyja_file": "freyja_2.0.0-09_08_2025-00-34-2025-09-08.sif",
  "freyja_md5": "abc123...",
  "timestamp": "2025-09-09T10:30:00Z"
}
```

## Final Recommendations

### DO Implement:
1. ✅ **Optional version parameter** in process-covid-run (backward compatible)
2. ✅ **Environment variable support** with clear precedence
3. ✅ **"latest" as default** to maintain current behavior
4. ✅ **Version logging** in all output files
5. ✅ **Validation checks** for specified versions

### DON'T Implement:
1. ❌ **Mandatory version parameter** (breaks existing workflows)
2. ❌ **Silent version switching** without logging
3. ❌ **Complex precedence rules** (keep it simple)
4. ❌ **Automatic updates** of "latest" during runs

### Implementation Priority:
1. **Phase 1**: Makefile parameterization with "latest" default
2. **Phase 2**: Environment variable support
3. **Phase 3**: Command-line parameter in process-covid-run
4. **Phase 4**: Comprehensive logging and validation

## Security Considerations

- **Container Verification**: Check container signatures before execution
- **Path Traversal**: Validate version strings to prevent directory traversal
- **Permissions**: Ensure containers have appropriate permissions
- **Network Isolation**: Consider network policies for different versions