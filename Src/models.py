"""
ORM Models — Jobs, Sources, Categories
"""

import hashlib
from datetime import datetime, timezone
from sqlalchemy import (
    String, Text, DateTime, Boolean, Integer,
    ForeignKey, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR, ARRAY
from database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    id:          Mapped[int]  = mapped_column(Integer, primary_key=True)
    name:        Mapped[str]  = mapped_column(String(100), unique=True, nullable=False)
    url:         Mapped[str]  = mapped_column(String(512), nullable=False)
    feed_type:   Mapped[str]  = mapped_column(String(20), nullable=False)   # rss | scrape
    is_active:   Mapped[bool] = mapped_column(Boolean, default=True)
    last_fetched: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:  Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="source_rel")


class Job(Base):
    __tablename__ = "jobs"

    id:           Mapped[int]  = mapped_column(Integer, primary_key=True)
    title:        Mapped[str]  = mapped_column(String(300), nullable=False)
    company:      Mapped[str]  = mapped_column(String(200), nullable=False)
    location:     Mapped[str]  = mapped_column(String(150), nullable=False)
    job_type:     Mapped[str]  = mapped_column(String(20), nullable=False)   # Private | Govt | PSU
    experience:   Mapped[str]  = mapped_column(String(50), nullable=True)
    salary:       Mapped[str | None]  = mapped_column(String(100), nullable=True)
    description:  Mapped[str | None]  = mapped_column(Text, nullable=True)
    apply_url:    Mapped[str]  = mapped_column(String(1024), nullable=False)
    tags:         Mapped[list] = mapped_column(ARRAY(String), nullable=True, default=list)
    posted_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at:   Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_active:    Mapped[bool] = mapped_column(Boolean, default=True)

    # SHA-256 fingerprint for deduplication: hash(title + company + location)
    fingerprint:  Mapped[str]  = mapped_column(String(64), unique=True, nullable=False, index=True)

    source_id:    Mapped[int]  = mapped_column(ForeignKey("sources.id"), nullable=False)
    source_rel:   Mapped["Source"] = relationship("Source", back_populates="jobs")

    # Full-text search vector (populated by DB trigger or in crud)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

    __table_args__ = (
        Index("ix_jobs_type",     "job_type"),
        Index("ix_jobs_location", "location"),
        Index("ix_jobs_posted",   "posted_at"),
        Index("ix_jobs_fts",      "search_vector", postgresql_using="gin"),
    )

    @staticmethod
    def make_fingerprint(title: str, company: str, location: str) -> str:
        raw = f"{title.strip().lower()}|{company.strip().lower()}|{location.strip().lower()}"
        return hashlib.sha256(raw.encode()).hexdigest()
