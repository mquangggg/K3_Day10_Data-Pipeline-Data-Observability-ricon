from typing import Any
from pathlib import Path
from core.utils import write_text


def _format_value(val: Any, precision: int = 2) -> str:
    """Format value cho markdown table."""
    if val is None or val == "N/A":
        return "N/A"
    if isinstance(val, bool):
        return "✅ Yes" if val else "❌ No"
    if isinstance(val, float):
        return f"{val:.{precision}f}"
    if isinstance(val, int):
        return f"{val:,}"
    return str(val)


def _calculate_delta(baseline: Any, current: Any) -> str:
    """Calculate và format delta giữa baseline và current value."""
    try:
        baseline_val = float(baseline) if baseline not in [None, "N/A"] else 0
        current_val = float(current) if current not in [None, "N/A"] else 0
        
        if baseline_val == 0:
            return "N/A"
        
        delta = current_val - baseline_val
        pct = (delta / baseline_val) * 100 if baseline_val != 0 else 0
        
        icon = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
        return f"{icon} {delta:+.2f} ({pct:+.1f}%)"
    except (ValueError, TypeError):
        return "N/A"


def generate_phase1_report(
    report_path: Any,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
    embedding_audit: dict[str, Any] | None = None,
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
    baseline_quality: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    baseline_freshness: dict[str, Any],
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

    # Extract quality and freshness values
    baseline_passed = baseline_quality.get("passed", True)
    corrupted_passed = corrupted_quality.get("passed", False)
    repaired_passed = repaired_quality.get("passed", True)
    
    baseline_fresh = baseline_freshness.get("is_fresh", True)
    corrupted_fresh = corrupted_freshness.get("is_fresh", False)
    repaired_fresh = repaired_freshness.get("is_fresh", True)

    # Convert to checkmark format
    b_quality = "✅ Pass" if baseline_passed else "❌ Fail"
    c_quality = "✅ Pass" if corrupted_passed else "❌ Fail"
    r_quality = "✅ Pass" if repaired_passed else "❌ Fail"
    
    b_fresh_str = "✅ Fresh" if baseline_fresh else "⚠️ Stale"
    c_fresh_str = "✅ Fresh" if corrupted_fresh else "⚠️ Stale"
    r_fresh_str = "✅ Fresh" if repaired_fresh else "⚠️ Stale"

    md = f"""# Corruption & Recovery Impact Report

## 1. Metric Comparison Overview

| State | Retrieval Hit Rate | Mean Token F1 | Quality Passed | Freshness Status |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline** | {b_hit:.4f} | {b_f1:.4f} | {b_quality} | {b_fresh_str} |
| **Corrupted** | {c_hit:.4f} | {c_f1:.4f} | {c_quality} | {c_fresh_str} |
| **Repaired** | {r_hit:.4f} | {r_f1:.4f} | {r_quality} | {r_fresh_str} |

## 2. Impact Analysis
- **Impact of Corruption (Delta Hit Rate):** {c_hit - b_hit:+.4f}
- **Recovery Effect (Delta Hit Rate Repaired vs Corrupted):** {r_hit - c_hit:+.4f}

## 3. Data Quality Details

### Baseline Quality
- Total Records: {baseline_quality.get("total_rows", 0)}
- Paper ID Unique: {baseline_quality.get("paper_id_is_unique", False)}
- Empty Summaries: {baseline_quality.get("summary_empty_count", 0)}
- Stale Rows (>180 days): {baseline_quality.get("stale_rows_count", 0)}

### Corrupted Quality
- Total Records: {corrupted_quality.get("total_rows", 0)}
- Paper ID Unique: {corrupted_quality.get("paper_id_is_unique", False)}
- Empty Summaries: {corrupted_quality.get("summary_empty_count", 0)} (↑ {corrupted_quality.get("summary_empty_count", 0) - baseline_quality.get("summary_empty_count", 0)})
- Stale Rows (>180 days): {corrupted_quality.get("stale_rows_count", 0)}

### Repaired Quality
- Total Records: {repaired_quality.get("total_rows", 0)}
- Paper ID Unique: {repaired_quality.get("paper_id_is_unique", False)}
- Empty Summaries: {repaired_quality.get("summary_empty_count", 0)}
- Stale Rows (>180 days): {repaired_quality.get("stale_rows_count", 0)}

## 4. Conclusion
Repairing clean dataset directly from reliable raw source restores data observability signals and evaluation metrics back to baseline level.
"""
    write_text(Path(report_path), md)


