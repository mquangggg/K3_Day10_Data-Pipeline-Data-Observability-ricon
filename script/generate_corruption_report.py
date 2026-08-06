#!/usr/bin/env python
"""Generate corruption impact report for CP5."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import load_settings
from src.core.utils import read_json
from src.observability.reporting import generate_corruption_report
import pandas as pd

settings = load_settings()

# Load all metrics and quality reports
baseline_metrics = read_json(settings.paths.baseline_metrics)
baseline_quality = read_json(settings.paths.quality_dir / "baseline_quality.json")
baseline_freshness = read_json(settings.paths.freshness_report)

corrupted_quality = read_json(settings.paths.quality_dir / "corrupted_quality.json")
corrupted_freshness = read_json(settings.paths.quality_dir / "corrupted_freshness.json")
corruption_log = read_json(settings.paths.corruption_log)

# Use placeholder corrupted metrics for now (will be populated by member 2)
# If file exists, use it; otherwise use a default structure
try:
    corrupted_metrics = read_json(settings.paths.corrupted_metrics)
except FileNotFoundError:
    # Placeholder metrics (member 2 will update these after evaluation)
    corrupted_metrics = {
        "retrieval_hit_rate": 0.0,
        "mean_token_f1": 0.0,
        "judge_accuracy": 0.0,
        "samples": 0
    }
    print(f"⚠️  Corrupted metrics not found, using placeholder: {corrupted_metrics}")

# For repaired, use placeholder or baseline (since repaired should match baseline)
try:
    repaired_metrics = read_json(settings.paths.repaired_metrics)
except FileNotFoundError:
    repaired_metrics = baseline_metrics.copy()
    print(f"⚠️  Repaired metrics not found, using baseline as reference")

# Repaired quality should match baseline (same cleaning process from same raw data)
try:
    repaired_quality = read_json(settings.paths.quality_dir / "repaired_quality.json")
except FileNotFoundError:
    repaired_quality = baseline_quality.copy()
    print(f"⚠️  Repaired quality not found, using baseline as reference")

# Repaired freshness should match baseline
try:
    repaired_freshness = read_json(settings.paths.quality_dir / "repaired_freshness.json")
except FileNotFoundError:
    repaired_freshness = baseline_freshness.copy()
    print(f"⚠️  Repaired freshness not found, using baseline as reference")

print("\n" + "="*60)
print("Generating Corruption Impact Report")
print("="*60)

# Generate the report
generate_corruption_report(
    settings.paths.comparison_report,
    baseline_metrics,
    corrupted_metrics,
    repaired_metrics,
    baseline_quality,
    corrupted_quality,
    repaired_quality,
    baseline_freshness,
    corrupted_freshness,
    repaired_freshness,
)

print(f"✅ Report generated: {settings.paths.comparison_report}")

# Also print summary to console
print("\n" + "="*60)
print("Corruption Impact Summary")
print("="*60)
print(f"\nData Quality Impact:")
print(f"  Baseline: {baseline_quality['total_rows']} rows, Passed={baseline_quality['passed']}")
print(f"  Corrupted: {corrupted_quality['total_rows']} rows, Passed={corrupted_quality['passed']}")
print(f"  Quality Gate Failure: {not corrupted_quality['passed']}")
print(f"  Issues Added:")
print(f"    - Empty Summaries: {corrupted_quality['summary_empty_count']} (was {baseline_quality['summary_empty_count']})")

print(f"\nCorruption Details:")
for corruption_type, count in corruption_log["corruptions_applied"].items():
    print(f"  - {corruption_type.replace('_', ' ').title()}: {count}")

print(f"\nFreshness Impact:")
print(f"  Baseline: Stale={baseline_freshness['stale_rows']}, Fresh={baseline_freshness['is_fresh']}")
print(f"  Corrupted: Stale={corrupted_freshness['stale_rows']}, Fresh={corrupted_freshness['is_fresh']}")

print("\n💡 Evaluation metrics will be updated by Member 2 after evaluation completes")
print("📊 Report location: data/reports/corruption_report.md")
