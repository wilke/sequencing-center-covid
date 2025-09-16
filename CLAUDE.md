# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a SARS-CoV-2 sequencing center pipeline for processing viral assemblies, creating analytical reports, and managing wastewater surveillance data. The repository contains scripts for parallel sequence assembly processing, variant calling, pileup analysis, and automated data workflows for COVID surveillance.

## Key Development Commands

### Assembly Processing Pipeline
```bash
# Run parallel assemblies with specific primer sets
./scripts/parallel-assemblies-v2.pl -n <threads> -p <primer_set> < sample_mapping.tsv

# Supported primer sets: ARTIC, midnight, qiagen, swift, varskip, varskip-long
# For ARTIC, specify version: -v [3, 4, 4.1]
./scripts/parallel-assemblies-v2.pl -n 8 -p ARTIC -v 4.1 < data/sample-mapping.tsv
```

### Variant Calling and Analysis
```bash
# Process BAM files through Freyja pipeline (requires Makefile in run directory)
make variants/SAMPLE.variants.tsv
make strain  # Process all BAM files

# Parse pileup files for SNP analysis with configurable thresholds
./scripts/parse_pileup-v12.pl -f 0.05 < input.pileup > output.parsed.tab
```

### Run Processing Workflow
```bash
# Initialize new run directory structure
./scripts/setup.sh /path/to/run

# Process complete run through full pipeline
./scripts/process-run.sh /path/to/run

# Create pileup files for detailed variant analysis
./scripts/create-pileups.sh
```

### Data Processing and Aggregation
```bash
# Convert staging BAM files to dated BAM structure
python3 scripts/staging2bam.py -m sample-mapping.tsv -s ./staging/ -d ./bam/

# Generate coverage summaries and reports
./scripts/create_summary.sh
./scripts/out2spreadsheet.sh

# Merge and aggregate location data
python3 scripts/samples2aggregates.py
python3 scripts/labels2aggregates.py
```

## Architecture Overview

### Core Processing Scripts
- **`parallel-assemblies-v2.pl`**: Main assembly orchestration using `sars2-onecodex` with multi-primer support
- **`parse_pileup-v12.pl`**: SNP extraction from mpileup files with configurable fraction thresholds (default 0.05)
- **`process-run.sh`**: Complete run processing pipeline from raw data to analysis
- **`staging2bam.py`**: BAM file organization with sample mapping integration

### Directory Structure Pattern
Each run follows standardized structure:
```
/local/incoming/covid/runs/RUNID/
├── samples/          # Raw FASTQ files
├── staging/          # Intermediate BAM files  
├── bam/             # Final organized BAM files with dates
├── variants/        # Freyja variant call outputs (.variants.tsv)
├── output/          # Freyja demix lineage results
├── depth/           # Coverage depth files
└── Assemblies/      # Assembly intermediate files
```

### Configuration Dependencies
- **Freyja Singularity container**: `/local/incoming/covid/config/freyja_latest.sif`
- **Reference genome**: `MN908947.3.trimmed.fa` (SARS-CoV-2)
- **Sample mapping format**: TSV with `sample_id`, `sample_collect_date`, `sample_location_specify`, `wwtp_name`, `site_id`

### Processing Flow
1. **Setup**: `setup.sh` creates directory structure and copies FASTQ files
2. **Assembly**: `parallel-assemblies-v2.pl` runs primer-specific assemblies using `sars2-onecodex`
3. **BAM Processing**: Move and organize BAM files with `staging2bam.py`
4. **Variant Calling**: Makefile orchestrates Freyja variants and demix steps
5. **Analysis**: Various scripts for pileup analysis, coverage, and reporting

### Key File Formats
- **Sample mapping**: `.sample-mapping.tsv` files link samples to metadata
- **Variants**: `.variants.tsv` files from Freyja variant calling
- **Pileup analysis**: Parsed pileup files for detailed SNP analysis
- **Assembly logs**: Standard assembly processing logs and error files

## Data Flow Integration

The pipeline integrates with broader COVID surveillance infrastructure:
- Raw data from `/local/incoming/covid/runs/`
- Export to analysis systems via `/vol/sars2/jdavis/Sarah/`
- SSH key-based secure transfer using `covid_rsa` keys
- Group permission management for collaborative access