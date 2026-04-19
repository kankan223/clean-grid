"""
Route models for Phase 3: Route Optimization & Real-Time Route Management

Models:
- Route: Main route entity with spatial polyline
- RouteStop: Individual stops within a route
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry  # type: ignore
from geoalchemy2.types import Geometry as GeometryType  # type: ignore

from app.core.database import Base


class RouteStatus:
    """Route status constants"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
    @classmethod
    def all_values(cls) -> list[str]:
        return [cls.PENDING, cls.ACTIVE, cls.COMPLETED, cls.CANCELLED]


class RouteStopStatus:
    """Route stop status constants"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    
    @classmethod
    def all_values(cls) -> list[str]:
        return [cls.PENDING, cls.IN_PROGRESS, cls.COMPLETED, cls.SKIPPED]


class Route(Base):
    """Route model with spatial polyline for optimized waste collection routes"""
    __tablename__ = "routes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    
    crew_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Assigned crew member ID",
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RouteStatus.PENDING,
        comment="Route status: pending, active, completed, cancelled",
    )
    
    total_distance_meters: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        comment="Total route distance in meters",
    )
    
    total_duration_seconds: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        comment="Total route duration in seconds",
    )
    
    polyline: Mapped[str] = mapped_column(
        Geometry(
            geometry_type="LINESTRING",
            srid=4326,
            spatial_index=True,
        ),
        nullable=True,
        comment="Route polyline as PostGIS LINESTRING",
    )
    
    optimization_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="ors",
        comment="Optimization method: ors, haversine_nn",
    )
    
    metadata_json: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Additional route metadata as JSON",
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        onupdate="now()",
    )
    
    # Relationships
    crew: Mapped["User"] = relationship(
        "User",
        back_populates="assigned_routes",
        lazy="joined",
    )
    
    stops: Mapped[list["RouteStop"]] = relationship(
        "RouteStop",
        back_populates="route",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RouteStop.stop_order",
    )


class RouteStop(Base):
    """Individual stops within a route"""
    __tablename__ = "route_stops"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    
    route_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent route ID",
    )
    
    incident_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Associated incident ID",
    )
    
    stop_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Order of this stop in the route",
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RouteStopStatus.PENDING,
        comment="Stop status: pending, in_progress, completed, skipped",
    )
    
    estimated_arrival: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Estimated arrival time at this stop",
    )
    
    actual_arrival: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Actual arrival time at this stop",
    )
    
    notes: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        comment="Notes about this stop",
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        onupdate="now()",
    )
    
    # Relationships
    route: Mapped["Route"] = relationship(
        "Route",
        back_populates="stops",
        lazy="joined",
    )
    
    incident: Mapped["Incident"] = relationship(
        "Incident",
        back_populates="route_stop",
        lazy="joined",
    )
