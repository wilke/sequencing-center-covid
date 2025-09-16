#!/bin/bash
# Create hard links for BAM files to save space and time
# Hard links work within the same filesystem and containers can access them

set -e

EXPERIMENT_DIR="/nfs/seq-data/covid/tmp/freyja_experiment"
SAMPLE_LIST="${EXPERIMENT_DIR}/sample_list.txt"
LOG_FILE="${EXPERIMENT_DIR}/logs/bam_linking.log"

echo "============================================"
echo "Creating hard links for BAM files"
echo "============================================"
echo "Started: $(date)" | tee -a ${LOG_FILE}

# Process each version
for VERSION in v1.5.3 v2.0.0; do
    echo ""
    echo "Processing ${VERSION}..."
    BAM_DIR="${EXPERIMENT_DIR}/${VERSION}/bam"

    COUNT=0
    SKIPPED=0
    FAILED=0

    # Read sample list and create links
    while IFS=',' read -r run sample bam_path; do
        # Skip comments and empty lines
        [[ "$run" =~ ^#.*$ ]] && continue
        [[ -z "$run" ]] && continue

        DEST="${BAM_DIR}/${sample}.sorted.bam"

        # Check if source exists
        if [ ! -f "${bam_path}" ]; then
            echo "  ✗ Source not found: ${sample}" | tee -a ${LOG_FILE}
            ((FAILED++))
            continue
        fi

        # Check if destination already exists
        if [ -f "${DEST}" ]; then
            ((SKIPPED++))
            if [ $((COUNT + SKIPPED)) -le 5 ] || [ $(((COUNT + SKIPPED) % 100)) -eq 0 ]; then
                echo "  ⊙ Already exists: ${sample}"
            fi
            continue
        fi

        # Create hard link
        if ln "${bam_path}" "${DEST}" 2>/dev/null; then
            ((COUNT++))
            if [ ${COUNT} -le 5 ] || [ $((COUNT % 100)) -eq 0 ]; then
                SIZE_MB=$(du -m "${DEST}" | cut -f1)
                echo "  ✓ Linked [${COUNT}]: ${sample} (${SIZE_MB} MB)"
            fi
        else
            # If hard link fails, try copy as fallback
            echo "  ⚠ Hard link failed, copying: ${sample}" | tee -a ${LOG_FILE}
            if cp "${bam_path}" "${DEST}"; then
                ((COUNT++))
                echo "  ✓ Copied: ${sample}"
            else
                echo "  ✗ Failed: ${sample}" | tee -a ${LOG_FILE}
                ((FAILED++))
            fi
        fi
    done < "${SAMPLE_LIST}"

    echo ""
    echo "Summary for ${VERSION}:"
    echo "  Linked/Copied: ${COUNT}"
    echo "  Skipped: ${SKIPPED}"
    echo "  Failed: ${FAILED}"
    echo "  Total: $((COUNT + SKIPPED + FAILED))"
done

# Verify the results
echo ""
echo "============================================"
echo "Verification"
echo "============================================"

for VERSION in v1.5.3 v2.0.0; do
    BAM_DIR="${EXPERIMENT_DIR}/${VERSION}/bam"
    COUNT=$(ls ${BAM_DIR}/*.sorted.bam 2>/dev/null | wc -l)
    SIZE=$(du -sh ${BAM_DIR} 2>/dev/null | cut -f1)
    echo "${VERSION}: ${COUNT} files, ${SIZE}"
done

echo ""
echo "Completed: $(date)" | tee -a ${LOG_FILE}
echo "============================================"