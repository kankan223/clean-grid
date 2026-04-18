"""
Public Incidents Router
Provides read-only access to incident data for the map view
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
import structlog

from app.core.database import get_db
from app.models.incident import Incident
from app.models.user import User

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/incidents")
async def get_public_incidents(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    fields: Optional[str] = Query("id,lat,lng,severity,status,imageUrl,createdAt")
):
    """
    Get incidents for public map view
    Returns limited fields for security and performance
    """
    try:
        # Parse fields parameter
        requested_fields = [f.strip() for f in fields.split(",")]
        
        # Build base query
        query = select(Incident)
        
        # Apply filters
        if status:
            query = query.where(Incident.status == status)
        
        if severity:
            query = query.where(Incident.severity == severity)
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query
        result = await db.execute(query)
        incidents = result.scalars().all()
        
        # Format response with requested fields only
        incident_data = []
        for incident in incidents:
            incident_dict = {}
            
            # Map requested fields to incident properties
            field_mapping = {
                "id": str(incident.id),
                "lat": float(incident.latitude),
                "lng": float(incident.longitude),
                "severity": incident.severity,
                "status": incident.status,
                "imageUrl": incident.image_url,
                "createdAt": incident.created_at.isoformat(),
                "priorityScore": incident.priority_score,
                "note": incident.note,
                "aiConfidence": incident.ai_confidence,
            }
            
            for field in requested_fields:
                if field in field_mapping:
                    incident_dict[field] = field_mapping[field]
            
            incident_data.append(incident_dict)
        
        return {
            "incidents": incident_data,
            "total": len(incident_data),
            "limit": limit,
            "filters": {
                "status": status,
                "severity": severity,
                "fields": fields
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching public incidents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch incidents"
        )

@router.get("/incidents/stats")
async def get_public_stats(db: AsyncSession = Depends(get_db)):
    """
    Get public incident statistics
    Returns aggregated counts for dashboard
    """
    try:
        # Get total incidents
        total_query = select(func.count(Incident.id))
        total = await db.scalar(total_query)
        
        # Get counts by status
        status_counts = {}
        for status in ["Pending", "Assigned", "InProgress", "Cleaned", "Verified", "NeedsReview"]:
            status_query = select(func.count(Incident.id)).where(Incident.status == status)
            status_counts[status.lower()] = await db.scalar(status_query) or 0
        
        # Get counts by severity
        severity_counts = {}
        for severity in ["High", "Medium", "Low", "None"]:
            severity_query = select(func.count(Incident.id)).where(Incident.severity == severity)
            severity_counts[severity.lower()] = await db.scalar(severity_query) or 0
        
        return {
            "total": total or 0,
            "pending": status_counts["pending"],
            "assigned": status_counts["assigned"],
            "inProgress": status_counts["inprogress"],
            "cleaned": status_counts["cleaned"],
            "verified": status_counts["verified"],
            "needsReview": status_counts["needsreview"],
            "severity": severity_counts
        }
        
    except Exception as e:
        logger.error(f"Error fetching public stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch statistics"
        )

@router.get("/incidents/health")
async def health():
    """Incidents router health check"""
    return {"status": "incidents router healthy"}
