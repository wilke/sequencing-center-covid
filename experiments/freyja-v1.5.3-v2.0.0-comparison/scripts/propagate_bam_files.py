#!/usr/bin/env python3
"""
Copy BAM files to version-specific directories for Freyja processing.
Copies instead of symlinking due to container path requirements.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

def read_sample_list(sample_file):
    """Read the sample list file."""
    samples = []
    with open(sample_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) == 3:
                    samples.append({
                        'run': parts[0],
                        'sample': parts[1],
                        'bam_path': parts[2]
                    })
    return samples

def copy_bam_files(samples, version_dirs, dry_run=False):
    """Copy BAM files to version-specific directories."""

    copy_log = {
        'start_time': datetime.now().isoformat(),
        'versions': version_dirs,
        'total_samples': len(samples),
        'copied': [],
        'failed': [],
        'skipped': []
    }

    for version in version_dirs:
        print(f"\n{'='*60}")
        print(f"Copying BAM files to {version} directory...")
        print(f"{'='*60}")

        bam_dir = f"/nfs/seq-data/covid/tmp/freyja_experiment/{version}/bam"

        copied_count = 0
        skipped_count = 0
        failed_count = 0

        for i, sample in enumerate(samples, 1):
            source_bam = sample['bam_path']
            dest_bam = f"{bam_dir}/{sample['sample']}.sorted.bam"

            # Check if source exists
            if not os.path.exists(source_bam):
                print(f"  [{i}/{len(samples)}] ✗ Source not found: {sample['sample']}")
                copy_log['failed'].append({
                    'version': version,
                    'sample': sample['sample'],
                    'reason': 'source_not_found',
                    'source': source_bam
                })
                failed_count += 1
                continue

            # Check if destination already exists
            if os.path.exists(dest_bam):
                source_size = os.path.getsize(source_bam)
                dest_size = os.path.getsize(dest_bam)

                if source_size == dest_size:
                    if i <= 5 or i % 50 == 0:  # Show first 5 and every 50th
                        print(f"  [{i}/{len(samples)}] ⊙ Already exists: {sample['sample']}")
                    copy_log['skipped'].append({
                        'version': version,
                        'sample': sample['sample'],
                        'reason': 'already_exists'
                    })
                    skipped_count += 1
                    continue
                else:
                    print(f"  [{i}/{len(samples)}] ⚠ Size mismatch, re-copying: {sample['sample']}")

            # Copy the file
            if not dry_run:
                try:
                    shutil.copy2(source_bam, dest_bam)
                    if i <= 5 or i % 50 == 0:  # Show first 5 and every 50th
                        size_mb = os.path.getsize(dest_bam) / (1024 * 1024)
                        print(f"  [{i}/{len(samples)}] ✓ Copied: {sample['sample']} ({size_mb:.1f} MB)")

                    copy_log['copied'].append({
                        'version': version,
                        'sample': sample['sample'],
                        'source': source_bam,
                        'destination': dest_bam,
                        'size_bytes': os.path.getsize(dest_bam)
                    })
                    copied_count += 1

                except Exception as e:
                    print(f"  [{i}/{len(samples)}] ✗ Failed to copy {sample['sample']}: {str(e)}")
                    copy_log['failed'].append({
                        'version': version,
                        'sample': sample['sample'],
                        'reason': str(e),
                        'source': source_bam
                    })
                    failed_count += 1
            else:
                print(f"  [DRY RUN] Would copy: {sample['sample']}")
                copied_count += 1

        print(f"\nSummary for {version}:")
        print(f"  Copied: {copied_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total: {len(samples)}")

    copy_log['end_time'] = datetime.now().isoformat()

    # Save copy log
    log_file = "/nfs/seq-data/covid/tmp/freyja_experiment/metadata/bam_copy_log.json"
    with open(log_file, 'w') as f:
        json.dump(copy_log, f, indent=2)

    print(f"\n✓ Copy log saved to: {log_file}")

    return copy_log

def verify_copies(samples, version_dirs):
    """Verify that all BAM files were copied correctly."""
    print("\n" + "="*60)
    print("Verifying copied files...")
    print("="*60)

    verification = {}

    for version in version_dirs:
        bam_dir = f"/nfs/seq-data/covid/tmp/freyja_experiment/{version}/bam"

        expected = len(samples)
        found = len([f for f in os.listdir(bam_dir) if f.endswith('.sorted.bam')])

        verification[version] = {
            'expected': expected,
            'found': found,
            'complete': found == expected
        }

        print(f"\n{version}:")
        print(f"  Expected: {expected} files")
        print(f"  Found: {found} files")
        print(f"  Status: {'✓ Complete' if found == expected else '✗ Incomplete'}")

        if found < expected:
            # Find missing samples
            existing = set(f.replace('.sorted.bam', '') for f in os.listdir(bam_dir)
                          if f.endswith('.sorted.bam'))
            all_samples = set(s['sample'] for s in samples)
            missing = all_samples - existing

            if missing:
                print(f"  Missing {len(missing)} samples:")
                for m in list(missing)[:5]:  # Show first 5 missing
                    print(f"    - {m}")
                if len(missing) > 5:
                    print(f"    ... and {len(missing)-5} more")

    # Calculate total size
    for version in version_dirs:
        bam_dir = f"/nfs/seq-data/covid/tmp/freyja_experiment/{version}/bam"
        total_size = sum(os.path.getsize(f"{bam_dir}/{f}")
                        for f in os.listdir(bam_dir)
                        if f.endswith('.sorted.bam'))
        total_gb = total_size / (1024**3)
        print(f"\n{version} total size: {total_gb:.1f} GB")

    return verification

def main():
    """Main execution."""
    sample_file = "/nfs/seq-data/covid/tmp/freyja_experiment/sample_list.txt"
    version_dirs = ["v1.5.3", "v2.0.0"]

    print("="*60)
    print("BAM File Propagation for Freyja Comparison")
    print("="*60)

    # Read sample list
    print("\nReading sample list...")
    samples = read_sample_list(sample_file)
    print(f"Found {len(samples)} samples to process")

    # Calculate total size needed
    total_size = 0
    for sample in samples:
        if os.path.exists(sample['bam_path']):
            total_size += os.path.getsize(sample['bam_path'])

    total_gb = total_size / (1024**3)
    print(f"Total size to copy: {total_gb:.1f} GB")
    print(f"Space needed (both versions): {total_gb * 2:.1f} GB")

    # Check available space
    stat = os.statvfs('/nfs/seq-data/covid/tmp')
    available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    print(f"Available space: {available_gb:.1f} GB")

    if available_gb < total_gb * 2.2:  # Need some buffer
        print("\n⚠ WARNING: May not have enough space!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1

    # Copy files
    copy_log = copy_bam_files(samples, version_dirs, dry_run=False)

    # Verify copies
    verification = verify_copies(samples, version_dirs)

    print("\n" + "="*60)
    print("BAM file propagation complete!")
    print("="*60)

    return 0

if __name__ == "__main__":
    exit(main())