#!/usr/bin/env python3
"""
Comprehensive analysis of Freyja v1.5.3 vs v2.0.0 comparison experiment.
Includes full provenance tracking and evidence-based reporting.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import hashlib
import subprocess
from collections import defaultdict

class FreyjaComparisonAnalyzer:
    def __init__(self, base_dir="/nfs/seq-data/covid/tmp/freyja_experiment"):
        self.base_dir = Path(base_dir)
        self.v1_dir = self.base_dir / "v1.5.3"
        self.v2_dir = self.base_dir / "v2.0.0"
        self.analysis_dir = self.base_dir / "analysis"
        self.analysis_dir.mkdir(exist_ok=True)

        # Initialize provenance tracking
        self.provenance = {
            "analysis_timestamp": datetime.now().isoformat(),
            "script": __file__,
            "base_directory": str(self.base_dir),
            "versions_compared": {
                "v1": "1.5.3-03_07_2025-01-59-2025-03-10",
                "v2": "2.0.0-09_08_2025-00-34-2025-09-08"
            },
            "inputs": {},
            "outputs": {},
            "metrics": {}
        }

    def find_output_files(self):
        """Find all output files for both versions."""
        v1_outputs = sorted(self.v1_dir.glob("output/*.out"))
        v2_outputs = sorted(self.v2_dir.glob("output/*.out"))

        v1_samples = {f.stem for f in v1_outputs}
        v2_samples = {f.stem for f in v2_outputs}

        # Track in provenance
        self.provenance["inputs"]["v1_output_count"] = len(v1_outputs)
        self.provenance["inputs"]["v2_output_count"] = len(v2_outputs)
        self.provenance["inputs"]["v1_samples"] = list(v1_samples)[:5]  # First 5 as examples
        self.provenance["inputs"]["v2_samples"] = list(v2_samples)[:5]

        return v1_outputs, v2_outputs, v1_samples, v2_samples

    def identify_missing_samples(self, v1_samples, v2_samples):
        """Identify samples present in one version but not the other."""
        only_v1 = v1_samples - v2_samples
        only_v2 = v2_samples - v1_samples
        common = v1_samples & v2_samples

        missing_report = {
            "only_in_v1": list(only_v1),
            "only_in_v2": list(only_v2),
            "common_samples": len(common),
            "v1_total": len(v1_samples),
            "v2_total": len(v2_samples)
        }

        self.provenance["metrics"]["sample_overlap"] = missing_report

        return missing_report, common

    def parse_freyja_output(self, filepath):
        """Parse a Freyja output file."""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 4:
                    # Parse the standard Freyja output format
                    # Line 2 (index 2): lineages\t<list of lineages>
                    # Line 3 (index 3): abundances\t<list of abundances>
                    lineage_line = lines[2].strip().split('\t')
                    abundance_line = lines[3].strip().split('\t')

                    # Skip the first element which is the label
                    if lineage_line[0] == 'lineages':
                        lineages = lineage_line[1].split() if len(lineage_line) > 1 else []
                    else:
                        lineages = []

                    if abundance_line[0] == 'abundances':
                        abundance_str = abundance_line[1] if len(abundance_line) > 1 else ""
                        abundances = [float(x) for x in abundance_str.split() if x]
                    else:
                        abundances = []

                    # Create lineage dictionary
                    lineage_dict = {}
                    if len(lineages) == len(abundances):
                        for lin, abund in zip(lineages, abundances):
                            lineage_dict[lin] = abund

                    return {
                        "lineages": lineages,
                        "abundances": abundances,
                        "lineage_dict": lineage_dict,
                        "total_lineages": len(lineages),
                        "dominant_lineage": lineages[0] if lineages else None,
                        "dominant_abundance": abundances[0] if abundances else 0
                    }
        except Exception as e:
            return {"error": str(e)}
        return {"error": "Could not parse file"}

    def compare_sample_outputs(self, sample_name, common_samples):
        """Compare outputs for a specific sample between versions."""
        if sample_name not in common_samples:
            return None

        v1_file = self.v1_dir / "output" / f"{sample_name}.out"
        v2_file = self.v2_dir / "output" / f"{sample_name}.out"

        v1_data = self.parse_freyja_output(v1_file)
        v2_data = self.parse_freyja_output(v2_file)

        comparison = {
            "sample": sample_name,
            "v1_lineages": v1_data.get("total_lineages", 0),
            "v2_lineages": v2_data.get("total_lineages", 0),
            "v1_dominant": v1_data.get("dominant_lineage"),
            "v2_dominant": v2_data.get("dominant_lineage"),
            "dominant_match": v1_data.get("dominant_lineage") == v2_data.get("dominant_lineage"),
            "v1_dominant_abundance": v1_data.get("dominant_abundance", 0),
            "v2_dominant_abundance": v2_data.get("dominant_abundance", 0)
        }

        # Calculate Jaccard similarity for lineages
        if "lineages" in v1_data and "lineages" in v2_data:
            v1_set = set(v1_data["lineages"])
            v2_set = set(v2_data["lineages"])
            if v1_set or v2_set:
                jaccard = len(v1_set & v2_set) / len(v1_set | v2_set)
                comparison["jaccard_similarity"] = jaccard

        return comparison

    def analyze_all_samples(self, common_samples):
        """Analyze all common samples between versions."""
        comparisons = []

        for i, sample in enumerate(sorted(common_samples)):
            if i % 100 == 0:
                print(f"  Processing sample {i+1}/{len(common_samples)}")

            comp = self.compare_sample_outputs(sample, common_samples)
            if comp:
                comparisons.append(comp)

        return pd.DataFrame(comparisons)

    def calculate_concordance_metrics(self, df):
        """Calculate concordance metrics between versions."""
        metrics = {
            "total_samples_compared": len(df),
            "dominant_lineage_concordance": df["dominant_match"].mean() * 100,
            "mean_jaccard_similarity": df["jaccard_similarity"].mean() if "jaccard_similarity" in df else 0,
            "samples_with_perfect_match": (df["jaccard_similarity"] == 1.0).sum() if "jaccard_similarity" in df else 0,
            "samples_with_different_dominant": (~df["dominant_match"]).sum(),
            "mean_lineages_v1": df["v1_lineages"].mean(),
            "mean_lineages_v2": df["v2_lineages"].mean()
        }

        self.provenance["metrics"]["concordance"] = metrics
        return metrics

    def identify_discordant_samples(self, df, threshold=0.8):
        """Identify samples with significant discordance."""
        # Create conditions for discordance
        has_jaccard = "jaccard_similarity" in df.columns

        if has_jaccard:
            # Mark as discordant if dominant doesn't match OR Jaccard is below threshold
            discordant_mask = (df["dominant_match"] == False) | (df["jaccard_similarity"] < threshold)
            discordant = df[discordant_mask].copy()

            # Add reason for discordance
            discordant["discordance_reason"] = discordant.apply(
                lambda x: "Different dominant" if not x["dominant_match"] else f"Low similarity (<{threshold})",
                axis=1
            )
        else:
            discordant = df[df["dominant_match"] == False].copy()
            discordant["discordance_reason"] = "Different dominant"

        discordant_list = discordant["sample"].tolist()
        self.provenance["metrics"]["discordant_samples"] = {
            "count": len(discordant_list),
            "threshold": threshold,
            "different_dominant": (discordant["dominant_match"] == False).sum() if "dominant_match" in discordant.columns else 0,
            "low_similarity": (discordant["jaccard_similarity"] < threshold).sum() if has_jaccard else 0,
            "samples": discordant_list  # Store all samples
        }

        print(f"   Discordance breakdown:")
        print(f"     - Different dominant lineage: {(discordant['dominant_match'] == False).sum() if 'dominant_match' in discordant.columns else 0}")
        if has_jaccard:
            print(f"     - Low Jaccard similarity (<{threshold}): {(discordant['jaccard_similarity'] < threshold).sum()}")

        return discordant

    def save_results(self, df, missing_report, concordance_metrics, discordant_df):
        """Save all analysis results with provenance."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save comparison DataFrame
        csv_path = self.analysis_dir / f"comparison_results_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        self.provenance["outputs"]["comparison_csv"] = str(csv_path)

        # Save discordant samples
        if not discordant_df.empty:
            discordant_path = self.analysis_dir / f"discordant_samples_{timestamp}.csv"
            discordant_df.to_csv(discordant_path, index=False)
            self.provenance["outputs"]["discordant_csv"] = str(discordant_path)

        # Save comprehensive JSON report
        report = {
            "experiment": "Freyja v1.5.3 vs v2.0.0 Comparison",
            "analysis_date": datetime.now().isoformat(),
            "missing_samples": missing_report,
            "concordance_metrics": concordance_metrics,
            "summary": {
                "total_samples_analyzed": len(df),
                "concordance_rate": f"{concordance_metrics['dominant_lineage_concordance']:.2f}%",
                "discordant_samples": len(discordant_df),
                "mean_similarity": f"{concordance_metrics['mean_jaccard_similarity']:.3f}"
            }
        }

        report_path = self.analysis_dir / f"analysis_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        self.provenance["outputs"]["report_json"] = str(report_path)

        # Save provenance
        prov_path = self.analysis_dir / f"provenance_{timestamp}.json"
        with open(prov_path, 'w') as f:
            json.dump(self.provenance, f, indent=2, default=str)

        return csv_path, report_path, prov_path

    def generate_summary_report(self, missing_report, concordance_metrics, discordant_df):
        """Generate a markdown summary report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Freyja Version Comparison Analysis Report

**Generated**: {timestamp}
**Analyst**: Automated Analysis Pipeline
**Location**: {self.base_dir}

## Executive Summary

Comprehensive comparison of Freyja v1.5.3 vs v2.0.0 using 592 production samples.

## Sample Coverage

- **v1.5.3 samples**: {missing_report['v1_total']}
- **v2.0.0 samples**: {missing_report['v2_total']}
- **Common samples**: {missing_report['common_samples']}
- **Missing in v2.0.0**: {', '.join(missing_report['only_in_v1']) if missing_report['only_in_v1'] else 'None'}

## Concordance Metrics

### Overall Agreement
- **Dominant lineage concordance**: {concordance_metrics['dominant_lineage_concordance']:.2f}%
- **Mean Jaccard similarity**: {concordance_metrics['mean_jaccard_similarity']:.3f}
- **Samples with perfect match**: {concordance_metrics['samples_with_perfect_match']}
- **Samples with different dominant lineage**: {concordance_metrics['samples_with_different_dominant']}

### Lineage Detection
- **Mean lineages detected (v1.5.3)**: {concordance_metrics['mean_lineages_v1']:.1f}
- **Mean lineages detected (v2.0.0)**: {concordance_metrics['mean_lineages_v2']:.1f}

## Discordant Samples

Found {len(discordant_df)} samples with significant discordance (Jaccard < 0.8 or different dominant lineage).

### Discordant Samples Details

**Total discordant samples: {len(discordant_df)}**

Note: High Jaccard similarity (close to 1.0) with different dominant lineages suggests the lineages have very similar abundances,
and minor numerical differences cause different dominant calls.

"""
        if not discordant_df.empty:
            # Show all discordant samples if less than 50, otherwise show first 25
            num_to_show = min(len(discordant_df), 50)
            samples_to_show = discordant_df.head(num_to_show)

            report += "\n| # | Sample | v1.5.3 Dominant | v2.0.0 Dominant | v1.5.3 Abund | v2.0.0 Abund | Similarity |\n"
            report += "|---|--------|-----------------|-----------------|--------------|--------------|------------|\n"
            for idx, (_, row) in enumerate(samples_to_show.iterrows(), 1):
                similarity = row.get('jaccard_similarity', 'N/A')
                if similarity != 'N/A':
                    similarity = f"{similarity:.4f}"
                v1_abund = f"{row.get('v1_dominant_abundance', 0):.4f}"
                v2_abund = f"{row.get('v2_dominant_abundance', 0):.4f}"
                report += f"| {idx} | {row['sample']} | {row['v1_dominant']} | {row['v2_dominant']} | {v1_abund} | {v2_abund} | {similarity} |\n"

            if len(discordant_df) > num_to_show:
                report += f"\n*Showing {num_to_show} of {len(discordant_df)} discordant samples. See CSV file for complete list.*\n"

        report += f"""

## Evidence and Provenance

### Input Files
- v1.5.3 outputs: `{self.v1_dir}/output/*.out`
- v2.0.0 outputs: `{self.v2_dir}/output/*.out`

### Analysis Script
- Script: `{__file__}`
- Execution time: {timestamp}

### Output Files
- Full comparison data: `analysis/comparison_results_*.csv`
- Discordant samples: `analysis/discordant_samples_*.csv`
- Detailed report: `analysis/analysis_report_*.json`
- Provenance record: `analysis/provenance_*.json`

## Recommendations

"""
        if concordance_metrics['dominant_lineage_concordance'] > 95:
            report += "✅ **High concordance (>95%)**: Both versions produce consistent results for dominant lineage calling.\n"
        elif concordance_metrics['dominant_lineage_concordance'] > 90:
            report += "⚠️ **Good concordance (90-95%)**: Minor differences observed, review discordant samples.\n"
        else:
            report += "❌ **Significant differences (<90%)**: Detailed investigation required before version change.\n"

        report += "\n## Next Steps\n\n"
        report += "1. Review discordant samples for patterns\n"
        report += "2. Compare computational performance metrics\n"
        report += "3. Validate results with known reference samples\n"
        report += "4. Document any version-specific features or improvements\n"

        return report

    def run_full_analysis(self):
        """Run the complete comparison analysis."""
        print("="*60)
        print("Freyja Version Comparison Analysis")
        print("="*60)

        # Find output files
        print("\n1. Finding output files...")
        v1_outputs, v2_outputs, v1_samples, v2_samples = self.find_output_files()
        print(f"   Found {len(v1_outputs)} v1.5.3 outputs")
        print(f"   Found {len(v2_outputs)} v2.0.0 outputs")

        # Identify missing samples
        print("\n2. Identifying sample overlap...")
        missing_report, common_samples = self.identify_missing_samples(v1_samples, v2_samples)
        print(f"   Common samples: {len(common_samples)}")
        if missing_report['only_in_v1']:
            print(f"   Missing in v2.0.0: {missing_report['only_in_v1']}")

        # Analyze common samples
        print("\n3. Analyzing common samples...")
        df = self.analyze_all_samples(common_samples)
        print(f"   Analyzed {len(df)} samples")

        # Calculate concordance
        print("\n4. Calculating concordance metrics...")
        concordance_metrics = self.calculate_concordance_metrics(df)
        print(f"   Dominant lineage concordance: {concordance_metrics['dominant_lineage_concordance']:.2f}%")

        # Identify discordant samples
        print("\n5. Identifying discordant samples...")
        discordant_df = self.identify_discordant_samples(df)
        print(f"   Found {len(discordant_df)} discordant samples")

        # Save results
        print("\n6. Saving results...")
        csv_path, report_path, prov_path = self.save_results(
            df, missing_report, concordance_metrics, discordant_df
        )
        print(f"   Results saved to: {csv_path}")
        print(f"   Report saved to: {report_path}")
        print(f"   Provenance saved to: {prov_path}")

        # Generate summary report
        print("\n7. Generating summary report...")
        summary_report = self.generate_summary_report(
            missing_report, concordance_metrics, discordant_df
        )

        summary_path = self.analysis_dir / f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(summary_path, 'w') as f:
            f.write(summary_report)
        print(f"   Summary saved to: {summary_path}")

        print("\n" + "="*60)
        print("Analysis Complete!")
        print("="*60)

        return summary_report

if __name__ == "__main__":
    analyzer = FreyjaComparisonAnalyzer()
    summary = analyzer.run_full_analysis()
    print("\n" + summary)