"""
Leaderboard router - Phase 0 placeholder
"""

from fastapi import APIRouter

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/health")
async def health():
    return {"status": "leaderboard router healthy"}
