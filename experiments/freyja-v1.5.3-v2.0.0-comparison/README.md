# Freyja Version Comparison Experiment (v1.5.3 vs v2.0.0)

## Executive Summary

This experiment compared Freyja versions 1.5.3 and 2.0.0 on 592 production COVID-19 samples to evaluate concordance and identify version differences. The experiment achieved **92.72% concordance** between versions, with 43 discordant samples primarily due to tie-breaking in dominant lineage calls.

### Key Findings
- **Success Rate**: v1.5.3 (100%), v2.0.0 (99.83%)
- **Concordance**: 92.72% (549/592 samples)
- **Discordance Pattern**: Identical abundances but different dominant lineage selection
- **Failed Sample**: 20250805.112247_S24 (low coverage: 4.28x)

## Experiment Design

### Objective
Systematically evaluate Freyja v1.5.3 and v2.0.0 to determine compatibility and differences for production deployment.

### Approach
We used **Option 3: Sequential Testing with Existing Makefile** from the design document:
- Leverage production Makefile with version parameterization
- Process samples sequentially per version
- Maintain complete provenance tracking
- Direct comparison of outputs

## Dataset

### Sample Selection
- **Total Samples**: 592 valid BAM files
- **Source**: 12 most recent COVID sequencing runs
- **Date Range**: August 2025 - September 2025
- **Sample List**: `data/sample_list.txt`
- **Metadata**: `data/sample_metadata.json` (includes checksums)

### Runs Included
```
250910_Direct_311
250904_Direct_309_310
250903_Direct_308
250830_Direct_306
250829_Direct_304_305
250828_Direct_302_303
250827_Direct_301
250826_Direct_300
250823_Direct_299
250822_Direct_297_298
250820_Direct_295_296
250816_Direct_293_294
```

## Implementation

### Directory Structure
```
/nfs/seq-data/covid/tmp/freyja_experiment/
├── v1.5.3/
│   ├── bam/          # 592 copied BAM files
│   ├── variants/     # Variant calling outputs
│   └── output/       # Freyja demix results
├── v2.0.0/
│   ├── bam/          # 592 copied BAM files
│   ├── variants/     # Variant calling outputs
│   └── output/       # Freyja demix results
├── scripts/          # All processing scripts
├── analysis/         # Comparison results
└── logs/            # Execution logs
```

### Execution Commands

```bash
# 1. Generate sample list
cd /nfs/seq-data/covid/tmp/freyja_experiment
python3 scripts/generate_sample_list.py

# 2. Propagate BAM files (copy, not symlink due to container requirements)
python3 scripts/propagate_bam_files.py

# 3. Run Freyja comparison
./scripts/run_freyja_comparison.sh

# 4. Analyze results
python3 scripts/analyze_comparison.py
```

### Key Configuration

**Makefile Parameters**:
```makefile
# Version 1.5.3
SINGULARITY := /local/incoming/covid/config/freyja.1.5.3-03_07_2025-01-59-2025-03-10.sif

# Version 2.0.0
SINGULARITY := /local/incoming/covid/config/freyja.2.0.0-09_08_2025-00-34-2025-09-08.sif
```

**Make Command Options**:
- `-B`: Force rebuild all targets (ensures fresh processing)
- `-i`: Ignore errors (continue on failures)
- `-j 20`: Parallel execution with 20 jobs

## Results

### Processing Statistics
| Version | Processed | Success | Failed | Success Rate |
|---------|-----------|---------|--------|--------------|
| v1.5.3  | 592       | 592     | 0      | 100%        |
| v2.0.0  | 592       | 591     | 1      | 99.83%      |

### Concordance Analysis
- **Concordant Samples**: 549 (92.72%)
- **Discordant Samples**: 43 (7.28%)
- **Missing in v2.0.0**: 1 (0.17%)

### Discordance Pattern
All 43 discordant samples showed:
- Identical lineage abundances between versions
- Different dominant lineage selection
- Jaccard similarity = 1.0 (complete overlap)
- Suggests tie-breaking algorithm difference

### Failed Sample Analysis
**Sample**: 20250805.112247_S24
- **Coverage**: 4.281888x (below typical threshold)
- **Status**: No lineages detected in either version
- **Failure**: v2.0.0 processing incomplete

## Provenance Tracking

### Input Provenance
- Sample metadata with MD5 checksums: `data/sample_metadata.json`
- Source run documentation: `data/DATASET.md`
- Original Makefile configuration: `config/Makefile.original`

### Processing Provenance
- Execution scripts with timestamps: `scripts/`
- Complete execution logs: `logs/`
- Version-specific containers tracked

### Output Provenance
- All results preserved in `results/`
- Comparison metrics and analysis
- Discordant sample details

## Reproducibility

To reproduce this experiment:

```bash
# 1. Clone or navigate to experiment directory
cd /nfs/seq-data/covid/sequencing-center-covid/experiments/freyja-v1.5.3-v2.0.0-comparison

# 2. Review sample list and metadata
cat data/sample_list.txt
cat data/DATASET.md

# 3. Execute comparison script
scripts/run_freyja_comparison.sh

# 4. Run analysis
python3 scripts/analyze_comparison.py
```

## Conclusions

1. **High Concordance**: 92.72% agreement indicates strong consistency between versions
2. **Tie-Breaking Difference**: Discordances due to different handling of equal-abundance lineages
3. **Production Ready**: v2.0.0 shows comparable performance with minor algorithmic differences
4. **Low Coverage Handling**: Both versions struggle with very low coverage samples (<5x)

## Recommendations

1. **Version Selection**: Either version suitable for production based on concordance
2. **Tie-Breaking**: Document and understand tie-breaking behavior for interpretation
3. **Coverage Threshold**: Implement minimum coverage filter (suggest >10x)
4. **Transition Strategy**: Can safely upgrade to v2.0.0 with minimal impact

## Files in This Repository

- `scripts/` - All experiment scripts
  - `generate_sample_list.py` - Sample selection and metadata
  - `propagate_bam_files.py` - BAM file distribution
  - `run_freyja_comparison.sh` - Main execution script
  - `analyze_comparison.py` - Concordance analysis
- `data/` - Input data and metadata
  - `sample_list.txt` - 592 sample paths
  - `sample_metadata.json` - Checksums and provenance
  - `DATASET.md` - Dataset documentation
- `results/` - Analysis outputs
  - `comparison_analysis.json` - Detailed metrics
  - `discordant_samples.tsv` - Sample-level differences
- `config/` - Configuration files
  - `Makefile.original` - Production Makefile
- `logs/` - Execution logs (if preserved)

## Contact

This experiment was conducted as part of the COVID-19 genomic surveillance pipeline evaluation.
Date: September 16, 2025