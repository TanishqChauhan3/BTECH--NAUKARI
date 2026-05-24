"""
Pydantic Schemas — request validation and API response shapes
"""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, HttpUrl, Field


# ── Source Schemas ────────────────────────────────────────────────
class SourceOut(BaseModel):
    id: int
    name: str
    url: str
    feed_type: str
    is_active: bool
    last_fetched: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Job Schemas ───────────────────────────────────────────────────
JobType = Literal["Private", "Govt", "PSU"]


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    job_type: JobType
    experience: Optional[str]
    salary: Optional[str]
    apply_url: str
    tags: list[str]
    posted_at: Optional[datetime]
    scraped_at: datetime
    source_id: int

    model_config = {"from_attributes": True}


class JobDetail(JobOut):
    description: Optional[str]
    fingerprint: str
    source_rel: SourceOut


# ── Filter / Pagination Schemas ───────────────────────────────────
class JobFilters(BaseModel):
    job_type: Optional[JobType]   = Field(None, description="Private | Govt | PSU")
    location: Optional[str]       = Field(None, max_length=100)
    experience: Optional[str]     = Field(None, max_length=50)
    source_id: Optional[int]      = None
    page: int                     = Field(1, ge=1)
    page_size: int                = Field(20, ge=1, le=100)


class PaginatedJobs(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[JobOut]


# ── Search Schema ─────────────────────────────────────────────────
class SearchQuery(BaseModel):
    q: str = Field(..., min_length=2, max_length=200, description="Search keywords")
    job_type: Optional[JobType] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
