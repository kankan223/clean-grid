"""
Report schemas - CleanGrid Phase 1
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class ReportCreate(BaseModel):
    """Request schema for creating a new report"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    note: Optional[str] = Field(None, max_length=200, description="Optional note")


class ReportResponse(BaseModel):
    """Response schema for report creation"""
    report_id: str = Field(..., description="Unique report identifier")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")


class DetectionBox(BaseModel):
    """Bounding box for AI detection results"""
    label: str = Field(..., description="Detected object class")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    box: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")


class IncidentResponse(BaseModel):
    """Response schema for incident data"""
    id: str = Field(..., description="Incident UUID")
    reporter_id: Optional[str] = Field(None, description="Reporter user ID")
    assigned_to: Optional[str] = Field(None, description="Assigned crew user ID")
    image_url: str = Field(..., description="URL to before-photo")
    after_image_url: Optional[str] = Field(None, description="URL to after-photo")
    location: dict = Field(..., description="GPS coordinates")
    address_text: Optional[str] = Field(None, description="Reverse-geocoded address")
    note: Optional[str] = Field(None, description="User note")
    waste_detected: Optional[bool] = Field(None, description="AI waste detection result")
    confidence: Optional[float] = Field(None, description="AI confidence score")
    severity: Optional[str] = Field(None, description="AI severity classification")
    bounding_boxes: Optional[List[DetectionBox]] = Field(None, description="AI detection boxes")
    status: str = Field(..., description="Current incident status")
    priority_score: Optional[float] = Field(None, description="Computed priority score")
    is_hotspot: bool = Field(False, description="Whether in hotspot zone")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @classmethod
    def from_orm(cls, incident) -> "IncidentResponse":
        """Create response from ORM model"""
        return cls(
            id=str(incident.id),
            reporter_id=str(incident.reporter_id) if incident.reporter_id else None,
            assigned_to=str(incident.assigned_to) if incident.assigned_to else None,
            image_url=incident.image_url,
            after_image_url=incident.after_image_url,
            location={
                "lat": float(incident.location.ST_Y),
                "lon": float(incident.location.ST_X)
            } if incident.location else None,
            address_text=incident.address_text,
            note=incident.note,
            waste_detected=incident.waste_detected,
            confidence=incident.confidence,
            severity=incident.severity,
            bounding_boxes=[
                DetectionBox(**box) for box in (incident.bounding_boxes or {}).get("detections", [])
            ] if incident.bounding_boxes else None,
            status=incident.status,
            priority_score=incident.priority_score,
            is_hotspot=incident.is_hotspot,
            created_at=incident.created_at,
            updated_at=incident.updated_at
        )


class ReportUpdate(BaseModel):
    """Request schema for updating incident status"""
    status: str = Field(..., description="New status")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")


class ReportListResponse(BaseModel):
    """Response schema for incident list"""
    incidents: List[IncidentResponse] = Field(..., description="List of incidents")
    total: int = Field(..., description="Total number of incidents")
    offset: int = Field(..., description="Pagination offset")
    limit: int = Field(..., description="Pagination limit")
