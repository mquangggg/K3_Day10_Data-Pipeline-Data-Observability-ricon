from typing import Any
from pathlib import Path
import pandas as pd

from core.config import Settings
from core.utils import write_json


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

