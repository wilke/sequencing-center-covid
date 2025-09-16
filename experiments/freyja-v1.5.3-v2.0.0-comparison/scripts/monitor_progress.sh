#!/bin/bash
# Monitor progress of Freyja comparison experiment
# Run this in a separate terminal to track progress in real-time

EXPERIMENT_DIR=/nfs/seq-data/covid/tmp/freyja_experiment

clear
while true; do
    echo "============================================================"
    echo "Freyja Comparison Progress Monitor"
    echo "Time: $(date +"%Y-%m-%d %H:%M:%S")"
    echo "============================================================"
    echo ""

    # Count total BAM files
    TOTAL_BAMS=$(ls $EXPERIMENT_DIR/v1.5.3/bam/*.sorted.bam 2>/dev/null | wc -l)

    # Count outputs for v1.5.3
    V1_VARIANTS=$(ls $EXPERIMENT_DIR/v1.5.3/variants/*.variants.tsv 2>/dev/null | wc -l)
    V1_OUTPUTS=$(ls $EXPERIMENT_DIR/v1.5.3/output/*.out 2>/dev/null | wc -l)
    V1_DEPTHS=$(ls $EXPERIMENT_DIR/v1.5.3/depth/*.depth 2>/dev/null | wc -l)

    # Count outputs for v2.0.0
    V2_VARIANTS=$(ls $EXPERIMENT_DIR/v2.0.0/variants/*.variants.tsv 2>/dev/null | wc -l)
    V2_OUTPUTS=$(ls $EXPERIMENT_DIR/v2.0.0/output/*.out 2>/dev/null | wc -l)
    V2_DEPTHS=$(ls $EXPERIMENT_DIR/v2.0.0/depth/*.depth 2>/dev/null | wc -l)

    # Calculate percentages
    if [ $TOTAL_BAMS -gt 0 ]; then
        V1_PCT=$((V1_OUTPUTS * 100 / TOTAL_BAMS))
        V2_PCT=$((V2_OUTPUTS * 100 / TOTAL_BAMS))
    else
        V1_PCT=0
        V2_PCT=0
    fi

    # Display progress
    echo "Total samples to process: $TOTAL_BAMS"
    echo ""
    echo "Freyja v1.5.3:"
    echo "  Variants: $V1_VARIANTS/$TOTAL_BAMS"
    echo "  Outputs:  $V1_OUTPUTS/$TOTAL_BAMS ($V1_PCT%)"
    echo "  Depths:   $V1_DEPTHS/$TOTAL_BAMS"

    # Progress bar for v1.5.3
    echo -n "  Progress: ["
    for i in $(seq 1 50); do
        if [ $i -le $((V1_PCT / 2)) ]; then
            echo -n "="
        else
            echo -n " "
        fi
    done
    echo "] $V1_PCT%"

    echo ""
    echo "Freyja v2.0.0:"
    echo "  Variants: $V2_VARIANTS/$TOTAL_BAMS"
    echo "  Outputs:  $V2_OUTPUTS/$TOTAL_BAMS ($V2_PCT%)"
    echo "  Depths:   $V2_DEPTHS/$TOTAL_BAMS"

    # Progress bar for v2.0.0
    echo -n "  Progress: ["
    for i in $(seq 1 50); do
        if [ $i -le $((V2_PCT / 2)) ]; then
            echo -n "="
        else
            echo -n " "
        fi
    done
    echo "] $V2_PCT%"

    echo ""

    # Check if both are complete
    if [ "$V1_OUTPUTS" -eq "$TOTAL_BAMS" ] && [ "$V2_OUTPUTS" -eq "$TOTAL_BAMS" ]; then
        echo "✓ EXPERIMENT COMPLETE!"
        echo "Both versions have processed all $TOTAL_BAMS samples."
        break
    fi

    # Show recent activity
    echo "Recent activity (last 5 files):"
    echo "v1.5.3:"
    ls -lt $EXPERIMENT_DIR/v1.5.3/output/*.out 2>/dev/null | head -5 | awk '{print "  " $9}'
    echo "v2.0.0:"
    ls -lt $EXPERIMENT_DIR/v2.0.0/output/*.out 2>/dev/null | head -5 | awk '{print "  " $9}'

    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo "============================================================"

    sleep 30  # Update every 30 seconds
    clear
done