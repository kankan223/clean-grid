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
from app.core.redis import get_redis
from app.models.incident import Incident
from app.models.user import User

logger = __import__('structlog').get_logger(__name__)

router = APIRouter(tags=["admin"])

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
    limit: int = Query(20, ge=10, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    sort: str = Query("created_at", pattern="^(created_at|priority_score|severity)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    assigned_to: Optional[str] = Query(None)
):
    """Get paginated list of incidents for admin dashboard with advanced filtering and sorting"""
    
    try:
        # Build base query with joins for user info
        query = select(
            Incident,
            User.display_name.label("reporter_name")
        ).outerjoin(User, Incident.reporter_id == User.id)
        
        # Apply filters
        if status:
            query = query.where(Incident.status == status)
        
        if severity:
            query = query.where(Incident.severity == severity)
            
        if assigned_to:
            query = query.where(Incident.assigned_to == assigned_to)
        
        # Apply sorting
        if sort == "created_at":
            order_column = Incident.created_at
        elif sort == "priority_score":
            order_column = Incident.priority_score
        elif sort == "severity":
            order_column = Incident.severity
        else:
            order_column = Incident.created_at
            
        if order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        rows = result.all()
        
        # Get total count for pagination
        count_query = select(func.count(Incident.id))
        if status:
            count_query = count_query.where(Incident.status == status)
        if severity:
            count_query = count_query.where(Incident.severity == severity)
        if assigned_to:
            count_query = count_query.where(Incident.assigned_to == assigned_to)
        
        total_count = await db.scalar(count_query)
        
        # Format response
        incidents = []
        for incident, reporter_name in rows:
            # Calculate age in human readable format
            now = datetime.utcnow()
            age = now - incident.created_at
            if age.days > 0:
                age_str = f"{age.days}d ago"
            elif age.seconds > 3600:
                age_str = f"{age.seconds // 3600}h ago"
            elif age.seconds > 60:
                age_str = f"{age.seconds // 60}m ago"
            else:
                age_str = "just now"
            
            incidents.append({
                "id": str(incident.id),
                "status": incident.status,
                "severity": incident.severity,
                "priority_score": incident.priority_score,
                "location": {
                    "lat": float(incident.latitude),
                    "lng": float(incident.longitude)
                },
                "created_at": incident.created_at.isoformat(),
                "age": age_str,
                "reporter_name": reporter_name or "Anonymous",
                "assigned_to": incident.assigned_to,
                "image_url": incident.image_url,
                "ai_confidence": incident.ai_confidence,
                "note": incident.note
            })
        
        return {
            "incidents": incidents,
            "total": total_count or 0,
            "offset": offset,
            "limit": limit,
            "filters": {
                "status": status,
                "severity": severity,
                "assigned_to": assigned_to,
                "sort": sort,
                "order": order
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch incidents"
        )

@router.get("/users")
async def get_crew_members(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    role: str = Query("crew", pattern="^(crew|admin)$")
):
    """Get list of users by role for assignment dropdown"""
    
    try:
        # Query users by role
        query = select(User).where(User.role == role)
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Get current workload for each crew member
        crew_list = []
        for user in users:
            # Count currently assigned incidents
            workload_query = select(func.count(Incident.id)).where(
                Incident.assigned_to == str(user.id),
                Incident.status.in_(["Assigned", "In Progress"])
            )
            workload = await db.scalar(workload_query)
            
            crew_list.append({
                "id": str(user.id),
                "name": user.display_name or user.email,
                "email": user.email,
                "role": user.role,
                "current_workload": workload or 0
            })
        
        return {
            "crew": crew_list,
            "total": len(crew_list)
        }
        
    except Exception as e:
        logger.error(f"Error fetching crew members: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch crew members"
        )


@router.patch("/incidents/{incident_id}/assign")
async def assign_incident(
    incident_id: str,
    assignment: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Assign incident to crew member"""
    
    try:
        # Validate incident exists
        incident_query = select(Incident).where(Incident.id == incident_id)
        incident_result = await db.execute(incident_query)
        incident = incident_result.scalar_one_or_none()
        
        if not incident:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )
        
        # Validate crew member exists
        crew_id = assignment.get("assigned_to")
        if crew_id:
            crew_query = select(User).where(User.id == crew_id, User.role == "crew")
            crew_result = await db.execute(crew_query)
            crew_member = crew_result.scalar_one_or_none()
            
            if not crew_member:
                raise HTTPException(
                    status_code=404,
                    detail="Crew member not found"
                )
        
        # Update incident assignment
        incident.assigned_to = crew_id
        if crew_id:
            incident.status = "Assigned"
        incident.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(incident)
        
        # Get crew member info for response
        crew_info = None
        if crew_id:
            crew_info = {
                "id": str(crew_member.id),
                "name": crew_member.display_name or crew_member.email,
                "email": crew_member.email
            }
        
        return {
            "id": str(incident.id),
            "status": incident.status,
            "assigned_to": crew_info,
            "updated_at": incident.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning incident {incident_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to assign incident"
        )


@router.get("/health")
async def health():
    """Admin router health check"""
    return {"status": "admin router healthy"}


@router.get("/status")
async def status(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin readiness endpoint used for operational health checks."""
    db_status = "healthy"
    redis_status = "healthy"

    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error(f"Admin status database check failed: {exc}")
        db_status = "unhealthy"

    try:
        redis_client = await get_redis()
        await redis_client.ping()
    except Exception as exc:
        logger.error(f"Admin status Redis check failed: {exc}")
        redis_status = "unhealthy"

    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat(),
    }
