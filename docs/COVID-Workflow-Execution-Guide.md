# COVID Sequencing Center Workflow Execution Guide

This document provides a comprehensive guide to the COVID sequencing analysis workflow and execution order for SARS-CoV-2 surveillance and lineage analysis.

## Overview

The COVID sequencing workflow consists of two main execution scripts that handle the complete pipeline from raw sequencing data to variant calling and lineage analysis:

1. **`process-covid-run`** - Main entry point that sets up infrastructure and orchestrates the complete analysis pipeline
2. **`process-run.sh`** - Core processing script that handles variant calling, summary generation, and output formatting

## Main Execution Scripts

### 1. Primary Workflow Entry Point

**Script**: `/nfs/seq-data/covid/sequencing-center-covid/scripts/process-covid-run`

**Purpose**: Complete SARS-CoV-2 analysis pipeline from raw FASTQ files to lineage classification and reporting.

**Usage**:
```bash
./process-covid-run <input_directory> <primer_type>

# Examples
./process-covid-run /path/to/sequencing/run qiagen
./process-covid-run /path/to/sequencing/run swift
./process-covid-run /path/to/sequencing/run midnight
```

**Required Parameters**:
- `input_directory`: Directory containing FASTQ files and sample mapping file
- `primer_type`: One of `qiagen`, `swift`, or `midnight`

**Input Requirements**:
- FASTQ files (`.fastq.gz`) in the input directory
- Sample mapping file (`.sample-mapping.tsv`) for metadata

### 2. Core Processing Engine

**Script**: `/nfs/seq-data/covid/sequencing-center-covid/scripts/process-run.sh`

**Purpose**: Handles post-assembly processing including variant calling, depth analysis, and summary generation.

**Usage**: 
```bash
./process-run.sh <covid_run_directory>
```

**Note**: This script is automatically called by `process-covid-run` and typically should not be run independently.

## Complete Workflow Execution Order

### Phase 1: Infrastructure Setup (`process-covid-run`)

1. **Parameter Validation**
   - Validates primer type (qiagen/swift/midnight)
   - Sets up directory paths and configuration

2. **Directory Structure Creation**
   ```
   /local/incoming/covid/runs/${run_id}/
   ├── variants/          # Variant calling outputs
   ├── output/            # Freyja demix results  
   ├── depth/             # Coverage depth files
   ├── bam/               # Processed BAM files
   ├── samples/           # Raw FASTQ files
   ├── staging/           # Intermediate BAM files
   ├── Assemblies/        # Assembly outputs
   ├── Consensus/         # Consensus sequences
   └── tmp/               # Temporary files
   ```

3. **File Transfer**
   - Copy FASTQ files to `samples/` directory
   - Copy sample mapping file to run directory
   - Set up symbolic links and reference files

### Phase 2: Sequence Assembly (`assembly.sh`)

**Script**: `assembly.sh`

**Dependencies**: 
- Singularity container: `bvbrc-build-latest.sif`
- Primer-specific assembly scripts: `local-assembly.sh`
- Parallel assembly engine: `parallel-assemblies-v2.pl`

**Process**:
1. **Read Preparation**
   - Parse FASTQ files and create read pair mappings
   - Generate input file for parallel assembly

2. **Containerized Assembly**
   - Execute primer-specific assembly using Singularity container
   - Parallel processing with configurable threads (default: 10)
   - Generate assembly statistics and logs

3. **Consensus Generation** 
   - Extract consensus sequences from assemblies
   - Create multi-FASTA output for lineage analysis

### Phase 3: Variant Processing (`process-run.sh`)

**Dependencies**:
- Makefile-based workflow execution
- Freyja Singularity container: `freyja_latest.sif`
- Reference genome: `MN908947.3.trimmed.fa`
- Supporting Python scripts: `staging2bam.py`, `out2spreadsheet.py`, `update-sample-mapping.py`

**Process**:

1. **BAM File Organization**
   ```bash
   # Move sorted BAM files from assemblies to staging
   find ${run_dir}/Assemblies -name *.sorted.bam -exec mv {} ${run_dir}/staging/ \;
   ```

2. **Sample Processing Setup**
   ```bash
   # Set timestamps and organize BAM files by date
   python3 staging2bam.py -m ${mapping_file} -s ./staging/ -d ./bam/
   ```

3. **Variant Calling and Lineage Analysis**
   ```bash
   # Parallel variant calling using Makefile
   make update        # Update Freyja databases
   make -B -i -j 20 strain   # Primary variant calling (20 parallel jobs)
   make -i -j 10 strain      # Secondary processing (10 parallel jobs)
   ```

   **Per-sample Processing** (via Makefile):
   - **Variant Detection**: `freyja variants` - calls variants against reference
   - **Depth Analysis**: Generates coverage depth profiles
   - **Lineage Demixing**: `freyja demix` - determines lineage composition
   - **Output Generation**: Creates structured results files

4. **Coverage and Summary Analysis**
   ```bash
   # Generate coverage summaries
   for i in depth/* ; do sh depth2cov.sh $i ; done > coverage.all.txt
   
   # Create sample summaries  
   for i in output/* ; do python3 out2spreadsheet.py $i ; done > summary.tsv
   ```

5. **Data Integration and Reporting**
   ```bash
   # Sort and join coverage and summary data
   sort summary.tsv > summary.sorted.tsv
   sort coverage.all.txt > coverage.sorted.txt
   join -t $'\t' -a 1 -a 2 -e 'n/a' summary.sorted.tsv coverage.c1.c2 > summary.all.tsv
   
   # Update sample mapping with results
   python3 update-sample-mapping.py -c coverage.all.txt -m ${mapping_file} -s output
   ```

### Phase 4: Pileup Analysis and Final Processing

**Script**: `create-pileups.sh`

**Dependencies**:
- Freyja container: `freyja_latest.sif`
- Pileup parser: `parse_pileup-v12.pl`

**Process**:
1. **Pileup Extraction**
   ```bash
   # Extract and decompress pileup files
   find ./Assemblies/ -name "*.pileup*" -exec cp {} tmp/ \;
   gunzip -v tmp/*.gz
   ```

2. **Pileup Processing**
   ```bash
   # Process each pileup file through parser
   for pileup in tmp/*.pileup; do
     singularity run -B $script $container perl $script < $pileup > pileups/${pileup}.tab
   done
   ```

## Key Supporting Scripts

### Assembly Pipeline

- **`local-assembly.sh`**: Primer-specific assembly execution
- **`parallel-assemblies-v2.pl`**: Parallel assembly orchestration
- **Supported Primers**: qiagen, swift, midnight

### Data Processing Scripts

- **`staging2bam.py`**: Organizes BAM files with proper timestamps
- **`depth2cov.sh`**: Converts depth files to coverage summaries  
- **`out2spreadsheet.py`**: Formats Freyja outputs into tabular format
- **`update-sample-mapping.py`**: Updates sample metadata with analysis results

### Monitoring and Validation

- **`create-pileups.sh`**: Generates detailed variant pileups
- Various location and testing group processing scripts for batch operations

## Configuration and Dependencies

### Container Requirements

- **Assembly Container**: `bvbrc-build-latest.sif` (~23GB)
  - Contains assembly tools and dependencies
  - Location: `/local/incoming/covid/config/bvbrc-build-latest.sif`

- **Analysis Container**: `freyja_latest.sif` (~575MB)  
  - Current version: Freyja 1.5.3
  - Contains Freyja tools for variant calling and lineage analysis
  - Location: `/local/incoming/covid/config/freyja_latest.sif`

### Reference Data

- **Reference Genome**: `MN908947.3.trimmed.fa`
- **Barcode Database**: Updated regularly (usher_barcodes.*.feather)
- **Lineage Metadata**: `curated_lineages.json`, `lineages.yml`
- **Configuration**: `pathogen_config.yml`

### Resource Requirements

- **CPU**: 10-20 parallel processes supported
- **Memory**: Container-dependent, typically 4-8GB per process
- **Storage**: ~1-2GB per sample for intermediate files
- **Runtime**: 30-60 minutes per sample depending on coverage

## Output Structure

### Primary Outputs

```
/local/incoming/covid/runs/${run_id}/
├── summary.all.tsv              # Integrated sample summary with coverage
├── ${mapping_file}.updated.tsv  # Updated sample mapping with results
├── coverage.all.txt             # Coverage statistics for all samples
├── variants/                    # Per-sample variant calls
│   └── *.variants.tsv          # Freyja variant files
├── output/                      # Per-sample lineage analysis
│   └── *.out                   # Freyja demix results
├── depth/                       # Per-sample coverage depth
│   └── *.depth                 # Coverage depth profiles
├── pileups/                     # Detailed variant information
│   └── *.tab                   # Processed pileup data
└── bam/                         # Final processed alignments
    └── *.sorted.bam            # Sample BAM files with timestamps
```

### Log Files

- Assembly logs: `${prefix}.assembly.log`, `${prefix}.assembly.error`
- Processing logs: Standard output during execution
- Error logs: `summary.error.log`

## Usage Examples

### Complete Workflow Execution

```bash
# Standard Qiagen-based analysis
cd /nfs/seq-data/covid/sequencing-center-covid
./scripts/process-covid-run /path/to/run/240901_Swift_batch_15 qiagen

# Swift primer analysis  
./scripts/process-covid-run /path/to/run/240901_Swift_batch_15 swift

# Midnight primer analysis
./scripts/process-covid-run /path/to/run/240901_Midnight_batch_03 midnight
```

### Manual Processing Steps

```bash
# If you need to rerun just the processing step:
cd /local/incoming/covid/runs/240901_Swift_batch_15
/nfs/seq-data/covid/sequencing-center-covid/scripts/process-run.sh $(pwd)

# Reprocess just variant calling:
make -B -i -j 20 strain

# Regenerate summaries:
for i in output/*; do python3 /local/incoming/covid/scripts/out2spreadsheet.py $i; done > summary.tsv
```

## Troubleshooting

### Common Issues

1. **Missing Primer Parameter**
   ```
   Error: "No primer, please specify either qiagen or swift"
   Solution: Always specify primer type as second argument
   ```

2. **Container Access Issues**
   ```
   Error: Singularity container not found
   Solution: Verify container paths in /local/incoming/covid/config/
   ```

3. **Insufficient Resources**
   ```
   Error: Make jobs failing
   Solution: Reduce parallel job count (-j parameter) in Makefile calls
   ```

4. **Missing Input Files**
   ```
   Error: No FASTQ files found
   Solution: Verify *.fastq.gz files exist in input directory
   ```

### Monitoring Progress

- Check assembly logs: `tail -f ${run_id}/*.assembly.log`
- Monitor variant calling: `watch 'ls variants/*.variants.tsv | wc -l'`
- Check processing status: `ps aux | grep freyja`

### Database Updates

Freyja databases are updated automatically during processing:
```bash
make update  # Updates lineage barcodes and metadata
```

Manual database updates (if needed):
```bash
singularity run /local/incoming/covid/config/freyja_latest.sif freyja update
```

## Expected Results

### Successful Run Indicators

- All samples have corresponding files in `variants/`, `output/`, and `depth/` directories
- `summary.all.tsv` contains results for all input samples
- No error messages in assembly or processing logs
- BAM files properly timestamped in `bam/` directory

### Quality Metrics

- **Coverage**: Typical >100X for good quality samples
- **Assembly Quality**: Check consensus lengths and N-content
- **Lineage Assignment**: Freyja confidence scores >0.8 for reliable calls

### Typical Runtime

- **Small batch (10 samples)**: 1-2 hours
- **Medium batch (50 samples)**: 3-5 hours  
- **Large batch (200 samples)**: 8-12 hours

## Integration and Downstream Analysis

### Data Export and Sharing

Results are automatically formatted for:
- GISAID submission preparation
- Public health reporting
- Research database integration

### Quality Control

The workflow includes built-in quality control:
- Assembly quality assessment
- Coverage depth validation
- Lineage assignment confidence scoring

### Batch Processing

For processing multiple runs:
```bash
# Process multiple directories
for run_dir in /path/to/runs/*/; do
  ./scripts/process-covid-run "$run_dir" qiagen
done
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Database Updates**: Weekly Freyja barcode updates
2. **Container Updates**: Monthly container refreshes
3. **Log Cleanup**: Regular cleanup of temporary files and logs

### Getting Help

- Check log files for specific error messages
- Verify container and reference file integrity
- Review input file formatting and completeness
- Monitor resource usage during processing

For technical issues:
- Review the CLAUDE.md file for project-specific guidance
- Check container versions and compatibility
- Validate input file formats and sample mapping files