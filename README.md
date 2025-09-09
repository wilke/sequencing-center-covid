# sequencing-center-covid

Scripts for processing assemblies, creating plots and reports

## Features

- SARS-CoV-2 genome assembly and analysis
- Variant calling using Freyja
- Lineage analysis and demixing
- Flexible Freyja version selection for testing and validation

## Usage

### Basic Usage (unchanged)
```bash
# Standard execution (uses latest Freyja version)
./scripts/process-covid-run /path/to/sequencing/run qiagen

# Supported primers: qiagen, swift, midnight
./scripts/process-covid-run /path/to/sequencing/run midnight
```

### Freyja Version Control (new)
```bash
# Use specific Freyja version (full version string required)
./scripts/process-covid-run /path/to/sequencing/run qiagen 2.0.0-09_08_2025-00-34-2025-09-08

# Set version via environment variable
export FREYJA_VERSION=1.5.3-07_14_2025-00-44-2025-07-14
./scripts/process-covid-run /path/to/sequencing/run swift

# Direct Makefile usage with version
cd /local/incoming/covid/runs/your_run
make FREYJA_VERSION=2.0.0-09_08_2025-00-34-2025-09-08 strain
```

### Available Freyja Versions
- `latest` - Current production version (symlink to 2.0.0)
- `2.0.0-09_08_2025-00-34-2025-09-08` - Current latest with ampliconstat feature
- `1.5.3-07_14_2025-00-44-2025-07-14` - Previous stable version from July 2025
- `1.5.2-01_06_2025-02-03-2025-01-06` - Earlier version available

### Version Comparison Experiments
```bash
# Run same samples with different versions for comparison
FREYJA_VERSION=1.5.3-07_14_2025-00-44-2025-07-14 make strain
mv output output_v1.5.3

FREYJA_VERSION=2.0.0-09_08_2025-00-34-2025-09-08 make strain
mv output output_v2.0.0

# Compare results
diff output_v1.5.3/sample.out output_v2.0.0/sample.out
```

## Testing

Run the test suite to verify version switching:
```bash
./tests/test_freyja_versions.sh
```

## Provenance Tracking

Each run now records the Freyja version used:
- Version information saved in `output/*.freyja_version` for each sample
- Full container path tracked for reproducibility
