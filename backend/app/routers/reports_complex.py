"""
Reports router - CleanGrid Phase 1
Handles incident reporting, retrieval, and status updates
"""

import uuid
import os
import asyncio
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from geoalchemy2.functions import ST_Point, ST_MakeEnvelope, ST_DWithin
import httpx
import structlog

from app.core.database import get_db
from app.models.incident import Incident, IncidentStatus, IncidentSeverity
from app.models.points import User, PointTransaction, PointReason
from app.schemas.report import (
    ReportCreate, ReportResponse, ReportListResponse,
    IncidentResponse, ReportUpdate
)
from app.services.ai_client import call_ai_service
from app.services.geocoding import reverse_geocode
from app.services.storage import save_upload_file
from app.core.auth import get_current_user_optional
from app.routers.events import broadcast_incident_created

logger = structlog.get_logger()
router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/", response_model=ReportResponse)
async def create_report(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    image: UploadFile = File(...),
    lat: float = Form(...),
    lng: float = Form(...),
    note: Optional[str] = Form(None, max_length=200)
):
    """
    Create a new waste report
    Handles image upload, AI analysis, and database storage
    """
    logger.info("Creating new report", lat=lat, lng=lng, has_image=bool(image))
    
    try:
        # Validate file
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG, and WEBP images are accepted"
            )
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(await image.read()) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File exceeds 10MB limit. Please compress or choose another image"
            )
        
        # Reset file position
        await image.seek(0)
        
        # Save uploaded image
        image_url = await save_upload_file(image)
        
        # Create initial incident record
        incident = Incident(
            reporter_id=current_user.id if current_user else None,
            image_url=image_url,
            location=ST_Point(lng, lat, srid=4326),
            note=note,
            status=IncidentStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        
        # Call AI service in background
        background_tasks.add_task(
            process_ai_analysis,
            incident_id=str(incident.id),
            image_url=image_url
        )
        
        logger.info("Report created successfully", incident_id=str(incident.id))
        
        return ReportResponse(
            report_id=str(incident.id),
            status="processing",
            message="Report submitted successfully. Analyzing image..."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create report", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to process report. Please try again."
        )


async def process_ai_analysis(incident_id: str, image_url: str):
    """
    Background task to process AI analysis
    Called after report is created
    """
    logger.info("Starting AI analysis", incident_id=incident_id)
    
    async with get_db() as db:
        try:
            # Get incident
            result = await db.execute(
                select(Incident).where(Incident.id == uuid.UUID(incident_id))
            )
            incident = result.scalar_one_or_none()
            
            if not incident:
                logger.error("Incident not found for AI analysis", incident_id=incident_id)
                return
            
            # Call AI service
            ai_result = await call_ai_service(image_url)
            
            # Update incident with AI results
            incident.waste_detected = ai_result.get("waste_detected", False)
            incident.confidence = ai_result.get("confidence")
            incident.severity = ai_result.get("severity")
            incident.bounding_boxes = ai_result.get("detections", [])
            
            # Calculate priority score based on severity and status
            if incident.severity == IncidentSeverity.HIGH:
                base_priority = 80
            elif incident.severity == IncidentSeverity.MEDIUM:
                base_priority = 50
            elif incident.severity == IncidentSeverity.LOW:
                base_priority = 20
            else:
                base_priority = 0
            
            incident.priority_score = base_priority * 0.8  # PENDING status multiplier
            incident.status = IncidentStatus.PENDING if incident.waste_detected else IncidentStatus.NEEDS_REVIEW
            incident.updated_at = datetime.utcnow()
            
            # Perform reverse geocoding if we have location
            if incident.location:
                try:
                    lat = float(incident.location.ST_Y)
                    lng = float(incident.location.ST_X)
                    address = await reverse_geocode(lat, lng)
                    incident.address_text = address
                except Exception as e:
                    logger.warning("Reverse geocoding failed", error=str(e))
            
            await db.commit()
            
            logger.info(
                "AI analysis completed",
                incident_id=incident_id,
                waste_detected=incident.waste_detected,
                severity=incident.severity
            )
            
            # Broadcast incident update event
            await broadcast_incident_updated(incident)
            
        except Exception as e:
            logger.error("AI analysis failed", incident_id=incident_id, error=str(e))
            await db.rollback()


@router.get("/", response_model=ReportListResponse)
async def list_incidents(
    lat_min: Optional[float] = None,
    lat_max: Optional[float] = None,
    lng_min: Optional[float] = None,
    lng_max: Optional[float] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get incidents with spatial bounding box query
    Supports map viewport filtering and pagination
    """
    logger.info("Fetching incidents", bounds=[lat_min, lat_max, lng_min, lng_max])
    
    try:
        # Build base query
        query = select(Incident)
        
        # Apply spatial bounding box filter if provided
        if all([lat_min, lat_max, lng_min, lng_max]):
            bbox = ST_MakeEnvelope(lat_min, lng_min, lat_max, lng_max, 4326)
            query = query.where(ST_DWithin(Incident.location, bbox))
        
        # Apply status filter
        if status:
            query = query.where(Incident.status == status)
        
        # Apply severity filter
        if severity:
            query = query.where(Incident.severity == severity)
        
        # Add ordering by priority score (descending)
        query = query.order_by(Incident.priority_score.desc())
        
        # Execute query with pagination
        result = await db.execute(
            query.offset(offset).limit(limit)
        )
        incidents = result.scalars().all()
        
        # Get total count for pagination
        count_query = select(Incident)
        if all([lat_min, lat_max, lng_min, lng_max]):
            count_query = count_query.where(ST_DWithin(Incident.location, bbox))
        if status:
            count_query = count_query.where(Incident.status == status)
        if severity:
            count_query = count_query.where(Incident.severity == severity)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        return ReportListResponse(
            incidents=[IncidentResponse.from_orm(incident) for incident in incidents],
            total=total,
            offset=offset,
            limit=limit
        )
        
    except Exception as e:
        logger.error("Failed to fetch incidents", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch incidents"
        )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get single incident by ID
    """
    logger.info("Fetching incident", incident_id=incident_id)
    
    try:
        result = await db.execute(
            select(Incident)
            .where(Incident.id == uuid.UUID(incident_id))
            .options(selectinload(Incident.reporter))
        )
        incident = result.scalar_one_or_none()
        
        if not incident:
            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )
        
        return IncidentResponse.from_orm(incident)
        
    except Exception as e:
        logger.error("Failed to fetch incident", incident_id=incident_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch incident"
        )


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    update: ReportUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update incident status with validation
    """
    logger.info("Updating incident status", incident_id=incident_id, new_status=update.status)
    
    async with get_db() as db:
        try:
            # Get current incident
            result = await db.execute(
                select(Incident).where(Incident.id == uuid.UUID(incident_id))
            )
            incident = result.scalar_one_or_none()
            
            if not incident:
                raise HTTPException(
                    status_code=404,
                    detail="Incident not found"
                )
            
            old_status = incident.status
            
            # Validate status transitions
            allowed_transitions = {
                IncidentStatus.PENDING: [IncidentStatus.ASSIGNED, IncidentStatus.NEEDS_REVIEW],
                IncidentStatus.ASSIGNED: [IncidentStatus.IN_PROGRESS, IncidentStatus.NEEDS_REVIEW],
                IncidentStatus.IN_PROGRESS: [IncidentStatus.CLEANED, IncidentStatus.NEEDS_REVIEW],
                IncidentStatus.CLEANED: [IncidentStatus.VERIFIED, IncidentStatus.NEEDS_REVIEW],
                IncidentStatus.NEEDS_REVIEW: [IncidentStatus.PENDING, IncidentStatus.ASSIGNED]
            }
            
            if update.status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition from {old_status} to {update.status}"
                )
            
            # Update incident
            incident.status = update.status
            incident.updated_at = datetime.utcnow()
            
            # Recalculate priority score based on new status
            status_multipliers = {
                IncidentStatus.PENDING: 0.8,
                IncidentStatus.ASSIGNED: 1.0,
                IncidentStatus.IN_PROGRESS: 1.2,
                IncidentStatus.CLEANED: 1.5,
                IncidentStatus.VERIFIED: 2.0,
                IncidentStatus.NEEDS_REVIEW: 0.6
            }
            
            base_priority = {
                IncidentSeverity.HIGH: 80,
                IncidentSeverity.MEDIUM: 50,
                IncidentSeverity.LOW: 20,
                IncidentSeverity.NONE: 0
            }.get(incident.severity, 0)
            
            incident.priority_score = base_priority * status_multipliers.get(update.status, 1.0)
            
            await db.commit()
            await db.refresh(incident)
            
            logger.info(
                "Incident status updated",
                incident_id=incident_id,
                old_status=old_status,
                new_status=update.status
            )
            
            # Broadcast incident update event
            await broadcast_incident_updated(incident)
            
            return IncidentResponse.from_orm(incident)
            
        except Exception as e:
            logger.error("Failed to update incident", incident_id=incident_id, error=str(e))
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to update incident status"
            )
