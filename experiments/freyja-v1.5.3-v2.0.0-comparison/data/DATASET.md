# Freyja Testing Dataset

## Overview
Comprehensive test dataset of 592 SARS-CoV-2 samples for Freyja version comparison and pipeline validation.

## Dataset Characteristics

### Composition
- **Total samples**: 592 valid BAM files
- **Source runs**: 12 most recent production runs
- **Date range**: 2025-06-11 to 2025-09-10
- **Total size**: 29.2 GB per version (58.4 GB total when copied)
- **Average sample size**: 52.1 MB

### Runs Included
1. 250910_Direct_311 (52 samples)
2. 250904_Direct_309_310 (108 samples)
3. 250820_xhyb_test_f_v1 (1 sample)
4. 250820_Direct_308_org (51 samples)
5. 250820_Direct_308 (51 samples)
6. 250813_Direct_307 (55 samples)
7. 250806_Direct_306 (57 samples)
8. 250730_Direct_305_org (54 samples)
9. 250730_Direct_303 (54 samples)
10. 250723_Direct_304 (56 samples)
11. 250716_Direct_303 (55 samples)
12. 250711_Direct_301_302 (103 samples)

## File Structure

```
/nfs/seq-data/covid/tmp/freyja_experiment/
├── sample_list.txt              # Master list of all samples
├── DATASET.md                    # This documentation
├── metadata/
│   ├── experiment_metadata.json # Detailed metadata with checksums
│   ├── run_summary.txt          # Run statistics
│   └── bam_copy_log.json       # Copy operation logs
├── v1.5.3/
│   └── bam/                     # 592 BAM files for v1.5.3 testing
└── v2.0.0/
    └── bam/                     # 592 BAM files for v2.0.0 testing
```

## Sample List Format

The `sample_list.txt` file contains comma-separated values:
```
run_id,sample_name,bam_path
```

Example:
```
250910_Direct_311,20250831.113400_S44,/nfs/seq-data/covid/runs/250910_Direct_311/bam/20250831.113400_S44.sorted.bam
```

## Selection Criteria

Samples were selected based on:
1. **Recency**: Most recent 12 production runs
2. **Validity**: BAM files >1MB in size
3. **Accessibility**: Files must be readable
4. **Diversity**: Various coverage levels and sample types
5. **Completeness**: Only properly formatted BAM files

## Usage Instructions

### Regenerating the Dataset
```bash
cd /nfs/seq-data/covid/tmp/freyja_experiment
python3 scripts/generate_sample_list.py
python3 scripts/propagate_bam_files.py
```

### Running Tests
```bash
# Run Freyja comparison
./scripts/run_freyja_comparison.sh

# Monitor progress
./scripts/monitor_progress.sh
```

### Accessing Metadata
```python
import json

# Load experiment metadata
with open('metadata/experiment_metadata.json') as f:
    metadata = json.load(f)

# Access sample details
print(f"Total samples: {metadata['samples']['total_count']}")
print(f"Total size: {metadata['samples']['total_size_gb']} GB")
```

## Provenance

### Checksums
First 5 samples include MD5 checksums in `metadata/experiment_metadata.json` for verification.

### Creation Details
- **Created by**: wilke
- **Creation date**: 2025-09-15
- **Generation script**: `scripts/generate_sample_list.py`
- **Source data**: `/nfs/seq-data/covid/runs/`

## Validation

Dataset has been validated for:
- [x] File integrity (all BAM files readable)
- [x] Size requirements (>1MB per file)
- [x] Format consistency (proper BAM format)
- [x] Metadata completeness
- [x] Reproducibility (scripts included)

## Current Usage

This dataset is actively being used for:
- Freyja v1.5.3 vs v2.0.0 comparison (September 2025)
- Pipeline performance benchmarking
- Lineage calling consistency validation

## Future Extensions

Recommended additions for comprehensive testing:
- Low-coverage samples (<10x)
- Samples with known difficult variants
- Synthetic/spike-in controls
- Samples from different sequencing platforms

## Contact

For questions about this dataset, refer to the experiment documentation in `/nfs/seq-data/covid/tmp/freyja_experiment/reports/`