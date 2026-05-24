"""
Router — /api/v1/search
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database import get_db
from schemas import PaginatedJobs, SearchQuery, JobType
import crud

router = APIRouter()


@router.get("", response_model=PaginatedJobs)
async def keyword_search(
    q: str               = Query(..., min_length=2, max_length=200),
    job_type: Optional[JobType] = Query(None),
    page: int            = Query(1, ge=1),
    page_size: int       = Query(20, ge=1, le=100),
    db: AsyncSession     = Depends(get_db),
):
    query = SearchQuery(q=q, job_type=job_type, page=page, page_size=page_size)
    total, jobs = await crud.search_jobs(db, query)
    return PaginatedJobs(total=total, page=page, page_size=page_size, results=jobs)
