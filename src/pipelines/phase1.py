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
from observability.reporting import generate_phase1_report


def main() -> None:
    """Build baseline pipeline end-to-end.
    
    Pseudo-code:
    1. Load settings.
    2. Load or fetch raw records.
    3. Clean data.
    4. Save clean CSV/JSON.
    5. Build Chroma index.
    6. Create or load evaluation set.
    7. Evaluate.
    8. Run quality checks and freshness report.
    9. Generate markdown report.
    10. Can demo agent on some sample question.
    """
    # 1. Load settings
    settings = Settings()
    
    # 2. Load or fetch raw records
    try:
        raw_records = load_raw_records(settings.paths.raw_records_json)
        print("Loaded existing raw records")
    except FileNotFoundError:
        print("Fetching new raw records from Crossref API...")
        raw_records = fetch_source_records(settings)
    
    # 3. Clean data
    run_date = datetime.now()
    clean_df = build_clean_dataframe(raw_records, run_date)
    
    # 4. Save clean CSV/JSON
    clean_df.to_csv(settings.paths.clean_csv, index=False)
    clean_df.to_json(settings.paths.clean_json, orient='records', indent=2)
    print(f"Saved clean data to {settings.paths.clean_csv} and {settings.paths.clean_json}")
    
    # 5. Build Chroma index
    collection = build_chroma_index(clean_df, settings)
    print(f"Built Chroma index with {collection.count()} documents")
    
    # 6. Create or load evaluation set
    test_set = build_test_set(clean_df, settings.paths.eval_json)
    print(f"Created test set with {len(test_set)} questions")
    
    # 7. Evaluate
    metrics = calculate_metrics(collection, test_set)
    print("Calculated evaluation metrics")
    
    # 8. Run quality checks and freshness report
    quality_checks = run_data_quality_checks(clean_df, settings, "baseline_quality")
    freshness_report = build_freshness_report(clean_df, settings, "baseline_freshness")
    
    # 9. Generate markdown report
    generate_phase1_report(
        settings.paths.report_md,
        {
            "total_records": len(raw_records),
            "clean_records": len(clean_df),
            "source": "Crossref API"
        },
        metrics,
        quality_checks,
        freshness_report
    )
    print(f"Generated report at {settings.paths.report_md}")
    
    # 10. Demo agent on sample question (optional)
    print("Phase 1 pipeline completed successfully!")