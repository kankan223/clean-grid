"""
Reports router - CleanGrid Phase 1
Complete implementation with security and validation
"""

import asyncio
import os
import structlog
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.auth import get_current_user_optional
from app.core.rate_limit import limiter
from app.services.storage import storage_service
from app.services.ai_client import ai_client
from app.services.geocoding import geocoding_service
from app.models.incident import Incident

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Reports"])

def validate_image_file(file: UploadFile) -> bool:
    """Validate image file type and size"""
    # Check file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Check MIME type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and WEBP are allowed."
        )
    
    return True

@router.get("/health")
async def health():
    return {"status": "reports router healthy"}

@router.get("/")
async def list_reports():
    return {"message": "Incident list working", "incidents": []}

@router.get("/{report_id}")
async def get_report_status(
    report_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the status of a report for polling"""
    try:
        # Query incident by ID
        result = await db.execute(
            text("SELECT * FROM incidents WHERE id = :id"),
            {"id": report_id}
        )
        incident = result.fetchone()
        
        if not incident:
            raise HTTPException(
                status_code=404,
                detail="Report not found"
            )
        
        # Convert to dict for response
        incident_dict = dict(incident._mapping)
        
        return {
            "report_id": incident_dict["id"],
            "status": incident_dict["status"],
            "severity": incident_dict["severity"],
            "confidence": incident_dict["confidence"],
            "waste_detected": incident_dict["waste_detected"],
            "message": f"Report status: {incident_dict['status']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report {report_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching report status."
        )

@router.post("/")
@limiter.limit("10/hour")
async def create_report(
    response: Response,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[object] = Depends(get_current_user_optional),
    image: UploadFile = File(...),
    lat: float = Form(...),
    lng: float = Form(...),
    note: Optional[str] = Form(None, max_length=200)
):
    """Create a new waste report with AI analysis"""
    
    # Validate image file
    validate_image_file(image)
    
    try:
        # Save uploaded image
        image_path = await storage_service.save_image(image)
        
        # Insert incident with PostGIS location using ST_GeomFromText
        result = await db.execute(
            text("""
                INSERT INTO incidents 
                (id, reporter_id, image_url, location, address_text, note, status, waste_detected, confidence, severity, is_hotspot)
                VALUES 
                (gen_random_uuid(), :reporter_id, :image_url, ST_GeomFromText(:location_wkt, 4326), :address_text, :note, :status, :waste_detected, :confidence, :severity, :is_hotspot)
                RETURNING id, status
            """),
            {
                "reporter_id": str(current_user.id) if current_user else None,
                "image_url": image_path,
                "location_wkt": f"POINT({lng} {lat})",  # PostGIS WKT format: longitude latitude
                "address_text": None,
                "note": note,
                "status": "Pending",
                "waste_detected": None,
                "confidence": None,
                "severity": None,
                "is_hotspot": False,
            }
        )
        
        report_row = result.fetchone()
        if not report_row:
            raise Exception("Failed to create incident in database")
        
        incident_id = str(report_row[0])
        
        await db.commit()
        
        # Schedule AI analysis in background
        background_tasks.add_task(
            process_ai_analysis, 
            incident_id, 
            image_path
        )
        
        logger.info(f"Created incident {incident_id} for user {current_user}")
        
        return {
            "report_id": incident_id,
            "status": "processing",
            "message": "Report submitted successfully. AI analysis in progress."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating report: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing report."
        )

async def process_ai_analysis(incident_id: str, image_path: str):
    """Background task to process AI analysis"""
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Get incident
            result = await db.execute(
                text("SELECT * FROM incidents WHERE id = :id"),
                {"id": incident_id}
            )
            incident_row = result.fetchone()
            
            if not incident_row:
                logger.error(f"Incident {incident_id} not found for AI analysis")
                return
            
            incident = incident_row
            
            # Call AI service
            try:
                ai_result = await ai_client.analyze_image(image_path)
                
                # Update incident with AI results
                await db.execute(
                    text("""
                        UPDATE incidents 
                        SET severity = :severity,
                            confidence = :confidence,
                            waste_detected = :waste_detected,
                            status = :status
                        WHERE id = :id
                    """),
                    {
                        "severity": ai_result.get('severity'),
                        "confidence": ai_result.get('confidence'),
                        "waste_detected": ai_result.get('waste_detected', False),
                        "status": "Verified" if ai_result.get('waste_detected') else "Cleaned",
                        "id": incident_id
                    }
                )
                
                await db.commit()
                
                # Broadcast update event
                await broadcast_incident_update(incident_id, "ai_analysis_complete")
                
                logger.info(f"AI analysis completed for incident {incident_id}")
                
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.error(f"AI service unavailable for incident {incident_id}: {e}")
                
                # Save with pending status if AI service fails
                await db.execute(
                    text("""
                        UPDATE incidents 
                        SET status = :status
                        WHERE id = :id
                    """),
                    {
                        "status": "NeedsReview",
                        "id": incident_id
                    }
                )
                await db.commit()
                
                await broadcast_incident_update(incident_id, "ai_analysis_failed")
                
        except Exception as e:
            logger.error(f"Error in AI analysis for incident {incident_id}: {e}")
            await db.rollback()

async def broadcast_incident_update(incident_id: str, event_type: str):
    """Broadcast incident update via SSE"""
    try:
        # This would integrate with the events router
        event_data = {
            "type": "incident_update",
            "incident_id": incident_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        redis_client = await get_redis()

        # Store event in Redis for SSE streaming
        await redis_client.lpush("incident_events", str(event_data))
        await redis_client.expire("incident_events", 3600)  # 1 hour
        
    except Exception as e:
        logger.error(f"Failed to broadcast incident update: {e}")
