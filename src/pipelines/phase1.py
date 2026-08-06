from __future__ import annotations

import pandas as pd
from datetime import datetime

from core.config import Settings, load_settings
from ingestion.crossref import fetch_source_records, load_raw_records
from ingestion.cleaning import build_clean_dataframe
from retrieval.index import LocalEmbeddingIndex
from evaluation.testset import build_test_set
from evaluation.metrics import evaluate_pipeline
from observability.quality import (
    run_data_quality_checks,
    build_freshness_report,
    audit_embedding_manifest,
    save_baseline_signals,
)
from observability.reporting import generate_phase1_report


def main() -> None:
    """Build baseline pipeline end-to-end.
    
    Flow:
    1. Load settings
    2. Load/fetch raw records
    3. Clean data
    4. Save clean CSV/JSON
    5. Build Chroma index + audit embedding manifest
    6. Create/load evaluation set
    7. Evaluate
    8. Run quality checks & freshness
    9. Audit embedding manifest
    10. Save baseline signals (for corruption comparison)
    11. Generate Phase 1 report
    """
    # 1. Load settings
    settings = load_settings()
    print("✅ Settings loaded")
    
    # 2. Load or fetch raw records
    try:
        raw_records = load_raw_records(settings.paths.raw_records_json)
        print(f"✅ Loaded existing raw records: {len(raw_records)}")
    except FileNotFoundError:
        print("🔄 Fetching new raw records from Crossref API...")
        raw_records = fetch_source_records(settings)
        print(f"✅ Fetched: {len(raw_records)} records")
    
    # 3. Clean data
    run_date = datetime.now()
    clean_df = build_clean_dataframe(raw_records, run_date)
    print(f"✅ Cleaned: {len(clean_df)} records")
    
    # 4. Save clean CSV/JSON
    clean_df.to_csv(settings.paths.clean_csv, index=False)
    clean_df.to_json(settings.paths.clean_json, orient='records', indent=2)
    print(f"✅ Saved clean data to CSV & JSON")
    
    # 5. Build Chroma index
    collection = LocalEmbeddingIndex.build(clean_df, settings)
    print(f"✅ Built Chroma index with {collection.collection.count()} documents")
    
    # 6. Create or load evaluation set
    test_set = build_test_set(clean_df, settings.paths.eval_testset)
    print(f"✅ Created test set with {len(test_set)} questions")
    
    # 7. Evaluate
    bundle = evaluate_pipeline(settings, collection, settings.paths.eval_testset, settings.paths.baseline_metrics, settings.paths.baseline_answers)
    metrics = bundle.summary
    print("✅ Calculated evaluation metrics")
    
    # 8. Run quality checks and freshness report
    quality_checks = run_data_quality_checks(clean_df, settings, "baseline_quality")
    print(f"✅ Quality checks saved: data/quality/baseline_quality.json")
    
    freshness_report = build_freshness_report(clean_df, settings, settings.paths.freshness_report)
    print(f"✅ Freshness report saved: {settings.paths.freshness_report}")
    
    # 9. Audit embedding manifest (CP2 - for audit trail)
    embedding_audit = audit_embedding_manifest(settings, settings.paths.embeddings_json)
    print(f"✅ Embedding audit complete: {embedding_audit.get('audit_result', 'UNKNOWN')}")
    
    # 10. Save baseline signals for corruption comparison (CP2)
    baseline_signals_result = save_baseline_signals(
        quality_checks,
        freshness_report,
        embedding_audit,
        settings
    )
    print(f"✅ {baseline_signals_result['message']}")
    
    # 11. Generate markdown report
    generate_phase1_report(
        settings.paths.baseline_report,
        {
            "total_records": len(raw_records),
            "clean_records": len(clean_df),
            "source": "Crossref API"
        },
        metrics,
        quality_checks,
        freshness_report,
        embedding_audit
    )
    print(f"✅ Phase 1 markdown report generated: {settings.paths.baseline_report}")
    
    print("\n" + "="*60)
    print("✅ PHASE 1 PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Baseline Artifacts:")
    print(f"  - Clean data: {settings.paths.clean_csv}")
    print(f"  - Quality report: data/quality/baseline_quality.json")
    print(f"  - Freshness report: {settings.paths.freshness_report}")
    print(f"  - Baseline signals: data/quality/baseline_signals.json")
    print(f"  - Evaluation metrics: {settings.paths.baseline_metrics}")
    print(f"  - Markdown report: {settings.paths.baseline_report}")
    print(f"\n🎯 Ready for Phase 2: Corruption flow")


if __name__ == "__main__":
    main()
