#!/usr/bin/env python
"""Check quality & freshness of corrupted data and compare with baseline."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import load_settings
from src.core.utils import read_json
from src.ingestion.cleaning import build_clean_dataframe
from src.ingestion.corruption import corrupt_clean_dataframe
from src.ingestion.crossref import load_raw_records
from src.observability.quality import run_data_quality_checks, build_freshness_report
import pandas as pd

settings = load_settings()

# Load corrupted data
corrupted_df = pd.read_csv(settings.paths.corrupted_clean_csv)
print(f"Loaded corrupted data: {len(corrupted_df)} records")

# Run quality checks
corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
print(f"\nCorrupted Quality Checks:")
print(f"  - Passed: {corrupted_quality['passed']}")
print(f"  - Unique paper_id: {corrupted_quality['paper_id_is_unique']}")
print(f"  - Null paper_ids: {corrupted_quality['paper_id_null_count']}")
print(f"  - Null titles: {corrupted_quality['title_null_count']}")
print(f"  - Empty summaries: {corrupted_quality['summary_empty_count']}")
print(f"  - Stale rows (>180 days): {corrupted_quality['stale_rows_count']}")
print(f"  - Total rows: {corrupted_quality['total_rows']}")

# Run freshness checks
corrupted_freshness = build_freshness_report(
    corrupted_df, settings, settings.paths.quality_dir / "corrupted_freshness.json"
)
print(f"\nCorrupted Freshness Report:")
print(f"  - Latest published: {corrupted_freshness['latest_published']}")
print(f"  - Oldest published: {corrupted_freshness['oldest_published']}")
print(f"  - Stale rows: {corrupted_freshness['stale_rows']}")
print(f"  - Is fresh: {corrupted_freshness['is_fresh']}")

# Load baseline for comparison
baseline_quality = read_json(settings.paths.quality_dir / "baseline_quality.json")
baseline_freshness = read_json(settings.paths.freshness_report)

print("\n" + "="*50)
print("BASELINE vs CORRUPTED Comparison")
print("="*50)

print("\nData Quality:")
print(f"  Passed: Baseline={baseline_quality['passed']} → Corrupted={corrupted_quality['passed']}")
print(f"  Paper ID Unique: {baseline_quality['paper_id_is_unique']} → {corrupted_quality['paper_id_is_unique']}")
print(f"  Paper ID Nulls: {baseline_quality['paper_id_null_count']} → {corrupted_quality['paper_id_null_count']}")
print(f"  Title Nulls: {baseline_quality['title_null_count']} → {corrupted_quality['title_null_count']}")
print(f"  Empty Summaries: {baseline_quality['summary_empty_count']} → {corrupted_quality['summary_empty_count']} (Δ {corrupted_quality['summary_empty_count'] - baseline_quality['summary_empty_count']})")
print(f"  Stale Rows: {baseline_quality['stale_rows_count']} → {corrupted_quality['stale_rows_count']} (Δ {corrupted_quality['stale_rows_count'] - baseline_quality['stale_rows_count']})")
print(f"  Total Rows: {baseline_quality['total_rows']} → {corrupted_quality['total_rows']} (Δ {corrupted_quality['total_rows'] - baseline_quality['total_rows']})")

print("\nFreshness:")
print(f"  Is Fresh: {baseline_freshness['is_fresh']} → {corrupted_freshness['is_fresh']}")
print(f"  Stale Rows: {baseline_freshness['stale_rows']} → {corrupted_freshness['stale_rows']} (Δ {corrupted_freshness['stale_rows'] - baseline_freshness['stale_rows']})")

# Load corruption log
corruption_log = read_json(settings.paths.corruption_log)
print("\n" + "="*50)
print("Corruption Log")
print("="*50)
print(f"Timestamp: {corruption_log['timestamp']}")
print(f"Original rows: {corruption_log['original_row_count']}")
print(f"Corrupted rows: {corruption_log['corrupted_row_count']}")
print(f"Corruptions applied:")
for corruption_type, count in corruption_log["corruptions_applied"].items():
    print(f"  - {corruption_type}: {count}")
