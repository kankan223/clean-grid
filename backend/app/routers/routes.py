"""
Routes API Router - Phase 3

Endpoints for route generation, management, and monitoring.
Integrates ORS optimization with Haversine fallback.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import User
from app.models.route import Route, RouteStop
from app.models.incident import Incident
from app.schemas.route import (
    RouteCreate,
    RouteResponse,
    RouteUpdate,
    RouteStopResponse,
    RouteStopUpdate,
    RouteListResponse,
)
from app.services.route_service import (
    generate_optimized_route,
    RouteServiceError,
    RouteValidationError,
    RouteGenerationError,
)
from app.services.ors_client import ors_client

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.post("/", response_model=RouteResponse, status_code=201)
async def create_route(
    route_data: RouteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RouteResponse:
    """
    Generate an optimized route for the given incidents.
    
    - Uses ORS optimization when available
    - Falls back to Haversine Nearest Neighbor algorithm
    - Creates Route and RouteStop records in database
    """
    try:
        # Convert UUIDs to strings for the service
        incident_ids = [str(inc_id) for inc_id in route_data.incident_ids]
        crew_id_str = str(route_data.crew_id)
        
        # Generate the route
        route = await generate_optimized_route(
            incident_ids=incident_ids,
            crew_id=crew_id_str,
            db=db,
            ors_client=ors_client,
        )
        
        # Load relationships for response
        await db.refresh(route, ["crew", "stops.incident"])
        
        return RouteResponse.model_validate(route)
        
    except RouteValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RouteGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error generating route: {str(e)}"
        )


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RouteResponse:
    """
    Get a specific route with all stops and incident details.
    """
    try:
        # Query route with eager-loaded relationships
        result = await db.execute(
            select(Route)
            .options(
                selectinload(Route.crew),
                selectinload(Route.stops).selectinload(RouteStop.incident)
            )
            .where(Route.id == route_id)
        )
        route = result.scalar_one_or_none()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Check access permissions
        if (current_user.role != "admin" and 
            str(route.crew_id) != str(current_user.id)):
            raise HTTPException(
                status_code=403, 
                detail="Access denied: can only view own routes"
            )
        
        return RouteResponse.model_validate(route)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching route: {str(e)}"
        )


@router.get("/", response_model=RouteListResponse)
async def list_routes(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    crew_id: UUID | None = Query(None, description="Filter by crew member"),
    status: str | None = Query(None, description="Filter by route status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RouteListResponse:
    """
    List routes with filtering and pagination.
    
    - Admins can see all routes
    - Crew members can only see their own routes
    - Citizens cannot access routes
    """
    try:
        # Build base query
        query = select(Route).options(
            selectinload(Route.crew),
            selectinload(Route.stops).selectinload(RouteStop.incident)
        )
        
        # Apply filters
        if crew_id:
            query = query.where(Route.crew_id == crew_id)
        elif current_user.role == "crew":
            # Crew members can only see their own routes
            query = query.where(Route.crew_id == current_user.id)
        elif current_user.role == "citizen":
            raise HTTPException(
                status_code=403, 
                detail="Citizens cannot access routes"
            )
        
        if status:
            query = query.where(Route.status == status)
        
        # Get total count
        count_result = await db.execute(select(Route.id).select_from(query.subquery()))
        total = len(count_result.scalars().all())
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Execute query
        result = await db.execute(query)
        routes = result.scalars().all()
        
        # Convert to response models
        route_responses = [RouteResponse.model_validate(route) for route in routes]
        
        return RouteListResponse(
            routes=route_responses,
            total=total,
            page=page,
            per_page=per_page,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error listing routes: {str(e)}"
        )


@router.patch("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: UUID,
    route_update: RouteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RouteResponse:
    """
    Update route status and metadata.
    """
    try:
        # Get route
        result = await db.execute(
            select(Route)
            .options(
                selectinload(Route.crew),
                selectinload(Route.stops).selectinload(RouteStop.incident)
            )
            .where(Route.id == route_id)
        )
        route = result.scalar_one_or_none()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Update fields
        if route_update.status:
            route.status = route_update.status
        
        # Note: We could add notes field to Route model in future
        # For now, we'll store notes in metadata_json
        if route_update.notes:
            import json
            metadata = json.loads(route.metadata_json or "{}")
            metadata["last_update_notes"] = route_update.notes
            route.metadata_json = json.dumps(metadata)
        
        await db.commit()
        await db.refresh(route)
        
        return RouteResponse.model_validate(route)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating route: {str(e)}"
        )


@router.patch("/{route_id}/stops/{stop_id}", response_model=RouteStopResponse)
async def update_route_stop(
    route_id: UUID,
    stop_id: UUID,
    stop_update: RouteStopUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RouteStopResponse:
    """
    Update individual route stop status.
    
    - Crew members can update their assigned route stops
    - Admins can update any route stop
    """
    try:
        # Get route stop with relationships
        result = await db.execute(
            select(RouteStop)
            .options(
                selectinload(RouteStop.route).selectinload(Route.crew),
                selectinload(RouteStop.incident)
            )
            .where(RouteStop.id == stop_id)
            .where(RouteStop.route_id == route_id)
        )
        route_stop = result.scalar_one_or_none()
        
        if not route_stop:
            raise HTTPException(status_code=404, detail="Route stop not found")
        
        # Check permissions
        if (current_user.role not in ["admin", "crew"] or
            (current_user.role == "crew" and 
             str(route_stop.route.crew_id) != str(current_user.id))):
            raise HTTPException(
                status_code=403, 
                detail="Access denied: can only update own route stops"
            )
        
        # Update fields
        if stop_update.status:
            route_stop.status = stop_update.status
        
        if stop_update.actual_arrival:
            route_stop.actual_arrival = stop_update.actual_arrival
        
        if stop_update.notes:
            route_stop.notes = stop_update.notes
        
        await db.commit()
        await db.refresh(route_stop)
        
        return RouteStopResponse.model_validate(route_stop)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating route stop: {str(e)}"
        )


@router.delete("/{route_id}", status_code=204)
async def delete_route(
    route_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> None:
    """
    Delete a route and all its stops.
    Admin only.
    """
    try:
        # Get route
        result = await db.execute(
            select(Route).where(Route.id == route_id)
        )
        route = result.scalar_one_or_none()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Delete route (cascade will delete stops)
        await db.delete(route)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting route: {str(e)}"
        )
