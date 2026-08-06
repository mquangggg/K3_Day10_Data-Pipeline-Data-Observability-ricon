from datetime import datetime, timezone
import re
import pandas as pd

from ingestion.crossref import PaperRecord


def _normalize_str(val: str | None) -> str:
    if not val:
        return ""
    return re.sub(r"\s+", " ", val).strip()


def _parse_date(date_str: str) -> datetime:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records thanh dataframe san sang de embed."""
    if run_date.tzinfo is None:
        run_date = run_date.replace(tzinfo=timezone.utc)

    cleaned_rows = []
    for r in records:
        title = _normalize_str(r.title)
        summary = _normalize_str(r.summary)

        # Skip rows missing vital fields
        if not title or not summary:
            continue

        authors = r.authors if isinstance(r.authors, list) else [str(r.authors)]
        categories = r.categories if isinstance(r.categories, list) else [str(r.categories)]

        authors_joined = ", ".join([_normalize_str(a) for a in authors if _normalize_str(a)])
        if not authors_joined:
            authors_joined = "Unknown Author"

        categories_joined = ", ".join([_normalize_str(c) for c in categories if _normalize_str(c)])
        if not categories_joined:
            categories_joined = "Computer Science"

        primary_category = _normalize_str(r.primary_category) or categories_joined.split(",")[0]
        published_str = _normalize_str(r.published) or "1970-01-01"
        updated_str = _normalize_str(r.updated) or published_str

        pub_dt = _parse_date(published_str)
        age_days = (run_date.date() - pub_dt.date()).days

        text_for_embedding = f"Title: {title}\nSummary: {summary}\nCategories: {categories_joined}"

        cleaned_rows.append(
            {
                "paper_id": _normalize_str(r.paper_id),
                "title": title,
                "summary": summary,
                "authors": authors,
                "authors_joined": authors_joined,
                "categories": categories,
                "categories_joined": categories_joined,
                "primary_category": primary_category,
                "published": published_str,
                "updated": updated_str,
                "abs_url": _normalize_str(r.abs_url),
                "pdf_url": _normalize_str(r.pdf_url),
                "comment": _normalize_str(r.comment),
                "summary_chars": len(summary),
                "age_days": max(0, age_days),
                "text_for_embedding": text_for_embedding,
            }
        )

    if not cleaned_rows:
        return pd.DataFrame(
            columns=[
                "paper_id",
                "title",
                "summary",
                "authors",
                "authors_joined",
                "categories",
                "categories_joined",
                "primary_category",
                "published",
                "updated",
                "abs_url",
                "pdf_url",
                "comment",
                "summary_chars",
                "age_days",
                "text_for_embedding",
            ]
        )

    df = pd.DataFrame(cleaned_rows)

    # Deduplicate by paper_id (keep first occurrence)
    df = df.drop_duplicates(subset=["paper_id"], keep="first")

    # Sort dataframe by published descending, then paper_id
    df = df.sort_values(by=["published", "paper_id"], ascending=[False, True]).reset_index(drop=True)

    return df

