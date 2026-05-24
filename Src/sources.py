"""
Router — /api/v1/sources
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import SourceOut
import crud

router = APIRouter()


@router.get("", response_model=list[SourceOut])
async def list_sources(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_sources(db)
