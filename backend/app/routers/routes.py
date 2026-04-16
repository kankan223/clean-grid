"""
Routes router - Phase 0 placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/routes", tags=["routes"])

@router.get("/health")
async def health():
    return {"status": "routes router healthy"}
