from typing import Any
from pathlib import Path
from core.utils import write_text


def generate_phase1_report(
    report_path: Any,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Viet markdown report cho baseline phase."""
    md = f"""# Baseline Data Pipeline & Evaluation Report

## 1. Source Summary
- **Source API:** {source_summary.get('source_api', 'Crossref REST API')}
- **Query:** `{source_summary.get('source_query', '')}`
- **Raw Records Count:** {source_summary.get('raw_count', 0)}
- **Clean Records Count:** {source_summary.get('clean_count', 0)}

## 2. Data Quality & Freshness
- **Passed Quality Gates:** {quality.get('passed', False)}
- **Paper ID Unique:** {quality.get('paper_id_is_unique', False)}
- **Title Null Count:** {quality.get('title_null_count', 0)}
- **Latest Published:** {freshness.get('latest_published', 'N/A')}
- **Oldest Published:** {freshness.get('oldest_published', 'N/A')}
- **Is Fresh:** {freshness.get('is_fresh', False)}

## 3. Evaluation Metrics
- **Retrieval Hit Rate:** {metrics.get('retrieval_hit_rate', 0.0):.4f}
- **Mean Token F1 Score:** {metrics.get('mean_token_f1', 0.0):.4f}
- **Judge Accuracy:** {metrics.get('judge_accuracy', 0.0):.4f}
- **Total Evaluated Questions:** {metrics.get('samples', 0)}
"""
    write_text(Path(report_path), md)


def generate_corruption_report(
    report_path: Any,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """Viet markdown report so sanh baseline/corrupted/repaired."""
    b_hit = baseline_metrics.get("retrieval_hit_rate", 0.0)
    c_hit = corrupted_metrics.get("retrieval_hit_rate", 0.0)
    r_hit = repaired_metrics.get("retrieval_hit_rate", 0.0)

    b_f1 = baseline_metrics.get("mean_token_f1", 0.0)
    c_f1 = corrupted_metrics.get("mean_token_f1", 0.0)
    r_f1 = repaired_metrics.get("mean_token_f1", 0.0)

    md = r"""# Corruption & Recovery Impact Report

## 1. Metric Comparison Overview

| State | Retrieval Hit Rate | Mean Token F1 | Quality Passed | Freshness Status |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline** | {b_hit:.4f} | {b_f1:.4f} | True | Fresh |
| **Corrupted** | {c_hit:.4f} | {c_f1:.4f} | {corrupted_quality.get('passed', False)} | {corrupted_freshness.get('is_fresh', False)} |
| **Repaired** | {r_hit:.4f} | {r_f1:.4f} | {repaired_quality.get('passed', False)} | {repaired_freshness.get('is_fresh', False)} |

## 2. Impact Analysis
- **Impact of Corruption (Delta Hit Rate):** {delta_corrupt:+.4f}
- **Recovery Effect (Delta Hit Rate Repaired vs Corrupted):** {delta_repair:+.4f}

## 3. Conclusion
- Repairing clean dataset directly from reliable raw source restores data observability signals and evaluation metrics back to baseline level.
""".format(
        b_hit=b_hit,
        b_f1=b_f1,
        c_hit=c_hit,
        c_f1=c_f1,
        r_hit=r_hit,
        r_f1=r_f1,
        corrupted_quality=corrupted_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_quality=repaired_quality,
        repaired_freshness=repaired_freshness,
        delta_corrupt=c_hit - b_hit,
        delta_repair=r_hit - c_hit,
    )
    write_text(Path(report_path), md)


