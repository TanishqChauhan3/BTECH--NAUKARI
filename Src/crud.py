"""
CRUD operations — all database interactions in one place
"""

import logging
from sqlalchemy import select, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Job, Source
from schemas import JobFilters, SearchQuery

logger = logging.getLogger(__name__)


# ── Sources ───────────────────────────────────────────────────────
async def get_all_sources(db: AsyncSession) -> list[Source]:
    result = await db.execute(select(Source).where(Source.is_active == True))
    return result.scalars().all()


# ── Jobs ──────────────────────────────────────────────────────────
async def get_jobs(db: AsyncSession, filters: JobFilters):
    stmt = select(Job).where(Job.is_active == True)

    if filters.job_type:
        stmt = stmt.where(Job.job_type == filters.job_type)
    if filters.location:
        stmt = stmt.where(Job.location.ilike(f"%{filters.location}%"))
    if filters.experience:
        stmt = stmt.where(Job.experience.ilike(f"%{filters.experience}%"))
    if filters.source_id:
        stmt = stmt.where(Job.source_id == filters.source_id)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        stmt
        .order_by(Job.posted_at.desc().nullslast(), Job.scraped_at.desc())
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    )
    results = (await db.execute(stmt)).scalars().all()
    return total, results


async def get_job_by_id(db: AsyncSession, job_id: int) -> Job | None:
    stmt = (
        select(Job)
        .where(Job.id == job_id, Job.is_active == True)
        .options(selectinload(Job.source_rel))
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def search_jobs(db: AsyncSession, query: SearchQuery):
    """
    PostgreSQL full-text search via tsvector.
    Falls back to ILIKE for dev environments without trigram extension.
    """
    try:
        stmt = (
            select(Job)
            .where(
                Job.is_active == True,
                Job.search_vector.op("@@")(func.plainto_tsquery("english", query.q)),
            )
        )
        if query.job_type:
            stmt = stmt.where(Job.job_type == query.job_type)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = (
            stmt
            .order_by(
                func.ts_rank(Job.search_vector, func.plainto_tsquery("english", query.q)).desc()
            )
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        results = (await db.execute(stmt)).scalars().all()

    except Exception:
        logger.warning("FTS failed, falling back to ILIKE search")
        like = f"%{query.q}%"
        stmt = select(Job).where(
            Job.is_active == True,
            or_(
                Job.title.ilike(like),
                Job.company.ilike(like),
                Job.description.ilike(like),
            ),
        )
        if query.job_type:
            stmt = stmt.where(Job.job_type == query.job_type)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()
        stmt = stmt.offset((query.page - 1) * query.page_size).limit(query.page_size)
        results = (await db.execute(stmt)).scalars().all()

    return total, results


async def upsert_job(db: AsyncSession, job_data: dict) -> tuple[Job, bool]:
    """
    Insert a new job or skip if fingerprint already exists.
    Returns (job, created: bool)
    """
    fingerprint = Job.make_fingerprint(
        job_data["title"], job_data["company"], job_data["location"]
    )
    existing = (
        await db.execute(select(Job).where(Job.fingerprint == fingerprint))
    ).scalar_one_or_none()

    if existing:
        return existing, False

    job = Job(**job_data, fingerprint=fingerprint)
    db.add(job)
    await db.flush()
    logger.info("Inserted new job: %s @ %s", job.title, job.company)
    return job, True
