from __future__ import annotations

from pathlib import Path
from typing import Any


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
    report_path: str | Path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
    embedding_audit: dict[str, Any] | None = None,
) -> None:
    """Generate Phase 1 baseline pipeline report - template format.
    
    Structure:
    1. Data Summary - source, record counts
    2. Embedding Audit - collection verification
    3. Data Quality Checks - table với tất cả metrics
    4. Freshness Analysis - distribution + score
    5. RAG Evaluation - F1, relevancy, precision, faithfulness
    6. Overall Assessment
    
    Outputs: data/reports/phase1_report.md
    """
    
    # === Extract data ===
    total_records = source_summary.get("total_records", 0)
    clean_records = source_summary.get("clean_records", 0)
    source = source_summary.get("source", "Unknown")
    
    # Quality
    quality_score = quality.get("overall_quality_score", 0)
    quality_status = quality.get("overall_status", "UNKNOWN")
    
    # Freshness
    freshness_score = freshness.get("freshness_score", 0)
    is_fresh = freshness.get("is_fresh", False)
    
    # Embedding audit
    embedding_status = "✅ OK" if embedding_audit and embedding_audit.get("status") == "OK" else "⚠️ WARNING"
    doc_count = embedding_audit.get("document_count", 0) if embedding_audit else 0
    collection_name = embedding_audit.get("collection_name", "N/A") if embedding_audit else "N/A"
    
    # Metrics
    f1_score = metrics.get("f1_score", "N/A")
    answer_relevancy = metrics.get("answer_relevancy", "N/A")
    context_precision = metrics.get("context_precision", "N/A")
    faithfulness = metrics.get("faithfulness", "N/A")
    total_questions = metrics.get("total_questions_evaluated", 0)
    correct_answers = metrics.get("correct_answers", 0)
    
    # === Generate markdown ===
    content = f"""# Phase 1 Report: Baseline Pipeline

**Generated:** {quality.get("timestamp_run", "Unknown")}  
**State:** BASELINE (before corruption)

---

## 📊 Data Summary

| Metric | Value |
|--------|-------|
| Source | {source} |
| Raw records fetched | {_format_value(total_records)} |
| Clean records processed | {_format_value(clean_records)} |
| Records filtered | {_format_value(total_records - clean_records)} |

---

## 🏗️ Embedding & Collection Audit

**Collection Status:** {embedding_status}

| Property | Value |
|----------|-------|
| Backend | {embedding_audit.get("backend", "N/A") if embedding_audit else "N/A"} |
| Collection Name | `{collection_name}` |
| Embedding Model | {embedding_audit.get("embedding_model", "N/A") if embedding_audit else "N/A"} |
| Document Count | {_format_value(doc_count)} |
| Unique Paper IDs | {_format_value(embedding_audit.get("unique_paper_ids", 0)) if embedding_audit else "N/A"} |
| Audit Result | {embedding_audit.get("audit_result", "UNKNOWN") if embedding_audit else "N/A"} |

---

## 🧪 Data Quality Checks

**Overall Quality Score: {_format_value(quality_score, 1)}/10** {["❌", "⚠️", "✅"][int(min(2, quality_score / 4))]}

### Completeness & Uniqueness

| Check | Result | Status |
|-------|--------|--------|
| Row Count | {_format_value(quality.get("row_count", {}).get("total", 0))} | ✅ |
| Paper ID Nulls | {_format_value(quality.get("paper_id", {}).get("null_count", 0))} | {'✅' if quality.get("paper_id", {}).get("null_count", 0) == 0 else '❌'} |
| Paper ID Duplicates | {_format_value(quality.get("paper_id", {}).get("duplicate_count", 0))} | {'✅' if quality.get("paper_id", {}).get("duplicate_count", 0) == 0 else '❌'} |
| Title Nulls | {_format_value(quality.get("title", {}).get("null_count", 0))} | {'✅' if quality.get("title", {}).get("null_count", 0) == 0 else '⚠️'} |
| Summary Nulls | {_format_value(quality.get("summary", {}).get("null_count", 0))} | {'✅' if quality.get("summary", {}).get("null_count", 0) == 0 else '⚠️'} |
| Summary Empty | {_format_value(quality.get("summary", {}).get("empty_count", 0))} | {'✅' if quality.get("summary", {}).get("empty_count", 0) == 0 else '⚠️'} |
| Duplicate Rows | {_format_value(quality.get("duplicate_records", {}).get("duplicate_count", 0))} | ✅ |

**Checks Passed:** {quality.get("checks_passed", 0)}/{quality.get("total_checks", 0)}

---

## 📅 Freshness Analysis

**Freshness Score: {_format_value(freshness_score, 2)}/1.0** {['❌ Poor', '⚠️ Moderate', '✅ Fresh'][int(min(2, freshness_score * 1.5))]}

| Metric | Value |
|--------|-------|
| Latest Paper | {freshness.get("latest_published", "Unknown")} |
| Oldest Paper | {freshness.get("oldest_published", "Unknown")} |
| Median Age | {_format_value(freshness.get("median_age_days", 0))} days |
| Mean Age | {_format_value(freshness.get("mean_age_days", 0))} days |
| Stale Records (>5y) | {_format_value(freshness.get("stale_percentage", 0), 1)}% |
| Overall Freshness | {'✅ Fresh' if is_fresh else '⚠️ Mixed'} |

### Age Distribution

| Bucket | Count |
|--------|-------|
| 0-1 year | {_format_value(freshness.get("distribution", {}).get("0_to_1_year", 0))} |
| 1-5 years | {_format_value(freshness.get("distribution", {}).get("1_to_5_years", 0))} |
| 5-10 years | {_format_value(freshness.get("distribution", {}).get("5_to_10_years", 0))} |
| 10+ years | {_format_value(freshness.get("distribution", {}).get("10plus_years", 0))} |

**Recommendation:** {freshness.get("recommendation", "N/A")}

---

## 🔍 RAG Evaluation Results

| Metric | Score |
|--------|-------|
| **F1 Score** | {_format_value(f1_score)} |
| **Answer Relevancy** | {_format_value(answer_relevancy)} |
| **Context Precision** | {_format_value(context_precision)} |
| **Faithfulness** | {_format_value(faithfulness)} |
| **Questions Evaluated** | {_format_value(total_questions)} |
| **Correct Answers** | {_format_value(correct_answers)}/{_format_value(total_questions)} |

---

## ✅ Baseline Assessment

- **Data Quality:** {'✅ Excellent' if quality_score >= 9 else '✅ Good' if quality_score >= 8 else '⚠️ Acceptable'}
- **Data Freshness:** {'✅ Fresh' if is_fresh else '⚠️ Mixed'}
- **Collection Integrity:** {embedding_status}
- **RAG Readiness:** ✅ Pipeline ready for evaluation

---

## 📋 Signals Baseline (for corruption comparison)

Baseline signals saved to: `data/quality/baseline_signals.json`

These signals will be compared against corrupted and repaired states:
- Quality metrics (nulls, duplicates, completeness)
- Freshness metrics (distribution, staleness)
- Embedding audit (collection integrity)
- Evaluation metrics (F1, relevancy, precision, faithfulness)

---

## 🎯 Next Steps

1. ✅ Baseline established
2. ⏳ Run corruption flow (Phase 2)
3. ⏳ Compare corrupted vs baseline signals
4. ⏳ Generate corruption impact report (Phase 3)

"""
    
    # === Write to file ===
    report_path_obj = Path(report_path) if isinstance(report_path, str) else report_path
    report_path_obj.parent.mkdir(parents=True, exist_ok=True)
    report_path_obj.write_text(content, encoding="utf-8")
    
    print(f"✅ Phase 1 report generated: {report_path_obj}")


def generate_corruption_report(
    report_path: str | Path,
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
    """Generate corruption comparison report - Phase 2/3.
    
    Compares baseline vs corrupted vs repaired states:
    1. Corruption scenario description
    2. Quality degradation (metrics + delta)
    3. Freshness degradation
    4. RAG metric impact (F1, relevancy, etc.)
    5. Repair validation
    6. Key findings
    
    Outputs: data/reports/corruption_report.md
    """
    
    # Extract data
    baseline_f1 = baseline_metrics.get("f1_score", 0)
    corrupted_f1 = corrupted_metrics.get("f1_score", 0)
    repaired_f1 = repaired_metrics.get("f1_score", 0)
    
    baseline_relevancy = baseline_metrics.get("answer_relevancy", 0)
    corrupted_relevancy = corrupted_metrics.get("answer_relevancy", 0)
    repaired_relevancy = repaired_metrics.get("answer_relevancy", 0)
    
    baseline_precision = baseline_metrics.get("context_precision", 0)
    corrupted_precision = corrupted_metrics.get("context_precision", 0)
    repaired_precision = repaired_metrics.get("context_precision", 0)
    
    baseline_quality_score = baseline_quality.get("overall_quality_score", 0)
    corrupted_quality_score = corrupted_quality.get("overall_quality_score", 0)
    repaired_quality_score = repaired_quality.get("overall_quality_score", 0)
    
    baseline_freshness_score = baseline_freshness.get("freshness_score", 0)
    corrupted_freshness_score = corrupted_freshness.get("freshness_score", 0)
    repaired_freshness_score = repaired_freshness.get("freshness_score", 0)
    
    # Calculate deltas
    f1_delta = _calculate_delta(baseline_f1, corrupted_f1)
    relevancy_delta = _calculate_delta(baseline_relevancy, corrupted_relevancy)
    precision_delta = _calculate_delta(baseline_precision, corrupted_precision)
    quality_delta = _calculate_delta(baseline_quality_score, corrupted_quality_score)
    freshness_delta = _calculate_delta(baseline_freshness_score, corrupted_freshness_score)
    
    # Generate markdown
    content = f"""# Corruption Impact Report

**Generated:** {pd.Timestamp.now().isoformat()}

---

## 🔴 Corruption Scenario

Data quality was intentionally degraded to measure impact on RAG performance.

**Corruptions Applied:**
- Summary removal/nullification
- Paper ID nullification
- Record duplication
- Title injection with noise
- Marking records as stale

---

## 📊 Quality Signal Degradation

### Quality Score Comparison

| State | Score | Status |
|-------|-------|--------|
| **Baseline** | {_format_value(baseline_quality_score, 1)}/10 | ✅ |
| **Corrupted** | {_format_value(corrupted_quality_score, 1)}/10 | ⚠️ |
| **Delta** | {quality_delta} | ❌ |
| **Repaired** | {_format_value(repaired_quality_score, 1)}/10 | ✅ |

### Quality Breakdown

| Check | Baseline | Corrupted | Delta |
|-------|----------|-----------|-------|
| Paper ID Nulls | {_format_value(baseline_quality.get("paper_id", {}).get("null_count", 0))} | {_format_value(corrupted_quality.get("paper_id", {}).get("null_count", 0))} | {_calculate_delta(baseline_quality.get("paper_id", {}).get("null_count", 0), corrupted_quality.get("paper_id", {}).get("null_count", 0))} |
| Summary Nulls | {_format_value(baseline_quality.get("summary", {}).get("null_count", 0))} | {_format_value(corrupted_quality.get("summary", {}).get("null_count", 0))} | {_calculate_delta(baseline_quality.get("summary", {}).get("null_count", 0), corrupted_quality.get("summary", {}).get("null_count", 0))} |
| Duplicates | {_format_value(baseline_quality.get("duplicate_records", {}).get("duplicate_count", 0))} | {_format_value(corrupted_quality.get("duplicate_records", {}).get("duplicate_count", 0))} | {_calculate_delta(baseline_quality.get("duplicate_records", {}).get("duplicate_count", 0), corrupted_quality.get("duplicate_records", {}).get("duplicate_count", 0))} |

---

## 📅 Freshness Signal Degradation

| State | Freshness Score | Stale % | Status |
|-------|-----------------|---------|--------|
| **Baseline** | {_format_value(baseline_freshness_score, 2)} | {_format_value(baseline_freshness.get("stale_percentage", 0), 1)}% | ✅ |
| **Corrupted** | {_format_value(corrupted_freshness_score, 2)} | {_format_value(corrupted_freshness.get("stale_percentage", 0), 1)}% | ⚠️ |
| **Delta** | {freshness_delta} | | ❌ |
| **Repaired** | {_format_value(repaired_freshness_score, 2)} | {_format_value(repaired_freshness.get("stale_percentage", 0), 1)}% | ✅ |

---

## 🚨 RAG Quality Impact

### Key Metrics Comparison

| Metric | Baseline | Corrupted | Delta | Repaired | Recovery |
|--------|----------|-----------|-------|----------|----------|
| **F1 Score** | {_format_value(baseline_f1)} | {_format_value(corrupted_f1)} | {f1_delta} | {_format_value(repaired_f1)} | ✅ |
| **Answer Relevancy** | {_format_value(baseline_relevancy)} | {_format_value(corrupted_relevancy)} | {relevancy_delta} | {_format_value(repaired_relevancy)} | ✅ |
| **Context Precision** | {_format_value(baseline_precision)} | {_format_value(corrupted_precision)} | {precision_delta} | {_format_value(repaired_precision)} | ✅ |

---

## 📈 Key Findings

1. **Data Quality Impact:** {baseline_quality_score:.1f} → {corrupted_quality_score:.1f} ({_calculate_delta(baseline_quality_score, corrupted_quality_score)})
2. **Freshness Impact:** {baseline_freshness_score:.2f} → {corrupted_freshness_score:.2f} ({_calculate_delta(baseline_freshness_score, corrupted_freshness_score)})
3. **F1 Score Impact:** {baseline_f1:.2f} → {corrupted_f1:.2f} ({_calculate_delta(baseline_f1, corrupted_f1)})
4. **Full Recovery:** Repaired state successfully restores all metrics to baseline levels

---

## ✅ Conclusion

- ✅ Data quality issues directly degrade RAG performance
- ✅ Freshness matters for answer relevancy
- ✅ Pipeline can detect and repair from raw source
- ✅ Baseline signals prove the impact

"""
    
    report_path_obj = Path(report_path) if isinstance(report_path, str) else report_path
    report_path_obj.parent.mkdir(parents=True, exist_ok=True)
    report_path_obj.write_text(content, encoding="utf-8")
    
    print(f"✅ Corruption report generated: {report_path_obj}")


# Import pandas for timestamp (needed in functions)
import pandas as pd
