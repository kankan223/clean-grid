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
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db, redis_client
from app.core.auth import get_current_user_optional
from app.services.storage import storage_service
from app.services.ai_client import ai_client
from app.services.geocoding import geocoding_service
from app.models.incident import Incident

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])

# Rate limiting configuration
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_REQUESTS = 10  # 10 requests per hour per IP

async def check_rate_limit(request: Request) -> bool:
    """Check if IP has exceeded rate limit using Redis sliding window"""
    client_ip = request.client.host
    current_time = datetime.utcnow().timestamp()
    
    # Clean up old entries and count current requests
    pipeline = redis_client.pipeline()
    pipeline.zremrangebyscore(f"rate_limit:{client_ip}", 0, current_time - RATE_LIMIT_WINDOW)
    pipeline.zcard(f"rate_limit:{client_ip}")
    pipeline.expire(f"rate_limit:{client_ip}", RATE_LIMIT_WINDOW)
    
    try:
        current_requests = await pipeline.execute()
        request_count = current_requests[1] if len(current_requests) > 1 else 0
        
        if request_count >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        # Add current request
        await redis_client.zadd(f"rate_limit:{client_ip}", {str(current_time): current_time})
        return True
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        # If Redis fails, allow the request (fail open)
        return True

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

@router.post("/")
async def create_report(
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
    
    # Rate limiting check
    if not await check_rate_limit(request):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 10 reports per hour."
        )
    
    # Validate image file
    validate_image_file(image)
    
    try:
        # Save uploaded image
        image_path = await storage_service.save_image(image)
        
        # Create initial incident record
        incident = Incident(
            latitude=lat,
            longitude=lng,
            note=note,
            image_url=image_path,
            status="pending_ai",
            severity=None,
            confidence=None,
            waste_detected=None,
            created_at=datetime.utcnow()
        )
        
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
        
        # Schedule AI analysis in background
        background_tasks.add_task(
            process_ai_analysis, 
            incident.id, 
            image_path
        )
        
        logger.info(f"Created incident {incident.id} for user {current_user}")
        
        return {
            "report_id": str(incident.id),
            "status": "processing",
            "message": "Report submitted successfully. AI analysis in progress."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing report."
        )

async def process_ai_analysis(incident_id: str, image_path: str):
    """Background task to process AI analysis"""
    async with get_db() as db:
        try:
            # Get incident
            incident = await db.get(Incident, incident_id)
            if not incident:
                logger.error(f"Incident {incident_id} not found for AI analysis")
                return
            
            # Call AI service
            try:
                ai_result = await ai_client.analyze_image(image_path)
                
                # Update incident with AI results
                incident.severity = ai_result.get('severity')
                incident.confidence = ai_result.get('confidence')
                incident.waste_detected = ai_result.get('waste_detected', False)
                incident.ai_metadata = ai_result
                incident.status = "active" if ai_result.get('waste_detected') else "verified_clean"
                
                # Add reverse geocoding
                try:
                    address = await geocoding_service.reverse_geocode(
                        incident.latitude, 
                        incident.longitude
                    )
                    incident.address = address
                except Exception as e:
                    logger.warning(f"Geocoding failed for incident {incident_id}: {e}")
                
                await db.commit()
                
                # Broadcast update event
                await broadcast_incident_update(incident.id, "ai_analysis_complete")
                
                logger.info(f"AI analysis completed for incident {incident_id}")
                
            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.error(f"AI service unavailable for incident {incident_id}: {e}")
                
                # Save with pending status if AI service fails
                incident.status = "pending_ai_review"
                incident.ai_error = str(e)
                await db.commit()
                
                await broadcast_incident_update(incident.id, "ai_analysis_failed")
                
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
        
        # Store event in Redis for SSE streaming
        await redis_client.lpush("incident_events", str(event_data))
        await redis_client.expire("incident_events", 3600)  # 1 hour
        
    except Exception as e:
        logger.error(f"Failed to broadcast incident update: {e}")
