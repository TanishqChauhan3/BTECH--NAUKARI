"""
Router — /api/v1/jobs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import JobDetail, JobFilters, JobOut, JobType, PaginatedJobs
import crud

router = APIRouter()


@router.get("", response_model=PaginatedJobs)
async def list_jobs(
    job_type: Optional[JobType] = Query(None, description="Filter by Private | Govt | PSU"),
    location: Optional[str]     = Query(None, max_length=100),
    experience: Optional[str]   = Query(None, max_length=50),
    source_id: Optional[int]    = Query(None),
    page: int                   = Query(1, ge=1),
    page_size: int              = Query(20, ge=1, le=100),
    db: AsyncSession            = Depends(get_db),
):
    filters = JobFilters(
        job_type=job_type, location=location,
        experience=experience, source_id=source_id,
        page=page, page_size=page_size,
    )
    total, jobs = await crud.get_jobs(db, filters)
    return PaginatedJobs(total=total, page=page, page_size=page_size, results=jobs)


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await crud.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/refresh", status_code=202, tags=["Admin"])
async def trigger_refresh():
    """Trigger a manual scrape cycle (sends task to Celery)."""
    from services.scheduler import trigger_all_scrapers
    trigger_all_scrapers.delay()
    return {"message": "Scrape cycle triggered", "status": "queued"}
