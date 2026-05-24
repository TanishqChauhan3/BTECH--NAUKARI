"""
CareerBridge — FastAPI Backend
Job Aggregator Portal for B.Tech CS Graduates
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import engine, Base
from routers import jobs, sources, search

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CareerBridge API — creating DB tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database ready.")
    yield
    logger.info("Shutting down CareerBridge API.")


app = FastAPI(
    title="CareerBridge API",
    description="Job Aggregator Portal for B.Tech CS Graduates",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router,    prefix="/api/v1/jobs",    tags=["Jobs"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["Sources"])
app.include_router(search.router,  prefix="/api/v1/search",  tags=["Search"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "careerbridge-api"}
