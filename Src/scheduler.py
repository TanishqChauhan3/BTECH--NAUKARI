"""
Scheduler — orchestrates the full ingestion pipeline using APScheduler.
Runs every 30 minutes: RSS fetch → Web scrape → Normalise → DB upsert.

Run standalone:  python scheduler.py
With Celery:     celery -A scheduler worker --loglevel=info
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from rss_fetcher import run_all_rss_fetchers
from web_scraper import run_all_scrapers
from normalizer import normalise_and_deduplicate

logger = logging.getLogger(__name__)


async def run_ingestion_pipeline():
    """
    Full pipeline:
      1. Fetch RSS feeds
      2. Scrape dynamic sites
      3. Normalise + deduplicate
      4. Upsert into PostgreSQL
    """
    logger.info("=" * 60)
    logger.info("INGESTION PIPELINE START")

    # Step 1: RSS
    rss_jobs = await run_all_rss_fetchers()
    logger.info("RSS: %d raw jobs", len(rss_jobs))

    # Step 2: Scrape (run in thread to avoid blocking event loop for sync parts)
    web_jobs = await run_all_scrapers()
    logger.info("Web scrape: %d raw jobs", len(web_jobs))

    # Step 3: Normalise + deduplicate
    all_raw = rss_jobs + web_jobs
    clean_jobs = normalise_and_deduplicate(all_raw)
    logger.info("After dedup: %d unique jobs", len(clean_jobs))

    # Step 4: Upsert into DB
    inserted = 0
    skipped  = 0
    try:
        # Import here to avoid circular imports at module load
        from database import AsyncSessionLocal
        from crud import upsert_job

        async with AsyncSessionLocal() as db:
            for job_data in clean_jobs:
                _, created = await upsert_job(db, job_data)
                if created:
                    inserted += 1
                else:
                    skipped += 1
            await db.commit()
    except Exception as exc:
        logger.exception("DB upsert error: %s", exc)

    logger.info("Pipeline done — inserted: %d, skipped (dupe): %d", inserted, skipped)
    logger.info("=" * 60)


def start_scheduler():
    """Start the APScheduler to run the pipeline every 30 minutes."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_ingestion_pipeline,
        trigger=IntervalTrigger(minutes=30),
        id="ingestion_pipeline",
        name="Full job ingestion",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    logger.info("Scheduler started. Pipeline runs every 30 minutes.")
    return scheduler


if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        stream=sys.stdout,
    )

    async def main():
        # Run once immediately on start
        await run_ingestion_pipeline()
        scheduler = start_scheduler()
        try:
            # Keep running
            while True:
                await asyncio.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("Scheduler stopped.")

    asyncio.run(main())
