from __future__ import annotations

from pathlib import Path
from typing import Any
from pathlib import Path
import pandas as pd

from core.config import Settings
from core.utils import write_json, read_json


def audit_embedding_manifest(settings: Settings, manifest_path: Path | None = None) -> dict[str, Any]:
    """Audit embedding manifest untuk track collection & document count.
    
    Memverifikasi:
    - Backend (Chroma)
    - Collection name
    - Document count
    - Embedding model
    - Timestamp audit
    
    Untuk audit trail: baseline_embedding_audit.json
    """
    if manifest_path is None:
        manifest_path = settings.paths.embeddings_json
    
    if not manifest_path.exists():
        return {
            "status": "NOT_FOUND",
            "timestamp": pd.Timestamp.now().isoformat(),
            "message": f"Embedding manifest not found at {manifest_path}"
        }
    
    try:
        manifest = read_json(manifest_path)
        
        documents = manifest.get("documents", [])
        doc_count = len(documents)
        
        # Verify document integrity
        paper_ids = [doc.get("paper_id") for doc in documents]
        unique_paper_ids = len(set(paper_ids))
        duplicate_record_ids = len([doc_id for doc_id in set(paper_ids) if paper_ids.count(doc_id) > 1])
        
        audit_report = {
            "status": "OK",
            "timestamp": pd.Timestamp.now().isoformat(),
            "backend": manifest.get("backend", "unknown"),
            "embedding_model": manifest.get("embedding_model", "unknown"),
            "collection_name": manifest.get("collection_name", "unknown"),
            "persist_path": manifest.get("persist_path", "unknown"),
            "document_count": doc_count,
            "unique_paper_ids": unique_paper_ids,
            "duplicate_records": duplicate_record_ids,
            "documents_integrity": {
                "total_documents": doc_count,
                "all_have_paper_id": all(doc.get("paper_id") for doc in documents),
                "all_have_title": all(doc.get("title") for doc in documents),
                "all_have_content": all(doc.get("content") for doc in documents),
            },
            "audit_result": "PASS" if doc_count > 0 and duplicate_record_ids == 0 else "WARN"
        }
        
        return audit_report
        
    except Exception as e:
        return {
            "status": "ERROR",
            "timestamp": pd.Timestamp.now().isoformat(),
            "error": str(e)
        }


def save_baseline_signals(
    quality_report: dict[str, Any],
    freshness_report: dict[str, Any],
    embedding_audit: dict[str, Any],
    settings: Settings
) -> dict[str, Any]:
    """Save baseline quality/freshness/embedding signals để đối chiếu sau corruption.
    
    Tập hợp 3 baseline reports thành 1 file baseline_signals.json
    để dùng làm reference khi compare với corrupted state.
    
    Outputs: data/quality/baseline_signals.json
    """
    baseline_signals = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "state": "baseline",
        "quality": quality_report,
        "freshness": freshness_report,
        "embedding_audit": embedding_audit,
    }
    
    signals_path = settings.paths.quality_dir / "baseline_signals.json"
    write_json(signals_path, baseline_signals)
    
    return {
        "status": "SAVED",
        "path": str(signals_path),
        "timestamp": baseline_signals["timestamp"],
        "message": "Baseline signals saved for corruption comparison"
    }


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Tao bo data quality checks va ghi ket qua vao data/quality/."""
    total_rows = len(df)
    paper_id_null = int(df["paper_id"].isnull().sum()) if "paper_id" in df else 0
    paper_id_unique = bool(df["paper_id"].is_unique) if "paper_id" in df else False
    title_null = int(df["title"].isnull().sum()) if "title" in df else 0
    summary_empty = int((df["summary"].fillna("").str.strip() == "").sum()) if "summary" in df else 0
    stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum()) if "age_days" in df else 0

    passed = bool(paper_id_null == 0 and paper_id_unique and title_null == 0 and summary_empty == 0)

    result = {
        "report_name": report_name,
        "total_rows": total_rows,
        "paper_id_null_count": paper_id_null,
        "paper_id_is_unique": paper_id_unique,
        "title_null_count": title_null,
        "summary_empty_count": summary_empty,
        "stale_rows_count": stale_rows,
        "passed": passed,
    }

    out_path = settings.paths.quality_dir / f"{report_name}.json"
    write_json(out_path, result)
    return result


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path: Any) -> dict[str, Any]:
    """Tong hop freshness report va ghi vao report_path."""
    if "published" in df and not df["published"].empty:
        published_dates = pd.to_datetime(df["published"], errors="coerce").dropna()
        latest_published = published_dates.max().strftime("%Y-%m-%d") if not published_dates.empty else "1970-01-01"
        oldest_published = published_dates.min().strftime("%Y-%m-%d") if not published_dates.empty else "1970-01-01"
    else:
        latest_published = "1970-01-01"
        oldest_published = "1970-01-01"

    stale_rows = int((df["age_days"] > settings.freshness_threshold_days).sum()) if "age_days" in df else 0
    total_rows = len(df)
    is_fresh = bool(stale_rows == 0)

    payload = {
        "latest_published": latest_published,
        "oldest_published": oldest_published,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "is_fresh": is_fresh,
        "freshness_threshold_days": settings.freshness_threshold_days,
    }

    write_json(Path(report_path), payload)
    return payload

