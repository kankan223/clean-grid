"""
Routes API Tests - Phase 3

Automated tests for route generation and management endpoints.
Tests both ORS optimization success and Haversine fallback paths.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.core.database import get_db
from app.models.points import User, UserRole
from app.models.incident import Incident, IncidentStatus
from app.models.route import Route, RouteStop, RouteStatus
from app.schemas.route import RouteCreate, RouteResponse
from app.services.ors_client import (
    ORSClient,
    ORSClientError,
    ORSRateLimitError,
    ORSUpstreamError,
    ORSTransportError,
)


class TestRoutesAPI:
    """Test suite for Routes API endpoints"""
    
    @pytest.fixture
    async def admin_user(self, db_session: AsyncSession):
        """Create admin user for testing"""
        admin_user = User(
            email="admin@test.com",
            display_name="Test Admin",
            role=UserRole.ADMIN,
            total_points=100,
        )
        db_session.add(admin_user)
        await db_session.commit()
        await db_session.refresh(admin_user)
        return admin_user
    
    @pytest.fixture
    async def crew_user(self, db_session: AsyncSession):
        """Create crew user for testing"""
        crew_user = User(
            email="crew@test.com",
            display_name="Test Crew",
            role=UserRole.CREW,
            total_points=50,
        )
        db_session.add(crew_user)
        await db_session.commit()
        await db_session.refresh(crew_user)
        return crew_user
    
    @pytest.fixture
    async def test_incidents(self, db_session: AsyncSession):
        """Create test incidents for routing"""
        incidents = []
        for i in range(3):
            incident = Incident(
                reporter_id=uuid4(),
                image_url=f"https://example.com/image{i}.jpg",
                location=f"SRID=4326;POINT({-74.0 + i * 0.01} {40.7 + i * 0.01})",
                address_text=f"{123 + i} Test St, New York, NY",
                status=IncidentStatus.ASSIGNED,
                severity="Medium" if i % 2 == 0 else "High",
            )
            incidents.append(incident)
            db_session.add(incident)
        
        await db_session.commit()
        for incident in incidents:
            await db_session.refresh(incident)
        return incidents
    
    @pytest.fixture
    def mock_ors_success(self):
        """Mock ORS client returning successful optimization"""
        mock_response = {
            "routes": [{
                "distance": 5420,
                "duration": 1800,
                "steps": [
                    {"job": str(inc.id)} for inc in [
                        type('Incident', (), {'id': uuid4()}) for _ in range(3)
                    ]
                ]
            }]
        }
        
        with patch('app.services.ors_client.ors_client') as mock_client:
            mock_client.optimize_route = AsyncMock(return_value=mock_response)
            mock_client.is_configured = True
            yield mock_client
    
    @pytest.fixture
    def mock_ors_failure(self):
        """Mock ORS client raising an error"""
        with patch('app.services.ors_client.ors_client') as mock_client:
            mock_client.optimize_route = AsyncMock(
                side_effect=ORSUpstreamError("ORS API error")
            )
            mock_client.is_configured = True
            yield mock_client
    
    async def test_create_route_success_ors(
        self, 
        client: AsyncClient, 
        admin_user: User, 
        test_incidents: list[Incident],
        mock_ors_success
    ):
        """Test successful route creation with ORS optimization"""
        incident_ids = [str(inc.id) for inc in test_incidents]
        
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=admin_user.id,
        )
        
        response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 201
        
        route_response = RouteResponse(**response.json())
        assert route_response.crew_id == admin_user.id
        assert route_response.status == RouteStatus.PENDING
        assert route_response.total_distance_meters == 5420
        assert route_response.total_duration_seconds == 1800
        assert route_response.optimization_method == "ors"
        assert len(route_response.stops) == 3
        
        # Verify stops are ordered
        stop_orders = [stop.stop_order for stop in route_response.stops]
        assert stop_orders == [1, 2, 3]
        
        # Verify ORS client was called
        mock_ors_success.optimize_route.assert_called_once()
    
    async def test_create_route_fallback_haversine(
        self, 
        client: AsyncClient, 
        admin_user: User, 
        test_incidents: list[Incident],
        mock_ors_failure
    ):
        """Test route creation with Haversine fallback when ORS fails"""
        incident_ids = [str(inc.id) for inc in test_incidents]
        
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=admin_user.id,
        )
        
        response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 201
        
        route_response = RouteResponse(**response.json())
        assert route_response.crew_id == admin_user.id
        assert route_response.status == RouteStatus.PENDING
        assert route_response.optimization_method == "haversine_nn"
        assert len(route_response.stops) == 3
        
        # Verify distance is calculated (not from ORS)
        assert route_response.total_distance_meters > 0
        assert route_response.total_duration_seconds > 0
    
    async def test_create_route_invalid_incidents(
        self, 
        client: AsyncClient, 
        admin_user: User
    ):
        """Test route creation with invalid incident IDs"""
        route_data = RouteCreate(
            incident_ids=[uuid4()],  # Non-existent incident
            crew_id=admin_user.id,
        )
        
        response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 400
        assert "not found or invalid status" in response.json()["detail"].lower()
    
    async def test_create_route_empty_incidents(
        self, 
        client: AsyncClient, 
        admin_user: User
    ):
        """Test route creation with empty incident list"""
        route_data = RouteCreate(
            incident_ids=[],
            crew_id=admin_user.id,
        )
        
        response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 400
        assert "at least one incident" in response.json()["detail"].lower()
    
    async def test_create_route_unauthorized(
        self, 
        client: AsyncClient, 
        admin_user: User, 
        test_incidents: list[Incident]
    ):
        """Test route creation without authentication"""
        route_data = RouteCreate(
            incident_ids=[str(inc.id) for inc in test_incidents],
            crew_id=admin_user.id,
        )
        
        response = await client.post(
            "/api/routes/",
            json=route_data.model_dump()
        )
        
        assert response.status_code == 401
    
    async def test_create_route_forbidden_citizen(
        self, 
        client: AsyncClient, 
        test_incidents: list[Incident]
    ):
        """Test route creation by citizen (should be forbidden)"""
        citizen_user = User(
            email="citizen@test.com",
            display_name="Test Citizen",
            role=UserRole.CITIZEN,
            total_points=25,
        )
        
        route_data = RouteCreate(
            incident_ids=[str(inc.id) for inc in test_incidents],
            crew_id=citizen_user.id,
        )
        
        response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer citizen_token"}
        )
        
        assert response.status_code == 403
    
    async def test_get_route_success(
        self, 
        client: AsyncClient, 
        admin_user: User, 
        test_incidents: list[Incident],
        mock_ors_success
    ):
        """Test successful route retrieval"""
        # First create a route
        incident_ids = [str(inc.id) for inc in test_incidents]
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=admin_user.id,
        )
        
        create_response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        route = RouteResponse(**create_response.json())
        
        # Now retrieve it
        response = await client.get(
            f"/api/routes/{route.id}",
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 200
        
        retrieved_route = RouteResponse(**response.json())
        assert retrieved_route.id == route.id
        assert retrieved_route.crew_id == admin_user.id
        assert len(retrieved_route.stops) == 3
    
    async def test_get_route_not_found(
        self, 
        client: AsyncClient
    ):
        """Test retrieving non-existent route"""
        fake_id = uuid4()
        
        response = await client.get(
            f"/api/routes/{fake_id}",
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_get_route_forbidden_crew_wrong_route(
        self, 
        client: AsyncClient, 
        crew_user: User, 
        admin_user: User, 
        test_incidents: list[Incident],
        mock_ors_success
    ):
        """Test crew member accessing another crew's route"""
        # Create route for admin_user
        incident_ids = [str(inc.id) for inc in test_incidents]
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=admin_user.id,
        )
        
        create_response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        route = RouteResponse(**create_response.json())
        
        # Try to access as crew_user
        response = await client.get(
            f"/api/routes/{route.id}",
            headers={"Authorization": f"Bearer crew_token"}
        )
        
        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()
    
    async def test_list_routes_admin(
        self, 
        client: AsyncClient, 
        admin_user: User, 
        test_incidents: list[Incident],
        mock_ors_success
    ):
        """Test listing routes as admin (should see all)"""
        # Create a route first
        incident_ids = [str(inc.id) for inc in test_incidents]
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=admin_user.id,
        )
        
        await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        # List routes
        response = await client.get(
            "/api/routes/",
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 200
        
        routes_list = response.json()
        assert routes_list["total"] >= 1
        assert len(routes_list["routes"]) >= 1
        assert routes_list["page"] == 1
        assert routes_list["per_page"] == 20
    
    async def test_list_routes_crew_own_routes(
        self, 
        client: AsyncClient, 
        crew_user: User, 
        test_incidents: list[Incident],
        mock_ors_success
    ):
        """Test listing routes as crew member (should see own only)"""
        # Create route for crew_user
        incident_ids = [str(inc.id) for inc in test_incidents]
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=crew_user.id,
        )
        
        await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer crew_token"}
        )
        
        # List routes as crew_user
        response = await client.get(
            "/api/routes/",
            headers={"Authorization": f"Bearer crew_token"}
        )
        
        assert response.status_code == 200
        
        routes_list = response.json()
        assert routes_list["total"] >= 1
        # Crew user should only see routes assigned to them
        for route in routes_list["routes"]:
            assert route["crew_id"] == str(crew_user.id)
    
    async def test_list_routes_forbidden_citizen(
        self, 
        client: AsyncClient
    ):
        """Test listing routes as citizen (should be forbidden)"""
        response = await client.get(
            "/api/routes/",
            headers={"Authorization": f"Bearer citizen_token"}
        )
        
        assert response.status_code == 403
        assert "cannot access routes" in response.json()["detail"].lower()
    
    async def test_update_route_status(
        self, 
        client: AsyncClient, 
        admin_user: User, 
        test_incidents: list[Incident],
        mock_ors_success
    ):
        """Test updating route status"""
        # Create a route first
        incident_ids = [str(inc.id) for inc in test_incidents]
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=admin_user.id,
        )
        
        create_response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        route = RouteResponse(**create_response.json())
        
        # Update route status
        update_data = {"status": "active", "notes": "Route started"}
        response = await client.patch(
            f"/api/routes/{route.id}",
            json=update_data,
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 200
        
        updated_route = RouteResponse(**response.json())
        assert updated_route.status == "active"
        assert updated_route.id == route.id
    
    async def test_delete_route(
        self, 
        client: AsyncClient, 
        admin_user: User, 
        test_incidents: list[Incident],
        mock_ors_success
    ):
        """Test deleting a route"""
        # Create a route first
        incident_ids = [str(inc.id) for inc in test_incidents]
        route_data = RouteCreate(
            incident_ids=incident_ids,
            crew_id=admin_user.id,
        )
        
        create_response = await client.post(
            "/api/routes/",
            json=route_data.model_dump(),
            headers={"Authorization": f"Bearer admin_token"}
        )
        route = RouteResponse(**create_response.json())
        
        # Delete the route
        response = await client.delete(
            f"/api/routes/{route.id}",
            headers={"Authorization": f"Bearer admin_token"}
        )
        
        assert response.status_code == 204
        
        # Verify route is deleted
        get_response = await client.get(
            f"/api/routes/{route.id}",
            headers={"Authorization": f"Bearer admin_token"}
        )
        assert get_response.status_code == 404
