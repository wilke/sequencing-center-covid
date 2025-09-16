#!/bin/bash
# Run Freyja v1.5.3 and v2.0.0 sequentially using the production Makefile
# This script leverages the existing Makefile with version parameterization

set -e

EXPERIMENT_DIR=/nfs/seq-data/covid/tmp/freyja_experiment
MAKEFILE=/local/incoming/covid/config/Makefile
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Version specifications - using explicit versions (not symlinks)
V1_VERSION="1.5.3-03_07_2025-01-59-2025-03-10"
V2_VERSION="2.0.0-09_08_2025-00-34-2025-09-08"

echo "============================================================"
echo "Freyja Version Comparison Experiment"
echo "============================================================"
echo "Start time: $(date)"
echo "Experiment directory: $EXPERIMENT_DIR"
echo "Using Makefile: $MAKEFILE"
echo "Versions:"
echo "  - v1.5.3: $V1_VERSION"
echo "  - v2.0.0: $V2_VERSION"
echo ""

# Create provenance metadata
METADATA_FILE="$EXPERIMENT_DIR/metadata/run_${TIMESTAMP}.json"
cat > "$METADATA_FILE" <<EOF
{
  "experiment": "Freyja Version Comparison",
  "timestamp": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "user": "$USER",
  "working_directory": "$EXPERIMENT_DIR",
  "makefile": "$MAKEFILE",
  "versions": {
    "v1.5.3": "$V1_VERSION",
    "v2.0.0": "$V2_VERSION"
  },
  "sample_count": $(ls $EXPERIMENT_DIR/v1.5.3/bam/*.sorted.bam 2>/dev/null | wc -l),
  "command": "$0 $@"
}
EOF

echo "Provenance metadata saved to: $METADATA_FILE"
echo ""

# Function to count completed samples
count_outputs() {
    local dir=$1
    local version=$2
    local variants=$(ls $dir/variants/*.variants.tsv 2>/dev/null | wc -l)
    local outputs=$(ls $dir/output/*.out 2>/dev/null | wc -l)
    echo "[$version] Variants: $variants, Outputs: $outputs"
}

# Run Freyja v1.5.3
echo "============================================================"
echo "Running Freyja v1.5.3"
echo "============================================================"
cd $EXPERIMENT_DIR/v1.5.3

# Check initial state
echo "Initial state:"
count_outputs "." "v1.5.3"
echo ""

# Run with timing
echo "Starting processing at $(date +%H:%M:%S)..."
START_V1=$(date +%s)

make -B -i -j 20 -f $MAKEFILE \
    FREYJA_VERSION=$V1_VERSION \
    strain 2>&1 | tee $EXPERIMENT_DIR/logs/v1.5.3_${TIMESTAMP}.log

END_V1=$(date +%s)
DURATION_V1=$((END_V1 - START_V1))

echo ""
echo "Freyja v1.5.3 completed in $(($DURATION_V1 / 60)) minutes $(($DURATION_V1 % 60)) seconds"
count_outputs "." "v1.5.3"
echo ""

# Run Freyja v2.0.0
echo "============================================================"
echo "Running Freyja v2.0.0"
echo "============================================================"
cd $EXPERIMENT_DIR/v2.0.0

# Check initial state
echo "Initial state:"
count_outputs "." "v2.0.0"
echo ""

# Run with timing
echo "Starting processing at $(date +%H:%M:%S)..."
START_V2=$(date +%s)

make -B -i -j 20 -f $MAKEFILE \
    FREYJA_VERSION=$V2_VERSION \
    strain 2>&1 | tee $EXPERIMENT_DIR/logs/v2.0.0_${TIMESTAMP}.log

END_V2=$(date +%s)
DURATION_V2=$((END_V2 - START_V2))

echo ""
echo "Freyja v2.0.0 completed in $(($DURATION_V2 / 60)) minutes $(($DURATION_V2 % 60)) seconds"
count_outputs "." "v2.0.0"
echo ""

# Summary
echo "============================================================"
echo "Experiment Complete"
echo "============================================================"
echo "End time: $(date)"
echo ""
echo "Processing times:"
echo "  v1.5.3: $(($DURATION_V1 / 60))m $(($DURATION_V1 % 60))s"
echo "  v2.0.0: $(($DURATION_V2 / 60))m $(($DURATION_V2 % 60))s"
echo "  Total:  $((($DURATION_V1 + $DURATION_V2) / 60))m $((($DURATION_V1 + $DURATION_V2) % 60))s"
echo ""

# Final counts
echo "Final results:"
count_outputs "$EXPERIMENT_DIR/v1.5.3" "v1.5.3"
count_outputs "$EXPERIMENT_DIR/v2.0.0" "v2.0.0"
echo ""

# Check for differences in sample counts
V1_OUTPUTS=$(ls $EXPERIMENT_DIR/v1.5.3/output/*.out 2>/dev/null | wc -l)
V2_OUTPUTS=$(ls $EXPERIMENT_DIR/v2.0.0/output/*.out 2>/dev/null | wc -l)

if [ "$V1_OUTPUTS" -eq "$V2_OUTPUTS" ]; then
    echo "✓ Both versions processed the same number of samples ($V1_OUTPUTS)"
else
    echo "⚠ Warning: Different sample counts (v1.5.3: $V1_OUTPUTS, v2.0.0: $V2_OUTPUTS)"
fi

# Update metadata with results
RESULTS_FILE="$EXPERIMENT_DIR/metadata/results_${TIMESTAMP}.json"
cat > "$RESULTS_FILE" <<EOF
{
  "experiment": "Freyja Version Comparison Results",
  "timestamp": "$(date -Iseconds)",
  "durations": {
    "v1.5.3_seconds": $DURATION_V1,
    "v2.0.0_seconds": $DURATION_V2,
    "total_seconds": $(($DURATION_V1 + $DURATION_V2))
  },
  "outputs": {
    "v1.5.3": {
      "variants": $(ls $EXPERIMENT_DIR/v1.5.3/variants/*.variants.tsv 2>/dev/null | wc -l),
      "outputs": $(ls $EXPERIMENT_DIR/v1.5.3/output/*.out 2>/dev/null | wc -l),
      "depths": $(ls $EXPERIMENT_DIR/v1.5.3/depth/*.depth 2>/dev/null | wc -l)
    },
    "v2.0.0": {
      "variants": $(ls $EXPERIMENT_DIR/v2.0.0/variants/*.variants.tsv 2>/dev/null | wc -l),
      "outputs": $(ls $EXPERIMENT_DIR/v2.0.0/output/*.out 2>/dev/null | wc -l),
      "depths": $(ls $EXPERIMENT_DIR/v2.0.0/depth/*.depth 2>/dev/null | wc -l)
    }
  },
  "logs": {
    "v1.5.3": "logs/v1.5.3_${TIMESTAMP}.log",
    "v2.0.0": "logs/v2.0.0_${TIMESTAMP}.log"
  }
}
EOF

echo ""
echo "Results metadata saved to: $RESULTS_FILE"
echo "Logs saved to: $EXPERIMENT_DIR/logs/"
echo ""
echo "Next step: Run comparison analysis with analyze_results.py"