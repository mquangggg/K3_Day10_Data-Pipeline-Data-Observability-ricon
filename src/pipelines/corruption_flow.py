from __future__ import annotations

import pandas as pd
from datetime import datetime

from core.config import Settings
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from retrieval.index import build_chroma_index
from evaluation.testset import build_test_set
from evaluation.metrics import calculate_metrics
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report


def main() -> None:
    """Build corruption -> evaluate -> repair -> compare flow.
    
    Pseudo-code:
    1. Load baseline metrics and clean dataset.
    2. Create corrupted dataframe.
    3. Save corrupted artifacts.
    4. Rebuild index and evaluate.
    5. Run quality checks/freshness on corrupted data.
    6. Repair back from raw records.
    7. Evaluate repaired dataset.
    8. Generate comparison report.
    """
    # 1. Load baseline metrics and clean dataset
    settings = Settings()
    
    # Load or fetch raw records
    try:
        raw_records = load_raw_records(settings.paths.raw_records_json)
        print("Loaded existing raw records")
    except FileNotFoundError:
        print("Fetching new raw records from Crossref API...")
        raw_records = fetch_source_records(settings)
    
    # Clean data to get baseline
    run_date = datetime.now()
    clean_df = build_clean_dataframe(raw_records, run_date)
    
    # Save clean CSV/JSON for baseline
    clean_df.to_csv(settings.paths.clean_csv, index=False)
    clean_df.to_json(settings.paths.clean_json, orient='records', indent=2)
    print(f"Saved clean data to {settings.paths.clean_csv} and {settings.paths.clean_json}")
    
    # Create baseline evaluation set
    baseline_test_set = build_test_set(clean_df, settings.paths.eval_json)
    print(f"Created baseline test set with {len(baseline_test_set)} questions")
    
    # Calculate baseline metrics
    baseline_collection = build_chroma_index(clean_df, settings)
    baseline_metrics = calculate_metrics(baseline_collection, baseline_test_set)
    print("Calculated baseline evaluation metrics")
    
    # 2. Create corrupted dataframe
    corrupted_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
    print(f"Created corrupted dataframe with {len(corrupted_df)} records")
    
    # 3. Save corrupted artifacts
    corrupted_df.to_csv(settings.paths.corrupted_csv, index=False)
    corrupted_df.to_json(settings.paths.corrupted_json, orient='records', indent=2)
    print(f"Saved corrupted data to {settings.paths.corrupted_csv} and {settings.paths.corrupted_json}")
    
    # 4. Rebuild index and evaluate
    corrupted_collection = build_chroma_index(corrupted_df, settings)
    corrupted_metrics = calculate_metrics(corrupted_collection, baseline_test_set)
    print("Calculated corrupted evaluation metrics")
    
    # 5. Run quality checks/freshness on corrupted data
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(corrupted_df, settings, "corrupted_freshness")
    
    # 6. Repair back from raw records
    repaired_df = build_clean_dataframe(raw_records, run_date)
    print(f"Repaired dataframe with {len(repaired_df)} records")
    
    # 7. Evaluate repaired dataset
    repaired_collection = build_chroma_index(repaired_df, settings)
    repaired_metrics = calculate_metrics(repaired_collection, baseline_test_set)
    print("Calculated repaired evaluation metrics")
    
    # 8. Run quality checks/freshness on repaired data
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(repaired_df, settings, "repaired_freshness")
    
    # 9. Generate comparison report
    generate_corruption_report(
        settings.paths.corruption_report_md,
        baseline_metrics,
        corrupted_metrics,
        repaired_metrics,
        corrupted_quality,
        repaired_quality,
        corrupted_freshness,
        repaired_freshness
    )
    print(f"Generated corruption comparison report at {settings.paths.corruption_report_md}")
    
    print("Corruption flow pipeline completed successfully!")