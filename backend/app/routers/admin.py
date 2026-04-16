"""
Admin router - CleanGrid Phase 2
Admin dashboard endpoints with role-based access control
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.core.auth import get_current_user, require_admin
from app.core.database import get_db
from app.models.incident import Incident
from app.models.user import User

logger = __import__('structlog').get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    
    try:
        # Get counts for different statuses
        active_count = await db.scalar(
            select(func.count(Incident.id))
            .where(Incident.status == "active")
        )
        
        in_progress_count = await db.scalar(
            select(func.count(Incident.id))
            .where(Incident.status == "in_progress")
        )
        
        # Get verified today (start of day)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        verified_today_count = await db.scalar(
            select(func.count(Incident.id))
            .where(
                (Incident.status == "verified_clean") &
                (Incident.created_at >= today_start)
            )
        )
        
        return {
            "active": active_count or 0,
            "in_progress": in_progress_count or 0,
            "verified_today": verified_today_count or 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch admin statistics"
        )

@router.get("/incidents")
async def get_incidents(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=10, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None)
):
    """Get paginated list of incidents for admin dashboard"""
    
    try:
        # Build base query
        query = select(Incident)
        
        # Apply filters
        if status:
            query = query.where(Incident.status == status)
        
        if severity:
            query = query.where(Incident.severity == severity)
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        incidents = result.scalars().all()
        
        # Get total count for pagination
        count_query = select(func.count(Incident.id))
        if status:
            count_query = count_query.where(Incident.status == status)
        if severity:
            count_query = count_query.where(Incident.severity == severity)
        
        total_count = await db.scalar(count_query)
        
        return {
            "incidents": [
                {
                    "id": str(incident.id),
                    "status": incident.status,
                    "severity": incident.severity,
                    "location": {
                        "lat": float(incident.latitude),
                        "lng": float(incident.longitude)
                    },
                    "created_at": incident.created_at.isoformat(),
                    "assigned_to": incident.assigned_to
                }
                for incident in incidents
            ],
            "total": total_count or 0,
            "offset": offset,
            "limit": limit,
            "filters": {
                "status": status,
                "severity": severity
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch incidents"
        )

@router.get("/health")
async def health():
    """Admin router health check"""
    return {"status": "admin router healthy"}
