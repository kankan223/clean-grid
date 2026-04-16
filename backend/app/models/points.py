"""
User and PointTransaction models - CleanGrid Phase 1
User management with roles and gamification point system
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Column, String, Boolean, Float, Integer, Text, 
    DateTime, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


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


class User(Base):
    """
    User model with roles, points, and badge tiers
    Supports citizen reporting, crew assignment, and admin management
    """
    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email for login"
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="bcrypt hashed password"
    )
    
    # Profile
    display_name = Column(
        String(100),
        nullable=False,
        comment="Public-facing name"
    )
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.CITIZEN,
        nullable=False,
        index=True,
        comment="User role: citizen, crew, or admin"
    )
    
    # Gamification
    total_points = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Total accumulated points"
    )
    badge_tier = Column(
        SQLEnum(BadgeTier),
        nullable=True,
        comment="Computed badge tier based on points"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When user account was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="When user was last updated"
    )
    
    # Relationships
    reported_incidents = relationship(
        "Incident",
        foreign_keys="Incident.reporter_id",
        back_populates="reporter",
        cascade="all, delete-orphan"
    )
    assigned_incidents = relationship(
        "Incident", 
        foreign_keys="Incident.assigned_to",
        back_populates="assignee",
        cascade="all, delete-orphan"
    )
    point_transactions = relationship(
        "PointTransaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "display_name": self.display_name,
            "role": self.role,
            "total_points": self.total_points,
            "badge_tier": self.badge_tier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_badge_tier(self):
        """Update badge tier based on total points"""
        if self.total_points >= 100:
            self.badge_tier = BadgeTier.HERO
        elif self.total_points >= 50:
            self.badge_tier = BadgeTier.GUARDIAN
        elif self.total_points >= 10:
            self.badge_tier = BadgeTier.CLEANER
        else:
            self.badge_tier = None


class PointTransaction(Base):
    """
    Point transaction model for gamification
    Tracks point awards for reporting and cleanup verification
    """
    __tablename__ = "point_transactions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relationships
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who received points"
    )
    incident_id = Column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Related incident (if applicable)"
    )
    
    # Transaction details
    points = Column(
        Integer,
        nullable=False,
        comment="Positive point value awarded"
    )
    reason = Column(
        SQLEnum(PointReason),
        nullable=False,
        comment="Reason for point award"
    )
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When points were awarded"
    )
    
    # Relationships
    user = relationship("User", back_populates="point_transactions")
    incident = relationship("Incident", back_populates="point_transactions")
    
    def __repr__(self):
        return f"<PointTransaction(id={self.id}, user_id={self.user_id}, points={self.points})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "incident_id": str(self.incident_id) if self.incident_id else None,
            "points": self.points,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
