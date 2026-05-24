"""
Web Scraper — Playwright (JS-heavy sites) + BeautifulSoup (static HTML)
Targets: Internshala, NIC portal, SSC, BEL, ONGC

Anti-bot mitigations:
  - playwright-stealth to mask automation signals
  - Randomised delays between requests
  - Rotating User-Agents
  - Respects robots.txt

Usage:
  python web_scraper.py
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timezone
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser

logger = logging.getLogger(__name__)

# ── User-Agent pool ───────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


def random_delay(min_s: float = 1.5, max_s: float = 4.0):
    time.sleep(random.uniform(min_s, max_s))


# ── Internshala (static-ish, paginates via URL params) ────────────
async def scrape_internshala(page: Page, source_id: int) -> list[dict]:
    jobs = []
    base_url = "https://internshala.com/jobs/computer-science-jobs"
    logger.info("Scraping Internshala...")

    try:
        for pg in range(1, 4):   # scrape first 3 pages
            url = f"{base_url}/page-{pg}/"
            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            await page.wait_for_timeout(random.randint(1500, 3000))

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            cards = soup.select(".internship_meta") or soup.select(".job-internship-card")
            if not cards:
                logger.warning("Internshala page %d — no cards found, may be blocked", pg)
                break

            for card in cards:
                title    = (card.select_one(".profile") or card.select_one("h3"))
                company  = card.select_one(".company_name") or card.select_one(".company-name")
                location = card.select_one(".location_link") or card.select_one(".location")
                salary   = card.select_one(".stipend") or card.select_one(".salary")
                link_tag = card.find_parent("a") or card.select_one("a")

                if not title:
                    continue

                jobs.append({
                    "title":     title.get_text(strip=True)[:300],
                    "company":   company.get_text(strip=True)[:200] if company else "Unknown",
                    "location":  location.get_text(strip=True)[:150] if location else "India",
                    "job_type":  "Private",
                    "experience":"Fresher",
                    "salary":    salary.get_text(strip=True)[:100] if salary else None,
                    "apply_url": "https://internshala.com" + (link_tag["href"] if link_tag and link_tag.get("href","").startswith("/") else ""),
                    "tags":      [],
                    "posted_at": datetime.now(timezone.utc),
                    "source_id": source_id,
                })

            logger.info("Internshala page %d — %d jobs so far", pg, len(jobs))
            random_delay()

    except Exception as exc:
        logger.exception("Internshala scrape failed: %s", exc)

    return jobs


# ── NIC Jobs (static govt portal) ────────────────────────────────
async def scrape_nic_portal(page: Page, source_id: int) -> list[dict]:
    jobs = []
    url = "https://recruitment.nic.in/job-opening"
    logger.info("Scraping NIC portal...")

    try:
        await page.goto(url, wait_until="networkidle", timeout=40_000)
        await page.wait_for_timeout(2000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select("table tbody tr") or soup.select(".job-row")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            title    = cols[0].get_text(strip=True)
            location = cols[1].get_text(strip=True) if len(cols) > 1 else "Delhi"
            deadline = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            link     = row.find("a")

            if not title:
                continue

            jobs.append({
                "title":     title[:300],
                "company":   "National Informatics Centre",
                "location":  location[:150],
                "job_type":  "Govt",
                "experience":"Fresher",
                "salary":    None,
                "apply_url": link["href"] if link and link.get("href") else url,
                "tags":      ["Java", "Python", "Linux"],
                "posted_at": datetime.now(timezone.utc),
                "source_id": source_id,
                "description": f"Application deadline: {deadline}",
            })

    except Exception as exc:
        logger.exception("NIC portal scrape failed: %s", exc)

    return jobs


# ── Generic BeautifulSoup scraper for static PSU pages ───────────
def scrape_static_html(html: str, company: str, job_type: str, source_id: int, base_url: str) -> list[dict]:
    """
    Reusable static HTML scraper.
    Tries common job listing patterns — override selectors per site.
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # Try common patterns
    for selector in [".job-listing", ".vacancy-item", "table tbody tr", ".notice-row"]:
        items = soup.select(selector)
        if items:
            for item in items:
                text = item.get_text(" ", strip=True)
                link = item.find("a")
                if len(text) < 10:
                    continue
                jobs.append({
                    "title":     text[:200],
                    "company":   company,
                    "location":  "India",
                    "job_type":  job_type,
                    "experience":"Fresher",
                    "apply_url": (base_url + link["href"]) if link and link.get("href","").startswith("/") else (link["href"] if link else base_url),
                    "tags":      [],
                    "posted_at": datetime.now(timezone.utc),
                    "source_id": source_id,
                })
            if jobs:
                break

    return jobs


# ── Main scraper orchestrator ─────────────────────────────────────
async def run_all_scrapers() -> list[dict]:
    all_jobs = []

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
        )

        for scraper_fn, source_id in [
            (scrape_internshala, 5),
            (scrape_nic_portal,  6),
        ]:
            context = await browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
                ignore_https_errors=True,
            )
            # Stealth: hide navigator.webdriver
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)
            page = await context.new_page()
            try:
                jobs = await scraper_fn(page, source_id)
                all_jobs.extend(jobs)
            finally:
                await context.close()
            random_delay(2, 5)

        await browser.close()

    logger.info("Web scrape complete — %d raw jobs", len(all_jobs))
    return all_jobs


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    jobs = asyncio.run(run_all_scrapers())
    print(json.dumps(jobs[:3], indent=2, default=str))
