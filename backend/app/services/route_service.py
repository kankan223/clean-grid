"""
Route Orchestration Service - Phase 3

Handles route optimization using ORS client with Haversine Nearest Neighbor fallback.
Integrates with database to fetch incidents, save routes, and manage stops.
"""

from __future__ import annotations

import asyncio
import json
import math
from datetime import datetime, timedelta
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.incident import Incident, IncidentStatus
from app.models.route import Route, RouteStop, RouteStatus, RouteStopStatus
from app.models.user import User
from app.services.ors_client import (
    ORSClient,
    ORSClientError,
    ORSClientConfigError,
    ORSRateLimitError,
    ORSUpstreamError,
    ORSTransportError,
)

logger = structlog.get_logger(__name__)


class RouteServiceError(Exception):
    """Base error for route service failures."""


class RouteGenerationError(RouteServiceError):
    """Failed to generate route from incidents."""


class RouteValidationError(RouteServiceError):
    """Invalid input for route generation."""


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on earth.
    
    Returns:
        Distance in meters
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    return c * r


def nearest_neighbor_route(
    incidents: list[Incident], 
    start_lat: float = 0.0, 
    start_lon: float = 0.0
) -> tuple[list[Incident], float, float]:
    """
    Generate route using Nearest Neighbor algorithm.
    
    Args:
        incidents: List of incidents to route
        start_lat: Starting latitude
        start_lon: Starting longitude
        
    Returns:
        Tuple of (ordered_incidents, total_distance_meters, total_duration_seconds)
    """
    if not incidents:
        return [], 0.0, 0.0
    
    # Copy incidents to avoid modifying original
    unvisited = incidents.copy()
    current_lat, current_lon = start_lat, start_lon
    route = []
    total_distance = 0.0
    
    while unvisited:
        # Find nearest incident
        nearest = None
        nearest_distance = float('inf')
        
        for incident in unvisited:
            if incident.location:
                incident_lat = float(incident.location.ST_Y)
                incident_lon = float(incident.location.ST_X)
                distance = haversine_distance(current_lat, current_lon, incident_lat, incident_lon)
                
                if distance < nearest_distance:
                    nearest = incident
                    nearest_distance = distance
        
        if nearest is None:
            # Fallback: take first unvisited incident
            nearest = unvisited[0]
            nearest_distance = 0
        
        # Add to route and update position
        route.append(nearest)
        unvisited.remove(nearest)
        total_distance += nearest_distance
        
        if nearest.location:
            current_lat = float(nearest.location.ST_Y)
            current_lon = float(nearest.location.ST_X)
    
    # Estimate duration (assuming average speed of 30 km/h in urban areas)
    avg_speed_mps = 8.33  # meters per second (30 km/h)
    total_duration = int(total_distance / avg_speed_mps)
    
    return route, total_distance, total_duration


async def generate_optimized_route(
    incident_ids: list[str],
    crew_id: str,
    db: AsyncSession,
    ors_client: ORSClient | None = None
) -> Route:
    """
    Generate an optimized route for the given incidents.
    
    Args:
        incident_ids: List of incident IDs to include in route
        crew_id: ID of the crew member assigned to this route
        db: Database session
        ors_client: Optional ORS client (for testing/mocking)
        
    Returns:
        Route object with stops
        
    Raises:
        RouteValidationError: Invalid input parameters
        RouteGenerationError: Failed to generate route
    """
    logger.info(
        "generate_optimized_route called",
        incident_ids=len(incident_ids),
        crew_id=crew_id,
    )
    
    # Validate inputs
    if not incident_ids:
        raise RouteValidationError("At least one incident ID is required")
    
    if not crew_id:
        raise RouteValidationError("Crew ID is required")
    
    try:
        # Fetch incidents from database
        incident_uuids = [uuid for uuid in incident_ids]
        result = await db.execute(
            select(Incident)
            .where(Incident.id.in_(incident_uuids))
            .where(Incident.status.in_([
                IncidentStatus.PENDING,
                IncidentStatus.ASSIGNED,
                IncidentStatus.IN_PROGRESS
            ]))
        )
        incidents = result.scalars().all()
        
        if len(incidents) != len(incident_ids):
            found_ids = [str(inc.id) for inc in incidents]
            missing_ids = set(incident_ids) - set(found_ids)
            raise RouteValidationError(
                f"Some incidents not found or invalid status: {missing_ids}"
            )
        
        logger.info("Fetched incidents from database", count=len(incidents))
        
        # Try ORS optimization first
        optimization_method = "ors"
        total_distance = 0
        total_duration = 0
        ordered_incidents = []
        
        if ors_client and ors_client.is_configured:
            try:
                logger.info("Attempting ORS optimization")
                ordered_incidents, total_distance, total_duration = await _optimize_with_ors(
                    incidents, ors_client
                )
                logger.info(
                    "ORS optimization successful",
                    distance=total_distance,
                    duration=total_duration,
                )
            except (ORSClientError, ORSRateLimitError, ORSUpstreamError, ORSTransportError) as e:
                logger.warning(
                    "ORS optimization failed, falling back to Haversine",
                    error=str(e),
                )
                optimization_method = "haversine_nn"
        else:
            logger.info("ORS client not configured, using Haversine NN")
            optimization_method = "haversine_nn"
        
        # Use Haversine NN as fallback
        if not ordered_incidents:
            # Use a reasonable starting point (center of incidents)
            if incidents:
                avg_lat = sum(float(inc.location.ST_Y) for inc in incidents if inc.location) / len(incidents)
                avg_lon = sum(float(inc.location.ST_X) for inc in incidents if inc.location) / len(incidents)
            else:
                avg_lat, avg_lon = 0.0, 0.0
            
            ordered_incidents, total_distance, total_duration = nearest_neighbor_route(
                incidents, avg_lat, avg_lon
            )
            optimization_method = "haversine_nn"
            logger.info(
                "Haversine NN optimization complete",
                distance=total_distance,
                duration=total_duration,
            )
        
        # Create route record
        route = Route(
            crew_id=crew_id,
            status=RouteStatus.PENDING,
            total_distance_meters=int(total_distance),
            total_duration_seconds=int(total_duration),
            optimization_method=optimization_method,
            metadata_json=json.dumps({
                "incident_count": len(incidents),
                "generated_at": datetime.utcnow().isoformat(),
                "optimization_method": optimization_method,
            }),
        )
        
        db.add(route)
        await db.flush()  # Get the route ID
        
        # Create route stops
        route_stops = []
        for order, incident in enumerate(ordered_incidents, start=1):
            # Estimate arrival time (cumulative duration from start)
            if order == 1:
                estimated_arrival = datetime.utcnow() + timedelta(minutes=15)  # Start in 15 min
            else:
                # Rough estimate: 2 minutes per stop plus travel time
                travel_time = timedelta(seconds=int(total_duration / len(ordered_incidents) * (order - 1)))
                estimated_arrival = datetime.utcnow() + timedelta(minutes=15) + travel_time + timedelta(minutes=2 * (order - 1))
            
            route_stop = RouteStop(
                route_id=route.id,
                incident_id=incident.id,
                stop_order=order,
                status=RouteStopStatus.PENDING,
                estimated_arrival=estimated_arrival,
            )
            route_stops.append(route_stop)
        
        # Bulk insert route stops
        db.add_all(route_stops)
        await db.commit()
        
        logger.info(
            "Route generated successfully",
            route_id=str(route.id),
            stops=len(route_stops),
            distance=total_distance,
            duration=total_duration,
        )
        
        # Refresh the route to get relationships
        await db.refresh(route)
        
        return route
        
    except Exception as e:
        await db.rollback()
        logger.error("Route generation failed", error=str(e))
        raise RouteGenerationError(f"Failed to generate route: {str(e)}") from e


async def _optimize_with_ors(
    incidents: list[Incident], 
    ors_client: ORSClient
) -> tuple[list[Incident], float, float]:
    """
    Attempt to optimize route using ORS optimization API.
    
    Returns:
        Tuple of (ordered_incidents, total_distance_meters, total_duration_seconds)
    """
    # Filter incidents with valid locations
    valid_incidents = [inc for inc in incidents if inc.location]
    
    if len(valid_incidents) < 2:
        # ORS needs at least 2 points for meaningful optimization
        raise ORSClientError("Need at least 2 incidents with valid locations for ORS optimization")
    
    # Prepare ORS jobs (incidents to visit)
    jobs = []
    for i, incident in enumerate(valid_incidents):
        lat = float(incident.location.ST_Y)
        lon = float(incident.location.ST_X)
        jobs.append({
            "id": str(incident.id),
            "location": [lon, lat],  # ORS expects [lon, lat]
            "service": 300,  # 5 minutes service time per incident
        })
    
    # Prepare ORS vehicles (single vehicle starting from first incident)
    first_incident = valid_incidents[0]
    start_lat = float(first_incident.location.ST_Y)
    start_lon = float(first_incident.location.ST_X)
    
    vehicles = [{
        "id": "vehicle_1",
        "start": [start_lon, start_lat],
        "end": [start_lon, start_lat],  # Return to start
        "capacity": [len(valid_incidents)],  # Can visit all incidents
        "profile": "driving-car",
    }]
    
    # Call ORS optimization
    response = await ors_client.optimize_route(jobs, vehicles)
    
    # Parse ORS response
    if not response.get("routes"):
        raise ORSUpstreamError("ORS returned no routes")
    
    ors_route = response["routes"][0]
    ors_stops = ors_route.get("steps", [])
    
    # Map ORS stops back to incidents
    incident_map = {str(inc.id): inc for inc in valid_incidents}
    ordered_incidents = []
    
    for step in ors_stops:
        if "job" in step:
            job_id = step["job"]
            if job_id in incident_map:
                ordered_incidents.append(incident_map[job_id])
    
    # Extract distance and duration from ORS response
    total_distance = ors_route.get("distance", 0)  # Usually in meters
    total_duration = ors_route.get("duration", 0)  # Usually in seconds
    
    return ordered_incidents, total_distance, total_duration


