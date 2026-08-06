from __future__ import annotations

from core.config import load_settings
from core.utils import now_utc, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    """Build baseline pipeline end-to-end."""
    # 1. Load settings
    settings = load_settings()


    # 2. Load or fetch raw records
    try:
        raw_records = load_raw_records(settings.paths.raw_records_json)
        print(f"Loaded {len(raw_records)} existing raw records from {settings.paths.raw_records_json}")
    except FileNotFoundError:
        print("Fetching new raw records from Crossref API...")
        raw_records = fetch_source_records(settings)

    # 3. Clean data
    run_date = now_utc()
    clean_df = build_clean_dataframe(raw_records, run_date)

    # 4. Save clean CSV/JSON
    write_csv(clean_df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, clean_df.to_dict(orient="records"))
    print(f"Saved clean data: {len(clean_df)} rows to {settings.paths.clean_csv} and {settings.paths.clean_json}")

    # 5. Build Chroma index
    index = LocalEmbeddingIndex.build(clean_df, settings)
    print(f"Built Chroma index '{index.collection_name}' with {len(index.documents)} documents")

    # 6. Create or load evaluation set
    if not settings.paths.eval_testset.exists() or settings.refresh_test_set:
        test_set = build_test_set(clean_df, settings.paths.eval_testset)
        print(f"Created test set with {len(test_set)} questions at {settings.paths.eval_testset}")
    else:
        print(f"Using existing test set at {settings.paths.eval_testset}")

    # 7. Evaluate
    bundle = evaluate_pipeline(
        settings,
        index,
        settings.paths.eval_testset,
        settings.paths.baseline_metrics,
        settings.paths.baseline_answers,
    )
    print(f"Calculated baseline metrics: hit_rate={bundle.summary.get('retrieval_hit_rate', 0):.4f}, token_f1={bundle.summary.get('mean_token_f1', 0):.4f}")

    # 8. Run quality checks and freshness report
    quality_checks = run_data_quality_checks(clean_df, settings, "baseline_quality")
    freshness_report = build_freshness_report(clean_df, settings, settings.paths.freshness_report)

    # 9. Generate markdown report
    generate_phase1_report(
        settings.paths.baseline_report,
        {
            "source_api": settings.source_api,
            "source_query": settings.source_query,
            "raw_count": len(raw_records),
            "clean_count": len(clean_df),
        },
        bundle.summary,
        quality_checks,
        freshness_report,
    )
    print(f"Generated baseline report at {settings.paths.baseline_report}")
    print("Phase 1 pipeline completed successfully!")


if __name__ == "__main__":
    main()