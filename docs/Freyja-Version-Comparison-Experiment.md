# Freyja Version Comparison Experiment Design

## Executive Summary

This document outlines a comprehensive experiment to evaluate and compare different Freyja versions (1.5.3 vs 2.0.0) within the COVID sequencing pipeline to assess performance, accuracy, and compatibility implications for production deployment.

### Test Results Summary (2025-09-15)

**Initial Validation Complete**:
- ✅ Created validation script for version testing
- ✅ Established GitHub issues for tracking (#13-#16)
- ✅ Confirmed container availability for both versions
- 🔄 Performance benchmarking in progress

## Task Definition

**Objective**: Systematically evaluate Freyja v1.5.3 and v2.0.0 to determine optimal version for production COVID surveillance pipeline.

**Key Questions**:
1. Do different Freyja versions produce consistent lineage calling results?
2. What are the performance differences between versions?
3. Are there breaking changes that affect pipeline compatibility?
4. Which version provides better sensitivity for low-frequency variants?
5. How do resource requirements differ between versions?

## Current State Analysis

### Pipeline Integration Points

1. **Primary Integration**: `/local/incoming/covid/config/Makefile`
   - Line 4: `SINGULARITY := /local/incoming/covid/config/freyja_latest.sif`
   - Line 35: Freyja variants command
   - Line 37: Freyja demix command

2. **Secondary Integration**: `/nfs/seq-data/covid/sequencing-center-covid/scripts/create-pileups.sh`
   - Line 6: Container reference

3. **Legacy Scripts**: Multiple scripts reference older versions (1.3.1, 1.3.2)
   - Not actively used in main pipeline

### Available Versions

| Version | File Size | Date | Status |
|---------|-----------|------|--------|
| 1.5.3 | 534MB | Jul 14, 2025 | Current Production |
| 2.0.0 | 470MB | Sep 8, 2025 | Available for Testing |

### Command Compatibility Analysis

**Freyja 1.5.3 vs 2.0.0 Commands**:
- ✅ Both versions maintain same core command structure
- ✅ `demix` command parameters are compatible
- ✅ `variants` command syntax unchanged
- ⚠️ Version 2.0.0 adds new `ampliconstat` command
- ✅ Database update mechanisms remain consistent

## Gap Analysis

### Minimal Changes Required

1. **Makefile Modification** (1 line change):
   ```makefile
   SINGULARITY := /local/incoming/covid/config/freyja_VERSION.sif
   ```

2. **Create-pileups.sh** (1 line change):
   ```bash
   container=/local/incoming/covid/config/freyja_VERSION.sif
   ```

### No Changes Required

- Command syntax remains identical
- File paths and output formats unchanged
- Database update procedures compatible
- Bind mount requirements unchanged

### Risk Assessment

**Low Risk**:
- Command compatibility maintained
- Output format consistency expected
- Container size actually smaller in v2.0.0

**Medium Risk**:
- Potential differences in lineage calling algorithms
- Database compatibility between versions
- Performance characteristics unknown

**Mitigation**: Parallel execution design allows risk-free comparison

## Proposed Solution: Parallel Execution Framework

### Architecture

```
Input Samples
     |
     ├─→ Pipeline v1.5.3 → Results_1.5.3/
     |                        ├── variants/
     |                        ├── output/
     |                        └── summary.tsv
     |
     └─→ Pipeline v2.0.0 → Results_2.0.0/
                              ├── variants/
                              ├── output/
                              └── summary.tsv
                              
                    ↓
            Comparison Analysis
                    ↓
            Performance Metrics
```

### Implementation Approach

**Option 1: Makefile Parameterization** (RECOMMENDED)
```bash
# Modified Makefile with version parameter
FREYJA_VERSION ?= 1.5.3
SINGULARITY := /local/incoming/covid/config/freyja.$(FREYJA_VERSION).sif

# Usage:
make FREYJA_VERSION=1.5.3 strain
make FREYJA_VERSION=2.0.0 strain
```

**Option 2: Duplicate Pipeline Scripts**
```bash
process-covid-run-v1.5.3
process-covid-run-v2.0.0
```

**Option 3: Wrapper Script with Version Selection**
```bash
./run-freyja-comparison.sh <input_dir> <primer> <version>
```

## Experiment Design

### Phase 1: Compatibility Testing (1-2 days)

**Samples**: 10 representative samples from recent runs
**Metrics**:
- Command execution success/failure
- Output file generation
- Error message analysis

### Phase 2: Consistency Analysis (3-5 days)

**Samples**: 100 samples with known lineage compositions
**Metrics**:
- Lineage calling concordance
- Abundance estimation correlation
- Coverage calculation consistency

### Phase 3: Performance Benchmarking (2-3 days)

**Samples**: Full production batch (200+ samples)
**Metrics**:
- Execution time per sample
- Memory usage
- CPU utilization
- Disk I/O patterns

### Phase 4: Edge Case Evaluation (2-3 days)

**Samples**: Challenging cases
- Low coverage samples (<100x)
- Mixed infections
- Novel variants
- Degraded samples

## Success Metrics

### Primary Metrics

1. **Lineage Concordance Rate**
   - Target: >95% agreement on primary lineage calls
   - Threshold: >90% correlation in abundance estimates

2. **Performance Improvement**
   - Target: ≤10% performance degradation acceptable
   - Bonus: Any performance improvement

3. **Pipeline Stability**
   - Target: 100% successful completion rate
   - Zero breaking changes

### Secondary Metrics

4. **Resource Efficiency**
   - Memory usage differential <20%
   - Disk usage optimization

5. **Detection Sensitivity**
   - Low-frequency variant detection (>1% abundance)
   - Coverage uniformity metrics

6. **Database Compatibility**
   - Successful update procedures
   - Barcode file compatibility

### Quality Metrics

7. **Result Reproducibility**
   - Consistent results on repeated runs
   - Deterministic output ordering

8. **Error Handling**
   - Graceful failure modes
   - Informative error messages

## Implementation Steps

### Step 1: Environment Preparation
```bash
# Create experiment directory structure
mkdir -p /nfs/seq-data/covid/tmp/freyja-comparison/{v1.5.3,v2.0.0,analysis,logs}

# Verify container availability
ls -lh /local/incoming/covid/config/freyja*.sif

# Create modified Makefiles
cp /local/incoming/covid/config/Makefile /nfs/seq-data/covid/tmp/freyja-comparison/Makefile.v1.5.3
cp /local/incoming/covid/config/Makefile /nfs/seq-data/covid/tmp/freyja-comparison/Makefile.v2.0.0
```

### Step 2: Makefile Modifications
```bash
# For v1.5.3
sed -i 's|freyja_latest.sif|freyja.1.5.3-07_14_2025-00-44-2025-07-14.sif|g' Makefile.v1.5.3

# For v2.0.0
sed -i 's|freyja_latest.sif|freyja_2.0.0-09_08_2025-00-34-2025-09-08.sif|g' Makefile.v2.0.0
```

### Step 3: Wrapper Script Creation
```bash
#!/bin/bash
# run-freyja-comparison.sh

RUN_DIR=$1
PRIMER=$2
VERSION=$3

echo "Running Freyja comparison for version ${VERSION}"

# Set container based on version
if [ "$VERSION" = "1.5.3" ]; then
    export FREYJA_CONTAINER="freyja.1.5.3-07_14_2025-00-44-2025-07-14.sif"
elif [ "$VERSION" = "2.0.0" ]; then
    export FREYJA_CONTAINER="freyja_2.0.0-09_08_2025-00-34-2025-09-08.sif"
fi

# Run pipeline with specific version
./process-covid-run-modified ${RUN_DIR} ${PRIMER}
```

### Step 4: Parallel Execution
```bash
# Run both versions on same dataset
./run-freyja-comparison.sh /path/to/samples qiagen 1.5.3 &
./run-freyja-comparison.sh /path/to/samples qiagen 2.0.0 &
wait
```

### Step 5: Comparison Analysis
```python
# compare_freyja_results.py
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

# Load results from both versions
v1_results = pd.read_csv('results_v1.5.3/summary.tsv', sep='\t')
v2_results = pd.read_csv('results_v2.0.0/summary.tsv', sep='\t')

# Calculate concordance metrics
concordance = calculate_concordance(v1_results, v2_results)
performance = compare_performance(v1_logs, v2_logs)

# Generate comparison report
generate_report(concordance, performance)
```

## Pros and Cons Analysis

### Approach 1: Makefile Parameterization

**Pros**:
- ✅ Minimal code changes (1-2 lines)
- ✅ Easy version switching
- ✅ Maintains single codebase
- ✅ Simple rollback mechanism

**Cons**:
- ⚠️ Requires manual version specification
- ⚠️ Potential for user error

### Approach 2: Parallel Pipeline Infrastructure

**Pros**:
- ✅ Automated comparison
- ✅ Simultaneous execution
- ✅ Direct performance comparison
- ✅ Production-safe testing

**Cons**:
- ⚠️ Double resource consumption
- ⚠️ More complex setup

### Approach 3: Sequential Testing

**Pros**:
- ✅ Lower resource requirements
- ✅ Simpler implementation
- ✅ Clear separation of results

**Cons**:
- ⚠️ Longer total execution time
- ⚠️ Temporal variations possible

## Risk Mitigation Strategies

1. **Backup Current Production**
   ```bash
   cp -r /local/incoming/covid/runs /local/incoming/covid/runs.backup
   ```

2. **Isolated Test Environment**
   - Use dedicated test directory
   - Separate output paths
   - Independent log files

3. **Gradual Rollout**
   - Phase 1: Test samples (10)
   - Phase 2: Validation batch (100)
   - Phase 3: Production subset (500)
   - Phase 4: Full production

4. **Rollback Plan**
   ```bash
   # Quick rollback to v1.5.3
   ln -sf freyja.1.5.3-07_14_2025-00-44-2025-07-14.sif freyja_latest.sif
   ```

## Red Team Considerations

### Potential Failure Points

1. **Database Incompatibility**
   - Risk: Different barcode formats
   - Mitigation: Test database updates separately

2. **Memory Leaks**
   - Risk: v2.0.0 untested at scale
   - Mitigation: Monitor resource usage closely

3. **Algorithm Changes**
   - Risk: Unexplained result differences
   - Mitigation: Manual review of discordant calls

4. **Container Dependencies**
   - Risk: Missing libraries in new version
   - Mitigation: Comprehensive test suite

### Security Considerations

- Verify container signatures
- Check for known vulnerabilities
- Validate output sanitization
- Review file permissions

## Timeline and Milestones

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Setup & Compatibility | Infrastructure ready, initial tests |
| 1-2 | Consistency Testing | Concordance metrics report |
| 2 | Performance Analysis | Benchmark results |
| 3 | Edge Cases & Validation | Final recommendation |

## Expected Outcomes

### Best Case Scenario
- v2.0.0 shows improved performance (20-30% faster)
- 100% lineage calling concordance
- Reduced memory footprint
- Enhanced error handling

### Likely Scenario
- Minor performance differences (<10%)
- >95% concordance with explainable differences
- Similar resource usage
- Decision based on feature availability

### Worst Case Scenario
- Breaking changes requiring code modifications
- Significant result discrepancies
- Performance degradation
- Recommendation to stay on v1.5.3

## Recommendations

1. **Immediate Action**: Implement Makefile parameterization for flexible testing
2. **Short Term**: Run parallel comparison on 100-sample validation set
3. **Medium Term**: Develop automated comparison framework
4. **Long Term**: Establish version testing protocol for future updates

## Conclusion

The proposed experiment provides a low-risk, high-value approach to evaluating Freyja versions. The parallel execution framework ensures production stability while enabling comprehensive comparison. The minimal code changes required (primarily Makefile modifications) make this experiment both feasible and reversible.

**Recommended Implementation**: Start with Makefile parameterization approach, run parallel comparisons on test datasets, and gradually scale to production volumes based on initial results.

## Appendix: Implementation Scripts

### A1: Modified Makefile Template
```makefile
# Parameterized Freyja version
FREYJA_VERSION ?= 1.5.3
SINGULARITY := /local/incoming/covid/config/freyja.$(FREYJA_VERSION).sif

# Rest of Makefile remains unchanged
```

### A2: Comparison Script
```bash
#!/bin/bash
# compare_versions.sh

SAMPLE_DIR=$1
OUTPUT_BASE=/nfs/seq-data/covid/freyja-comparison

for version in 1.5.3 2.0.0; do
    echo "Processing with Freyja ${version}"
    mkdir -p ${OUTPUT_BASE}/v${version}
    
    # Run pipeline with specific version
    FREYJA_VERSION=${version} make -f Makefile.comparison strain
    
    # Copy results
    cp -r output/* ${OUTPUT_BASE}/v${version}/
done

# Run comparison analysis
python3 analyze_comparison.py ${OUTPUT_BASE}/v1.5.3 ${OUTPUT_BASE}/v2.0.0
```

### A3: Monitoring Script
```bash
#!/bin/bash
# monitor_comparison.sh

while true; do
    echo "=== Freyja Version Comparison Status ==="
    echo "v1.5.3: $(ls results_v1.5.3/output/*.out 2>/dev/null | wc -l) samples completed"
    echo "v2.0.0: $(ls results_v2.0.0/output/*.out 2>/dev/null | wc -l) samples completed"
    echo ""
    
    # Check for errors
    echo "Errors detected:"
    grep -i error logs/*.log | tail -5
    
    sleep 60
done
```