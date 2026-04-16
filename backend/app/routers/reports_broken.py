"""
Simple reports router - CleanGrid Phase 1
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.auth import get_current_user_optional

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/health")
async def health():
    return {"status": "reports router healthy"}

@router.post("/")
async def create_report(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[object] = Depends(get_current_user_optional),
    image: UploadFile = File(...),
    lat: float = Form(...),
    lng: float = Form(...),
    note: Optional[str] = Form(None)
):
    return {"message": "Report created successfully", "lat": lat, "lng": lng}
