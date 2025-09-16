# Freyja Version Selection Guide

## Overview

The COVID sequencing pipeline supports flexible Freyja version selection, allowing users to specify which version of the Freyja lineage calling software to use for their analysis. This feature enables:
- Testing new versions before production deployment
- Reproducible analysis with specific versions
- Parallel comparison of different versions
- Backward compatibility with existing workflows

## Quick Start

### Using process-covid-run Script

The simplest way to run the pipeline with a specific Freyja version:

```bash
# Use a specific version
./process-covid-run /path/to/run qiagen 2.0.0-09_08_2025-00-34-2025-09-08

# Use the latest version (default)
./process-covid-run /path/to/run qiagen
```

### Using the Makefile Directly

For more control over the analysis:

```bash
# Specify version as parameter
make FREYJA_VERSION=1.5.3-03_07_2025-01-59-2025-03-10 strain

# Use environment variable
export FREYJA_VERSION=1.5.3-03_07_2025-01-59-2025-03-10
make strain
```

## Available Versions

To see all available Freyja versions:

```bash
ls -1 /local/incoming/covid/config/freyja_*.sif | sed 's/.*freyja_//' | sed 's/.sif//'
```

Current versions (as of 2025-09-16):
- `latest` (symlink to current production version)
- `1.5.3-03_07_2025-01-59-2025-03-10`
- `2.0.0-09_08_2025-00-34-2025-09-08`

## Version Selection Methods

### Priority Order

The version selection follows this priority (highest to lowest):

1. **Command-line argument** to process-covid-run
2. **FREYJA_VERSION environment variable**
3. **Default**: `latest` (symlink to production version)

### Method 1: Command-Line Argument

Best for: One-off analyses with specific versions

```bash
./process-covid-run /path/to/run midnight 1.5.3-03_07_2025-01-59-2025-03-10
```

### Method 2: Environment Variable

Best for: Multiple runs with the same version

```bash
# Set for current session
export FREYJA_VERSION=2.0.0-09_08_2025-00-34-2025-09-08

# Run multiple analyses
./process-covid-run /path/to/run1 qiagen
./process-covid-run /path/to/run2 swift
```

### Method 3: Makefile Parameter

Best for: Direct Makefile invocation and testing

```bash
cd /path/to/run
make FREYJA_VERSION=1.5.3-03_07_2025-01-59-2025-03-10 strain
```

## Use Cases

### Testing a New Version

Compare results between versions on the same dataset:

```bash
# Process with current production version
./process-covid-run /path/to/run qiagen
mv output output_latest

# Process with new version
./process-covid-run /path/to/run qiagen 2.0.0-09_08_2025-00-34-2025-09-08
mv output output_v2.0.0

# Compare results
diff output_latest output_v2.0.0
```

### Reproducible Analysis

Ensure consistent results by specifying exact version:

```bash
# Document the version used
echo "FREYJA_VERSION=1.5.3-03_07_2025-01-59-2025-03-10" > analysis.config

# Run with specific version
source analysis.config
./process-covid-run /path/to/run swift
```

### Batch Processing with Specific Version

Process multiple runs with a consistent version:

```bash
#!/bin/bash
# batch_process.sh

FREYJA_VERSION="2.0.0-09_08_2025-00-34-2025-09-08"
export FREYJA_VERSION

for run in /local/incoming/covid/runs/*/; do
    echo "Processing $run with Freyja $FREYJA_VERSION"
    ./process-covid-run "$run" qiagen
done
```

## Validation and Error Handling

### Version Validation

The pipeline automatically validates that the specified version exists:

```bash
# This will error if version doesn't exist
./process-covid-run /path/to/run qiagen invalid_version

# Output:
# ERROR: Freyja version 'invalid_version' not found
# Available versions:
#   - latest
#   - 1.5.3-03_07_2025-01-59-2025-03-10
#   - 2.0.0-09_08_2025-00-34-2025-09-08
```

### Checking Current Version

To verify which version will be used:

```bash
# Check symlink target for 'latest'
readlink /local/incoming/covid/config/freyja_latest.sif

# Check if a specific version exists
ls -la /local/incoming/covid/config/freyja_2.0.0-09_08_2025-00-34-2025-09-08.sif
```

## Best Practices

### 1. Document Version Used

Always record the Freyja version in your analysis logs:

```bash
# In your analysis script
echo "Analysis date: $(date)" > analysis.log
echo "Freyja version: ${FREYJA_VERSION:-latest}" >> analysis.log
```

### 2. Use Explicit Versions for Production

For reproducibility, use explicit version numbers rather than 'latest':

```bash
# Good - explicit and reproducible
./process-covid-run /path/to/run qiagen 1.5.3-03_07_2025-01-59-2025-03-10

# Less ideal - 'latest' can change
./process-covid-run /path/to/run qiagen
```

### 3. Test Before Deploying

Test new versions on a subset before full deployment:

```bash
# Test on one run
./process-covid-run /test/run qiagen 2.0.0-09_08_2025-00-34-2025-09-08

# If successful, deploy more broadly
export FREYJA_VERSION=2.0.0-09_08_2025-00-34-2025-09-08
```

## Troubleshooting

### Issue: Version Not Found

**Error**: `ERROR: Freyja version 'x.x.x' not found`

**Solution**:
- Check available versions: `ls /local/incoming/covid/config/freyja_*.sif`
- Use the full version string including date stamp
- Verify the container file exists and is readable

### Issue: Permission Denied

**Error**: `Permission denied accessing freyja_version.sif`

**Solution**:
- Check file permissions: `ls -la /local/incoming/covid/config/freyja_*.sif`
- Ensure you're in the correct user group
- Contact system administrator if needed

### Issue: Inconsistent Results

**Symptom**: Different results when running same data

**Solution**:
- Verify version used: Check logs for "Using Freyja version:"
- Ensure consistent version across runs
- Check for 'latest' symlink changes

### Issue: Performance Differences

**Symptom**: Analysis takes longer with certain versions

**Solution**:
- Different versions may have performance characteristics
- Check system resources during run
- Consider parallel processing limits

## Advanced Configuration

### Setting Default Version

To change the default version (requires admin access):

```bash
# Update the 'latest' symlink
cd /local/incoming/covid/config
ln -sf freyja_2.0.0-09_08_2025-00-34-2025-09-08.sif freyja_latest.sif
```

### Version Comparison Script

For systematic version comparison:

```bash
#!/bin/bash
# compare_versions.sh

RUN_PATH=$1
PRIMER=$2

for version in "1.5.3-03_07_2025-01-59-2025-03-10" "2.0.0-09_08_2025-00-34-2025-09-08"; do
    echo "Processing with Freyja $version"
    ./process-covid-run "$RUN_PATH" "$PRIMER" "$version"
    mv output "output_$version"
    mv variants "variants_$version"
done

# Compare outputs
echo "Comparing results..."
diff -r output_1.5.3* output_2.0.0*
```

## Related Documentation

- [Freyja Version Comparison Experiment](./Freyja-Version-Comparison-Experiment.md)
- [Pipeline Overview](../README.md)
- [Makefile Documentation](../config/Makefile)
- [Process Scripts Guide](../scripts/README.md)

## Support

For issues or questions about Freyja version selection:
1. Check this documentation
2. Review error messages and logs
3. Check GitHub issues: https://github.com/wilke/sequencing-center-covid/issues
4. Contact the bioinformatics team

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.5.3 | 2025-03-10 | Current production version |
| 2.0.0 | 2025-09-08 | Latest version, 92.72% concordance with 1.5.3 |

Last updated: 2025-09-16