"""
Admin router - Phase 0 placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/health")
async def health():
    return {"status": "admin router healthy"}
