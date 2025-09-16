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
- `latest` - Current production version (symlink)
- `2.0.0-09_08_2025-00-34-2025-09-08` - Latest version with ampliconstat feature
- `1.5.3-03_07_2025-01-59-2025-03-10` - Stable version (92.72% concordance with v2.0.0)
- Additional versions in `/local/incoming/covid/config/`

📖 **[Detailed Freyja Version Usage Guide](docs/FREYJA_VERSION_USAGE.md)**

### Version Selection Priority

1. Command-line argument (highest)
2. FREYJA_VERSION environment variable
3. Default 'latest' symlink

### Quick Version Check
```bash
# List available versions
ls -1 /local/incoming/covid/config/freyja_*.sif | sed 's/.*freyja_//' | sed 's/.sif//'

# Check what 'latest' points to
readlink /local/incoming/covid/config/freyja_latest.sif

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
