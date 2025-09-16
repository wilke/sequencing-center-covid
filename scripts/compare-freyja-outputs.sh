#!/bin/bash
# compare-freyja-outputs.sh - Compare outputs from different Freyja versions
# Usage: ./compare-freyja-outputs.sh <dir1> <dir2> <output_report>

DIR1=$1
DIR2=$2
REPORT=${3:-comparison_report.txt}

if [ $# -lt 2 ]; then
    echo "Usage: $0 <freyja_output_dir1> <freyja_output_dir2> [report_file]"
    echo "Example: $0 results_v1.5.3/ results_v2.0.0/ comparison.txt"
    exit 1
fi

echo "=====================================" > $REPORT
echo "Freyja Output Comparison Report" >> $REPORT
echo "=====================================" >> $REPORT
echo "Date: $(date)" >> $REPORT
echo "Directory 1: $DIR1" >> $REPORT
echo "Directory 2: $DIR2" >> $REPORT
echo "" >> $REPORT

# Count files in each directory
COUNT1=$(find $DIR1 -name "*.tsv" -o -name "*.out" 2>/dev/null | wc -l)
COUNT2=$(find $DIR2 -name "*.tsv" -o -name "*.out" 2>/dev/null | wc -l)

echo "File Counts:" >> $REPORT
echo "  Dir1: $COUNT1 files" >> $REPORT
echo "  Dir2: $COUNT2 files" >> $REPORT
echo "" >> $REPORT

# Compare variant files if they exist
if [ -d "$DIR1/variants" ] && [ -d "$DIR2/variants" ]; then
    echo "Variant File Comparison:" >> $REPORT
    echo "------------------------" >> $REPORT

    for file1 in $DIR1/variants/*.variants.tsv; do
        basename=$(basename $file1)
        file2="$DIR2/variants/$basename"

        if [ -f "$file2" ]; then
            # Count variants in each file
            var1=$(wc -l < $file1)
            var2=$(wc -l < $file2)

            echo "  $basename: v1=$var1 lines, v2=$var2 lines" >> $REPORT

            # Check if files are identical
            if diff -q $file1 $file2 >/dev/null; then
                echo "    Status: Identical" >> $REPORT
            else
                echo "    Status: Different" >> $REPORT
                # Count differences
                DIFF_COUNT=$(diff $file1 $file2 | grep "^<\|^>" | wc -l)
                echo "    Differences: $DIFF_COUNT lines" >> $REPORT
            fi
        else
            echo "  $basename: Missing in Dir2" >> $REPORT
        fi
    done
fi

# Compare demix outputs if they exist
if [ -d "$DIR1/output" ] && [ -d "$DIR2/output" ]; then
    echo "" >> $REPORT
    echo "Demix Output Comparison:" >> $REPORT
    echo "------------------------" >> $REPORT

    for file1 in $DIR1/output/*.out; do
        basename=$(basename $file1)
        file2="$DIR2/output/$basename"

        if [ -f "$file2" ]; then
            # Extract lineages from each file
            lineages1=$(grep -o "[A-Z][A-Z]*\.[0-9]*" $file1 2>/dev/null | sort -u | wc -l)
            lineages2=$(grep -o "[A-Z][A-Z]*\.[0-9]*" $file2 2>/dev/null | sort -u | wc -l)

            echo "  $basename: v1=$lineages1 lineages, v2=$lineages2 lineages" >> $REPORT
        else
            echo "  $basename: Missing in Dir2" >> $REPORT
        fi
    done
fi

echo "" >> $REPORT
echo "=====================================" >> $REPORT
echo "Report complete: $REPORT"

# Display summary to terminal
echo "Comparison complete!"
echo "  Files in dir1: $COUNT1"
echo "  Files in dir2: $COUNT2"
echo "  Full report: $REPORT"