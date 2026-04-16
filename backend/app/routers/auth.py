"""
Authentication router - Phase 0 placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/health")
async def health():
    return {"status": "auth router healthy"}
