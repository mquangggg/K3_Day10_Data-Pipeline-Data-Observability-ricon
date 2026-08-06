from __future__ import annotations

from core.config import load_settings
from core.utils import now_utc, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from retrieval.index import LocalEmbeddingIndex


def main() -> None:
    """Build corruption -> evaluate -> repair -> compare flow."""
    settings = load_settings()


    # Load or fetch raw records
    try:
        raw_records = load_raw_records(settings.paths.raw_records_json)
        print("Loaded existing raw records")
    except FileNotFoundError:
        print("Fetching new raw records from Crossref API...")
        raw_records = fetch_source_records(settings)

    # 1. Baseline Clean Data
    run_date = now_utc()
    clean_df = build_clean_dataframe(raw_records, run_date)
    write_csv(clean_df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, clean_df.to_dict(orient="records"))

    # Baseline Index & Eval
    baseline_index = LocalEmbeddingIndex.build(clean_df, settings, settings.paths.embeddings_json)
    build_test_set(clean_df, settings.paths.eval_testset)
    baseline_bundle = evaluate_pipeline(
        settings,
        baseline_index,
        settings.paths.eval_testset,
        settings.paths.baseline_metrics,
        settings.paths.baseline_answers,
    )
    baseline_quality = run_data_quality_checks(clean_df, settings, "baseline_quality")
    baseline_freshness = build_freshness_report(clean_df, settings, settings.paths.freshness_report)

    # 2. Corrupted Flow
    corrupted_df = corrupt_clean_dataframe(clean_df, settings.paths.corruption_log)
    write_csv(corrupted_df, settings.paths.corrupted_clean_csv)
    write_json(settings.paths.corrupted_clean_json, corrupted_df.to_dict(orient="records"))

    corrupted_index = LocalEmbeddingIndex.build(corrupted_df, settings, settings.paths.corrupted_embeddings_json)
    corrupted_bundle = evaluate_pipeline(
        settings,
        corrupted_index,
        settings.paths.eval_testset,
        settings.paths.corrupted_metrics,
        settings.paths.corrupted_answers,
    )
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
    corrupted_freshness = build_freshness_report(corrupted_df, settings, settings.paths.quality_dir / "corrupted_freshness.json")

    # 3. Repaired Flow (re-clean from raw source)
    repaired_df = build_clean_dataframe(raw_records, run_date)
    write_csv(repaired_df, settings.paths.repaired_clean_csv)
    write_json(settings.paths.repaired_clean_json, repaired_df.to_dict(orient="records"))

    repaired_index = LocalEmbeddingIndex.build(repaired_df, settings, settings.paths.repaired_embeddings_json)
    repaired_bundle = evaluate_pipeline(
        settings,
        repaired_index,
        settings.paths.eval_testset,
        settings.paths.repaired_metrics,
        settings.paths.repaired_answers,
    )
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(repaired_df, settings, settings.paths.quality_dir / "repaired_freshness.json")

    # 4. Generate comparison report
    generate_corruption_report(
        settings.paths.comparison_report,
        baseline_bundle.summary,
        corrupted_bundle.summary,
        repaired_bundle.summary,
        baseline_quality,
        corrupted_quality,
        repaired_quality,
        baseline_freshness,
        corrupted_freshness,
        repaired_freshness,
    )
    print(f"Generated corruption comparison report at {settings.paths.comparison_report}")

    print("Corruption flow pipeline completed successfully!")


if __name__ == "__main__":
    main()