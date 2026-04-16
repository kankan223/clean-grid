"""
Test reports router - CleanGrid Phase 1
"""

from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/health")
async def health():
    return {"status": "reports router healthy"}

@router.get("/")
async def list_reports():
    return {"message": "Incident list working", "incidents": []}

@router.post("/")
async def create_report():
    return {"message": "Report created successfully"}
