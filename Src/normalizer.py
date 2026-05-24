"""
Normaliser — standardise raw job dicts from all scrapers into a
unified schema, then deduplicate using SHA-256 fingerprints.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Field maps ──────────────────────────────────────────────────
LOCATION_ALIASES = {
    "bengaluru": "Bangalore", "blr": "Bangalore",
    "new delhi": "Delhi", "ncr": "Delhi/NCR",
    "bombay": "Mumbai",
    "calcutta": "Kolkata",
    "pan india": "Pan India", "all india": "Pan India", "anywhere": "Pan India",
}

EXPERIENCE_PATTERNS = [
    (r"fresh(er)?s?",             "Fresher"),
    (r"0[\s\-–]?1\s*yr",         "0-1 yrs"),
    (r"0[\s\-–]?2\s*yr",         "0-2 yrs"),
    (r"1[\s\-–]?3\s*yr",         "1-3 yrs"),
    (r"graduate\s*train",        "Fresher"),
    (r"entry\s*level",           "Fresher"),
    (r"no\s*experience",         "Fresher"),
]

REQUIRED_FIELDS = ("title", "company", "location", "job_type", "apply_url", "source_id")


def _normalise_location(raw: str) -> str:
    if not raw:
        return "India"
    cleaned = raw.strip().rstrip(",. ").title()
    for alias, canonical in LOCATION_ALIASES.items():
        if alias in cleaned.lower():
            return canonical
    return cleaned[:150]


def _normalise_experience(raw: Optional[str], title: str = "") -> str:
    text = ((raw or "") + " " + title).lower()
    for pattern, label in EXPERIENCE_PATTERNS:
        if re.search(pattern, text):
            return label
    return raw[:50] if raw else "Not specified"


def _normalise_salary(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    # Remove HTML entities, normalise rupee symbol
    cleaned = re.sub(r"&[a-z]+;", "", raw).replace("INR", "₹").strip()
    return cleaned[:100] if cleaned else None


def _validate(job: dict) -> bool:
    for field in REQUIRED_FIELDS:
        if not job.get(field):
            logger.debug("Job missing required field '%s': %s", field, job.get("title"))
            return False
    if not job["apply_url"].startswith("http"):
        logger.debug("Invalid apply_url for job: %s", job.get("title"))
        return False
    return True


def normalise(raw_job: dict) -> Optional[dict]:
    """
    Normalise a raw scraped/parsed job dict into a standardised schema dict.
    Returns None if the job fails validation.
    """
    try:
        normalised = {
            "title":       (raw_job.get("title") or "").strip()[:300],
            "company":     (raw_job.get("company") or "Unknown").strip()[:200],
            "location":    _normalise_location(raw_job.get("location", "")),
            "job_type":    raw_job.get("job_type", "Private"),
            "experience":  _normalise_experience(raw_job.get("experience"), raw_job.get("title", "")),
            "salary":      _normalise_salary(raw_job.get("salary")),
            "description": (raw_job.get("description") or "")[:2000] or None,
            "apply_url":   (raw_job.get("apply_url") or "").strip()[:1024],
            "tags":        raw_job.get("tags") or [],
            "posted_at":   raw_job.get("posted_at") or datetime.now(timezone.utc),
            "source_id":   raw_job.get("source_id"),
        }
        if not _validate(normalised):
            return None
        return normalised
    except Exception as exc:
        logger.exception("Normalisation error for job '%s': %s", raw_job.get("title"), exc)
        return None


def deduplicate(jobs: list[dict]) -> list[dict]:
    """
    Remove in-memory duplicates using a fingerprint set.
    Database-level dedup is also applied in crud.upsert_job.
    """
    from models import Job  # lazy import to avoid circular deps
    seen = set()
    unique = []
    for job in jobs:
        fp = Job.make_fingerprint(job["title"], job["company"], job["location"])
        if fp not in seen:
            seen.add(fp)
            unique.append(job)

    dupes = len(jobs) - len(unique)
    if dupes:
        logger.info("Deduplication: removed %d duplicates (%d → %d)", dupes, len(jobs), len(unique))
    return unique


def normalise_and_deduplicate(raw_jobs: list[dict]) -> list[dict]:
    """End-to-end: normalise + deduplicate a batch of raw job dicts."""
    normalised = [n for r in raw_jobs if (n := normalise(r)) is not None]
    logger.info("Normalised %d / %d raw jobs", len(normalised), len(raw_jobs))
    return deduplicate(normalised)
