"""
Incident model - CleanGrid Phase 1
PostGIS-enabled incident tracking with AI analysis results
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Column, String, Boolean, Float, Integer, Text, 
    DateTime, ForeignKey, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography  # PostGIS support
from geoalchemy2.types import Geography as GeographyType

from app.core.database import Base


class IncidentStatus(str, Enum):
    """Incident status enumeration"""
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "InProgress"
    CLEANED = "Cleaned"
    VERIFIED = "Verified"
    NEEDS_REVIEW = "NeedsReview"


class IncidentSeverity(str, Enum):
    """AI-derived severity levels"""
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class UserRole(str, Enum):
    """User role enumeration"""
    CITIZEN = "citizen"
    CREW = "crew"
    ADMIN = "admin"


class BadgeTier(str, Enum):
    """User badge tiers based on points"""
    CLEANER = "Cleaner"
    GUARDIAN = "Guardian"
    HERO = "Hero"


class PointReason(str, Enum):
    """Point transaction reasons"""
    REPORT_CONFIRMED = "report_confirmed"
    CLEANUP_VERIFIED = "cleanup_verified"
    REPORT_BONUS = "report_bonus"


class Incident(Base):
    """
    Incident model with PostGIS location and AI analysis results
    Represents a waste report with location, images, and AI analysis
    """
    __tablename__ = "incidents"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User relationships
    reporter_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # Anonymous reporting allowed
        index=True
    )
    assigned_to = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Media
    image_url = Column(Text, nullable=False, comment="URL to before-photo in object storage")
    after_image_url = Column(Text, nullable=True, comment="URL to after-photo")
    
    # Location (PostGIS Geography)
    location = Column(
        Geography("POINT", srid=4326, spatial_index=True),
        nullable=False,
        comment="PostGIS geospatial point (WGS84)"
    )
    address_text = Column(Text, nullable=True, comment="Reverse-geocoded or user-provided address")
    
    # User input
    note = Column(Text, nullable=True, comment="Optional user note (max 200 chars)")
    
    # AI Analysis Results
    waste_detected = Column(Boolean, nullable=True, comment="AI result - was waste detected?")
    confidence = Column(Float, nullable=True, comment="AI confidence score (0-1)")
    severity = Column(
        String(10), 
        nullable=True,
        comment="AI-derived severity: None, Low, Medium, High"
    )
    bounding_boxes = Column(
        JSONB,
        nullable=True,
        comment="Optional array of bounding box coordinates"
    )
    
    # Status and Priority
    status = Column(
        String(20),
        default=IncidentStatus.PENDING,
        nullable=False,
        index=True,
        comment="Current incident status"
    )
    priority_score = Column(
        Float,
        nullable=True,
        index=True,
        comment="Computed priority score (0-100)"
    )
    is_hotspot = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether in a known hotspot zone"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When incident was reported"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When incident was last updated"
    )
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_incidents")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_incidents")
    point_transactions = relationship("PointTransaction", back_populates="incident")
    
    def __repr__(self):
        return f"<Incident(id={self.id}, status={self.status}, severity={self.severity})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "reporter_id": str(self.reporter_id) if self.reporter_id else None,
            "assigned_to": str(self.assigned_to) if self.assigned_to else None,
            "image_url": self.image_url,
            "after_image_url": self.after_image_url,
            "location": {
                "lat": float(self.location.ST_Y),
                "lon": float(self.location.ST_X)
            } if self.location else None,
            "address_text": self.address_text,
            "note": self.note,
            "waste_detected": self.waste_detected,
            "confidence": self.confidence,
            "severity": self.severity,
            "bounding_boxes": self.bounding_boxes,
            "status": self.status,
            "priority_score": self.priority_score,
            "is_hotspot": self.is_hotspot,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
