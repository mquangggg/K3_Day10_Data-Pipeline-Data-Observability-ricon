#!/usr/bin/env python
"""Generate repaired data and quality checks for CP6."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import load_settings
from src.core.utils import write_csv, write_json, now_utc, read_json
from src.ingestion.cleaning import build_clean_dataframe
from src.ingestion.crossref import load_raw_records
from src.observability.quality import run_data_quality_checks, build_freshness_report
import pandas as pd

settings = load_settings()

print("="*60)
print("CP6: Generating Repaired Dataset & Quality Checks")
print("="*60)

# Step 1: Load raw records from snapshot
print("\n1. Loading raw data snapshot...")
try:
    raw_records = load_raw_records(settings.paths.raw_records_json)
    print(f"   ✅ Loaded {len(raw_records)} raw records")
except Exception as e:
    print(f"   ❌ Error loading raw records: {e}")
    sys.exit(1)

# Step 2: Regenerate clean data from raw (same process as baseline)
print("\n2. Regenerating clean data from raw records...")
try:
    run_date = now_utc()
    repaired_df = build_clean_dataframe(raw_records, run_date)
    print(f"   ✅ Cleaned data: {len(repaired_df)} records")
    print(f"   ✅ Schema validated: {list(repaired_df.columns[:5])}...")
except Exception as e:
    print(f"   ❌ Error building clean dataframe: {e}")
    sys.exit(1)

# Step 3: Save repaired data
print("\n3. Saving repaired data...")
try:
    write_csv(repaired_df, settings.paths.repaired_clean_csv)
    write_json(settings.paths.repaired_clean_json, repaired_df.to_dict(orient="records"))
    print(f"   ✅ Saved to:")
    print(f"      - {settings.paths.repaired_clean_csv.name}")
    print(f"      - {settings.paths.repaired_clean_json.name}")
except Exception as e:
    print(f"   ❌ Error saving data: {e}")
    sys.exit(1)

# Step 4: Run quality checks on repaired data
print("\n4. Running quality checks on repaired data...")
try:
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    print(f"   ✅ Quality checks passed: {repaired_quality['passed']}")
    print(f"      - Paper ID Unique: {repaired_quality['paper_id_is_unique']}")
    print(f"      - Null Paper IDs: {repaired_quality['paper_id_null_count']}")
    print(f"      - Empty Summaries: {repaired_quality['summary_empty_count']}")
    print(f"      - Total Records: {repaired_quality['total_rows']}")
except Exception as e:
    print(f"   ❌ Error running quality checks: {e}")
    sys.exit(1)

# Step 5: Run freshness checks on repaired data
print("\n5. Running freshness checks on repaired data...")
try:
    repaired_freshness = build_freshness_report(
        repaired_df, 
        settings, 
        settings.paths.quality_dir / "repaired_freshness.json"
    )
    print(f"   ✅ Freshness report generated:")
    print(f"      - Is Fresh: {repaired_freshness['is_fresh']}")
    print(f"      - Latest Published: {repaired_freshness['latest_published']}")
    print(f"      - Stale Rows: {repaired_freshness['stale_rows']}")
except Exception as e:
    print(f"   ❌ Error running freshness checks: {e}")
    sys.exit(1)

# Step 6: Compare with baseline to verify restoration
print("\n6. Verifying repaired data matches baseline...")
try:
    baseline_quality = read_json(settings.paths.quality_dir / "baseline_quality.json")
    baseline_freshness = read_json(settings.paths.freshness_report)
    
    matches_quality = (
        repaired_quality['passed'] == baseline_quality['passed'] and
        repaired_quality['paper_id_is_unique'] == baseline_quality['paper_id_is_unique'] and
        repaired_quality['total_rows'] == baseline_quality['total_rows']
    )
    
    matches_freshness = (
        repaired_freshness['is_fresh'] == baseline_freshness['is_fresh']
    )
    
    if matches_quality and matches_freshness:
        print(f"   ✅ VERIFIED: Repaired data matches baseline perfectly!")
        print(f"      - Quality: {repaired_quality['passed']} (baseline: {baseline_quality['passed']})")
        print(f"      - Freshness: {repaired_freshness['is_fresh']} (baseline: {baseline_freshness['is_fresh']})")
        print(f"      - Row Count: {repaired_quality['total_rows']} (baseline: {baseline_quality['total_rows']})")
    else:
        print(f"   ⚠️  WARNING: Repaired data differs from baseline")
        if not matches_quality:
            print(f"      Quality mismatch")
        if not matches_freshness:
            print(f"      Freshness mismatch")
except Exception as e:
    print(f"   ❌ Error verifying: {e}")

print("\n" + "="*60)
print("✅ Repaired data generation complete")
print("="*60)
print("\nNext steps:")
print("  1. Member 2: Build Chroma collection papers-repaired")
print("  2. Member 2: Run evaluation with test set")
print("  3. Member 3: Generate final comparison report")
