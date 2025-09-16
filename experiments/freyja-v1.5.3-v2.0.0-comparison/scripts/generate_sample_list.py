#!/usr/bin/env python3
"""
Generate sample list from the 12 most recent COVID runs.
Creates formatted sample list and metadata for Freyja version comparison experiment.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Define the 12 runs to use (in chronological order, newest first)
RUNS = [
    "250910_Direct_311",
    "250904_Direct_309_310",
    "250820_xhyb_test_f_v1",
    "250820_Direct_308_org",
    "250820_Direct_308",
    "250813_Direct_307",
    "250806_Direct_306",
    "250730_Direct_305_org",
    "250730_Direct_303",
    "250723_Direct_304",
    "250716_Direct_303",
    "250711_Direct_301_302"
]

def get_file_checksum(filepath, chunk_size=8192):
    """Calculate MD5 checksum of a file."""
    md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            # Only read first 10MB for checksum (faster for large BAM files)
            bytes_read = 0
            max_bytes = 10 * 1024 * 1024  # 10MB
            while bytes_read < max_bytes:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5.update(chunk)
                bytes_read += len(chunk)
        return md5.hexdigest()
    except:
        return "unavailable"

def collect_samples():
    """Collect all BAM files from specified runs."""
    base_dir = "/nfs/seq-data/covid/runs"
    samples = []

    for run_id in RUNS:
        run_path = f"{base_dir}/{run_id}"
        bam_dir = f"{run_path}/bam"

        if not os.path.exists(bam_dir):
            print(f"Warning: BAM directory not found for {run_id}")
            continue

        # Find all sorted BAM files
        bam_files = sorted([f for f in os.listdir(bam_dir) if f.endswith('.sorted.bam')])

        for bam_file in bam_files:
            bam_path = f"{bam_dir}/{bam_file}"
            sample_name = bam_file.replace('.sorted.bam', '')

            # Get file stats
            if os.path.exists(bam_path):
                stat = os.stat(bam_path)
                file_size = stat.st_size
                mod_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

                # Only include files > 1MB
                if file_size > 1_000_000:
                    samples.append({
                        'run': run_id,
                        'sample': sample_name,
                        'bam_path': bam_path,
                        'size_mb': round(file_size / 1_000_000, 2),
                        'modified': mod_time,
                        'checksum': None  # Will calculate for subset
                    })

    return samples

def write_sample_list(samples, output_file):
    """Write sample list in CSV format required by the script."""
    with open(output_file, 'w') as f:
        # Write header comments
        f.write("# Sample list for Freyja version comparison experiment\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Total samples: {len(samples)}\n")
        f.write(f"# Runs included: {', '.join(RUNS)}\n")
        f.write("# Format: run,sample,bam_path\n")

        # Write data (no header row, just data)
        for sample in samples:
            f.write(f"{sample['run']},{sample['sample']},{sample['bam_path']}\n")

def write_metadata(samples):
    """Write comprehensive metadata for provenance tracking."""
    metadata_dir = "/nfs/seq-data/covid/tmp/freyja_experiment/metadata"
    os.makedirs(metadata_dir, exist_ok=True)

    # Calculate checksums for first 5 samples (as examples)
    print("Calculating checksums for provenance (first 5 samples)...")
    for i, sample in enumerate(samples[:5]):
        sample['checksum'] = get_file_checksum(sample['bam_path'])
        print(f"  {i+1}/5: {sample['sample']} - {sample['checksum'][:8]}...")

    # Aggregate statistics
    metadata = {
        'experiment': {
            'name': 'Freyja Version Comparison',
            'description': 'Systematic comparison of Freyja v1.5.3 vs v2.0.0',
            'created': datetime.now().isoformat(),
            'created_by': os.environ.get('USER', 'unknown'),
            'base_directory': '/nfs/seq-data/covid/tmp/freyja_experiment'
        },
        'data_source': {
            'runs': RUNS,
            'run_count': len(RUNS),
            'base_path': '/nfs/seq-data/covid/runs',
            'selection_criteria': 'Most recent 12 runs with valid BAM files'
        },
        'samples': {
            'total_count': len(samples),
            'total_size_gb': round(sum(s['size_mb'] for s in samples) / 1000, 2),
            'per_run_counts': {}
        },
        'statistics': {
            'min_size_mb': min(s['size_mb'] for s in samples) if samples else 0,
            'max_size_mb': max(s['size_mb'] for s in samples) if samples else 0,
            'avg_size_mb': round(sum(s['size_mb'] for s in samples) / len(samples), 2) if samples else 0
        },
        'sample_examples': samples[:5],  # Include first 5 with checksums
        'versions': {
            'freyja_v1': '1.5.3-03_07_2025-01-59-2025-03-10',
            'freyja_v2': 'latest (2.0.0)',
            'makefile': '/local/incoming/covid/config/Makefile'
        }
    }

    # Count samples per run
    for run in RUNS:
        count = len([s for s in samples if s['run'] == run])
        metadata['samples']['per_run_counts'][run] = count

    # Write metadata
    metadata_file = f"{metadata_dir}/experiment_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Metadata written to: {metadata_file}")

    # Also create a simple run summary
    summary_file = f"{metadata_dir}/run_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Run Summary for Freyja Version Comparison\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total samples: {len(samples)}\n")
        f.write(f"Total size: {sum(s['size_mb'] for s in samples) / 1000:.1f} GB\n\n")
        f.write("Samples per run:\n")
        f.write("-" * 30 + "\n")
        for run in RUNS:
            count = metadata['samples']['per_run_counts'][run]
            f.write(f"{run}: {count} samples\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total: {len(samples)} samples\n")

    print(f"✓ Summary written to: {summary_file}")

def main():
    """Main execution."""
    output_dir = "/nfs/seq-data/covid/tmp/freyja_experiment"

    print("=" * 60)
    print("Generating Sample List for Freyja Version Comparison")
    print("=" * 60)

    # Collect samples
    print(f"\nCollecting samples from {len(RUNS)} runs...")
    samples = collect_samples()

    if not samples:
        print("ERROR: No valid samples found!")
        return 1

    # Write sample list
    sample_list_file = f"{output_dir}/sample_list.txt"
    write_sample_list(samples, sample_list_file)
    print(f"\n✓ Sample list written to: {sample_list_file}")

    # Write metadata
    print("\nGenerating metadata for provenance tracking...")
    write_metadata(samples)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total runs: {len(RUNS)}")
    print(f"Total samples: {len(samples)}")
    print(f"Total data size: {sum(s['size_mb'] for s in samples) / 1000:.1f} GB")
    print(f"Average sample size: {sum(s['size_mb'] for s in samples) / len(samples):.1f} MB")

    print("\nSamples per run:")
    for run in RUNS:
        count = len([s for s in samples if s['run'] == run])
        print(f"  {run}: {count}")

    print("\n✓ Sample list generation complete!")
    print(f"  Output: {sample_list_file}")
    print(f"  Metadata: {output_dir}/metadata/")

    return 0

if __name__ == "__main__":
    exit(main())