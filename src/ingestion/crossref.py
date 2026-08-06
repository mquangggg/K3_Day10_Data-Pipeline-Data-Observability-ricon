import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
import urllib.parse
import requests

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    # Remove XML / HTML tags like <jats:p>, <jats:title>, etc.
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _extract_date(item: dict) -> str:
    for date_field in ("published-online", "published-print", "issued", "created"):
        if date_field in item and "date-parts" in item[date_field]:
            parts = item[date_field]["date-parts"]
            if parts and parts[0]:
                dp = parts[0]
                year = str(dp[0])
                month = f"{dp[1]:02d}" if len(dp) > 1 and dp[1] is not None else "01"
                day = f"{dp[2]:02d}" if len(dp) > 2 and dp[2] is not None else "01"
                return f"{year}-{month}-{day}"
    return "1970-01-01"


def _generate_paper_id(doi: str, fallback_idx: int) -> str:
    if doi:
        cleaned = re.sub(r"[^a-zA-Z0-9]", "_", doi).strip("_").lower()
        return f"doi_{cleaned}"
    return f"crossref_rec_{fallback_idx:04d}"


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload thanh list PaperRecord."""
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for idx, item in enumerate(items):
        doi = item.get("DOI", "")
        paper_id = _generate_paper_id(doi, idx + 1)

        # Title
        raw_titles = item.get("title", [])
        title = _clean_text(raw_titles[0] if raw_titles else "")
        if not title:
            continue

        # Summary / Abstract
        summary = _clean_text(item.get("abstract", ""))

        # Authors
        raw_authors = item.get("author", [])
        authors = []
        for a in raw_authors:
            if "given" in a and "family" in a:
                authors.append(f"{a['given']} {a['family']}")
            elif "family" in a:
                authors.append(a["family"])
            elif "name" in a:
                authors.append(a["name"])
        if not authors:
            authors = ["Unknown Author"]

        # Categories / Subject
        categories = item.get("subject", [])
        if not categories:
            categories = ["Computer Science"]
        primary_category = categories[0]

        # Dates
        published = _extract_date(item)
        updated = published

        # URLs
        abs_url = item.get("URL", f"https://doi.org/{doi}" if doi else "")
        pdf_url = ""
        for link in item.get("link", []):
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL", "")
                break

        comment = f"Source: Crossref API. DOI: {doi}"

        records.append(
            PaperRecord(
                paper_id=paper_id,
                title=title,
                summary=summary,
                authors=authors,
                categories=categories,
                primary_category=primary_category,
                published=published,
                updated=updated,
                abs_url=abs_url,
                pdf_url=pdf_url,
                comment=comment,
            )
        )

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Goi Crossref API, luu raw response, parse va luu records JSON."""
    base_url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results,
    }
    headers = {
        "User-Agent": "DataPipelineLab/1.0 (mailto:lab@example.com)"
    }

    response_payload = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.get(base_url, params=params, headers=headers, timeout=30)
            if resp.status_code == 200:
                response_payload = resp.json()
                break
            elif resp.status_code in (429, 503):
                time.sleep(2 ** attempt)
            else:
                resp.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Crossref API call failed after {max_retries} attempts: {e}") from e
            time.sleep(2 ** attempt)

    if not response_payload:
        raise RuntimeError("Failed to fetch response payload from Crossref API.")

    # Save raw API response
    settings.paths.raw_api_response.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.paths.raw_api_response, "w", encoding="utf-8") as f:
        json.dump(response_payload, f, ensure_ascii=False, indent=2)

    # Parse payload
    records = parse_crossref_payload(response_payload)

    # Save parsed records JSON
    settings.paths.raw_records_json.parent.mkdir(parents=True, exist_ok=True)
    records_dict_list = [asdict(r) for r in records]
    with open(settings.paths.raw_records_json, "w", encoding="utf-8") as f:
        json.dump(records_dict_list, f, ensure_ascii=False, indent=2)

    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Doc JSON snapshot va map thanh list PaperRecord."""
    if not path.exists():
        raise FileNotFoundError(f"Raw records file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw_list = json.load(f)

    return [PaperRecord(**item) for item in raw_list]

