"""
Events router - Phase 0 placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/health")
async def health():
    return {"status": "events router healthy"}
