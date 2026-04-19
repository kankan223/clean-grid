"""
Route Schemas - Phase 3

Pydantic v2 schemas for route API endpoints.
Defines request/response models for route generation and management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class RouteCreate(BaseModel):
    """Schema for creating a new route"""
    incident_ids: list[UUID] = Field(
        ..., 
        description="List of incident IDs to include in the route",
        min_length=1,
        max_length=50
    )
    crew_id: UUID = Field(
        ..., 
        description="ID of the crew member to assign this route to"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "incident_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "550e8400-e29b-41d4-a716-446655440001"
                ],
                "crew_id": "550e8400-e29b-41d4-a716-446655440002"
            }
        }
    )


class IncidentLocation(BaseModel):
    """Incident location for route responses"""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")


class IncidentSummary(BaseModel):
    """Summary of incident for route stop responses"""
    id: UUID = Field(..., description="Incident ID")
    location: IncidentLocation = Field(..., description="Incident location")
    severity: str | None = Field(None, description="AI-derived severity")
    status: str = Field(..., description="Incident status")
    created_at: datetime = Field(..., description="When incident was reported")
    address_text: str | None = Field(None, description="Geocoded address")


class RouteStopResponse(BaseModel):
    """Route stop response schema"""
    id: UUID = Field(..., description="Route stop ID")
    incident_id: UUID = Field(..., description="Associated incident ID")
    stop_order: int = Field(..., description="Order in the route")
    status: str = Field(..., description="Stop status")
    estimated_arrival: datetime | None = Field(
        None, 
        description="Estimated arrival time"
    )
    actual_arrival: datetime | None = Field(
        None, 
        description="Actual arrival time"
    )
    notes: str | None = Field(None, description="Notes about this stop")
    incident: IncidentSummary = Field(..., description="Incident details")
    created_at: datetime = Field(..., description="When stop was created")
    updated_at: datetime = Field(..., description="When stop was last updated")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "incident_id": "550e8400-e29b-41d4-a716-446655440000",
                "stop_order": 1,
                "status": "pending",
                "estimated_arrival": "2024-01-15T10:30:00Z",
                "actual_arrival": None,
                "notes": None,
                "incident": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "location": {"lat": 40.7128, "lon": -74.0060},
                    "severity": "Medium",
                    "status": "Assigned",
                    "created_at": "2024-01-15T09:00:00Z",
                    "address_text": "123 Main St, New York, NY"
                },
                "created_at": "2024-01-15T09:15:00Z",
                "updated_at": "2024-01-15T09:15:00Z"
            }
        }
    )


class CrewSummary(BaseModel):
    """Summary of crew member for route responses"""
    id: UUID = Field(..., description="Crew member ID")
    email: str = Field(..., description="Crew member email")
    display_name: str = Field(..., description="Crew member display name")
    role: str = Field(..., description="Crew member role")


class RouteResponse(BaseModel):
    """Route response schema with full details"""
    id: UUID = Field(..., description="Route ID")
    crew_id: UUID = Field(..., description="Assigned crew member ID")
    crew: CrewSummary = Field(..., description="Crew member details")
    status: str = Field(..., description="Route status")
    total_distance_meters: int = Field(..., description="Total distance in meters")
    total_duration_seconds: int = Field(..., description="Total duration in seconds")
    optimization_method: str = Field(..., description="Optimization method used")
    polyline: str | None = Field(None, description="Route polyline as GeoJSON")
    metadata_json: str | None = Field(None, description="Additional route metadata")
    stops: list[RouteStopResponse] = Field(..., description="Route stops")
    created_at: datetime = Field(..., description="When route was created")
    updated_at: datetime = Field(..., description="When route was last updated")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "crew_id": "550e8400-e29b-41d4-a716-446655440002",
                "crew": {
                    "id": "550e8400-e29b-41d4-a716-446655440002",
                    "email": "crew@cleangrid.io",
                    "display_name": "John Crew",
                    "role": "crew"
                },
                "status": "pending",
                "total_distance_meters": 5420,
                "total_duration_seconds": 1800,
                "optimization_method": "ors",
                "polyline": None,
                "metadata_json": '{"incident_count": 5, "generated_at": "2024-01-15T09:30:00Z"}',
                "stops": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "incident_id": "550e8400-e29b-41d4-a716-446655440000",
                        "stop_order": 1,
                        "status": "pending",
                        "estimated_arrival": "2024-01-15T10:30:00Z",
                        "actual_arrival": None,
                        "notes": None,
                        "incident": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "location": {"lat": 40.7128, "lon": -74.0060},
                            "severity": "Medium",
                            "status": "Assigned",
                            "created_at": "2024-01-15T09:00:00Z",
                            "address_text": "123 Main St, New York, NY"
                        },
                        "created_at": "2024-01-15T09:15:00Z",
                        "updated_at": "2024-01-15T09:15:00Z"
                    }
                ],
                "created_at": "2024-01-15T09:30:00Z",
                "updated_at": "2024-01-15T09:30:00Z"
            }
        }
    )


class RouteListResponse(BaseModel):
    """Schema for listing multiple routes"""
    routes: list[RouteResponse] = Field(..., description="List of routes")
    total: int = Field(..., description="Total number of routes")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "routes": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            }
        }
    )


class RouteUpdate(BaseModel):
    """Schema for updating route status"""
    status: str = Field(..., description="New route status")
    notes: str | None = Field(None, description="Optional notes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "active",
                "notes": "Route started"
            }
        }
    )


class RouteStopUpdate(BaseModel):
    """Schema for updating route stop status"""
    status: str = Field(..., description="New stop status")
    actual_arrival: datetime | None = Field(
        None, 
        description="Actual arrival time (when status changes to completed)"
    )
    notes: str | None = Field(None, description="Optional notes")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "actual_arrival": "2024-01-15T10:45:00Z",
                "notes": "Waste collected successfully"
            }
        }
    )
