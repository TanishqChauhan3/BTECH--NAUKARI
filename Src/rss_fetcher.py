"""
RSS Fetcher — parses RSS/Atom feeds for job listings
Handles malformed XML, encoding issues, and missing fields gracefully.
"""

import logging
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ── RSS Sources Config ────────────────────────────────────────────
RSS_SOURCES = [
    {
        "name": "TimesJobs CS",
        "url": "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=computer+science&txtLocation=&rssFeed=true",
        "job_type": "Private",
        "source_id": 1,
    },
    {
        "name": "Shine.com IT Fresher",
        "url": "https://www.shine.com/rss/jobs/it-software/fresh.xml",
        "job_type": "Private",
        "source_id": 2,
    },
    {
        "name": "Freshersworld CS",
        "url": "https://www.freshersworld.com/jobs/rss/computer-science",
        "job_type": "Private",
        "source_id": 3,
    },
    {
        "name": "Govt Jobs Portal",
        "url": "https://www.govtjobsalert.in/feed/",
        "job_type": "Govt",
        "source_id": 4,
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CareerBridgeBot/1.0; +https://careerbridge.in/bot)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def _parse_date(entry) -> Optional[datetime]:
    """Try multiple date fields from feedparser."""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                continue
    return None


def _clean_text(text: str) -> str:
    """Strip HTML tags from description snippets."""
    import re
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _extract_tags(text: str) -> list[str]:
    """Heuristic skill extraction from title/description."""
    SKILL_KEYWORDS = [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Angular",
        "Node.js", "Django", "FastAPI", "Spring", "SQL", "PostgreSQL", "MongoDB",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux", "Git",
        "Machine Learning", "Deep Learning", "Data Science", "Networking",
        "SAP", "ERP", "MATLAB", "Embedded", "C", "Go", "Rust",
    ]
    found = []
    text_lower = text.lower()
    for skill in SKILL_KEYWORDS:
        if skill.lower() in text_lower and skill not in found:
            found.append(skill)
    return found[:6]


async def fetch_rss_source(session: aiohttp.ClientSession, source: dict) -> list[dict]:
    """Fetch and parse a single RSS source. Returns a list of normalised job dicts."""
    jobs = []
    url = source["url"]
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.warning("RSS %s returned HTTP %d", source["name"], resp.status)
                return jobs
            content = await resp.read()

        feed = feedparser.parse(content)

        if feed.bozo and not feed.entries:
            logger.warning("Malformed RSS from %s: %s", source["name"], feed.bozo_exception)
            return jobs

        logger.info("RSS [%s] — %d entries", source["name"], len(feed.entries))

        for entry in feed.entries:
            title   = _clean_text(getattr(entry, "title", "") or "")
            company = _clean_text(getattr(entry, "author", "") or source["name"])
            link    = getattr(entry, "link", "") or ""
            summary = _clean_text(getattr(entry, "summary", "") or getattr(entry, "description", "") or "")
            location = "India"  # RSS rarely has location; enrich later

            if not title or not link:
                continue

            jobs.append({
                "title":       title[:300],
                "company":     company[:200],
                "location":    location,
                "job_type":    source["job_type"],
                "experience":  "Fresher",
                "description": summary[:2000] if summary else None,
                "apply_url":   link[:1024],
                "tags":        _extract_tags(title + " " + summary),
                "posted_at":   _parse_date(entry),
                "source_id":   source["source_id"],
            })

    except asyncio.TimeoutError:
        logger.error("Timeout fetching RSS source: %s", source["name"])
    except Exception as exc:
        logger.exception("Unexpected error fetching %s: %s", source["name"], exc)

    return jobs


async def run_all_rss_fetchers() -> list[dict]:
    """Run all RSS fetchers concurrently. Returns flat list of job dicts."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_rss_source(session, src) for src in RSS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_jobs = []
    for res in results:
        if isinstance(res, list):
            all_jobs.extend(res)
        else:
            logger.error("RSS task raised: %s", res)

    logger.info("RSS fetch complete — %d raw jobs collected", len(all_jobs))
    return all_jobs


if __name__ == "__main__":
    import json
    jobs = asyncio.run(run_all_rss_fetchers())
    print(json.dumps(jobs[:3], indent=2, default=str))
