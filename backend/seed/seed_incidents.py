#!/usr/bin/env python3
"""
Seed incidents for CleanGrid Phase 1 development
Creates 30-50 incidents across 5 geographic clusters
"""

import asyncio
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Point
from sqlalchemy import select

# Add the app directory to path
import sys
import os
sys.path.append('/app')

from app.core.database import AsyncSessionLocal
from app.models.incident import Incident, IncidentStatus, IncidentSeverity


# Geographic clusters around a city (example coordinates)
CLUSTERS = [
    {
        "name": "Downtown",
        "center": (40.7128, -74.0060),  # NYC Downtown
        "radius": 0.01,  # ~1km radius
        "count": 12
    },
    {
        "name": "Industrial Zone", 
        "center": (40.7282, -73.9942),
        "radius": 0.015,
        "count": 10
    },
    {
        "name": "Residential North",
        "center": (40.7589, -73.9851),
        "radius": 0.008,
        "count": 8
    },
    {
        "name": "Park Area",
        "center": (40.7829, -73.9654),
        "radius": 0.012,
        "count": 7
    },
    {
        "name": "Waterfront",
        "center": (40.7061, -74.0087),
        "radius": 0.009,
        "count": 6
    }
]

# Sample image URLs (using placeholder images)
IMAGE_URLS = [
    "https://picsum.photos/400/300?random=1",
    "https://picsum.photos/400/300?random=2", 
    "https://picsum.photos/400/300?random=3",
    "https://picsum.photos/400/300?random=4",
    "https://picsum.photos/400/300?random=5"
]

# Sample notes
NOTES = [
    "Large pile of plastic bottles near bus stop",
    "Overflowing trash can with mixed waste",
    "Scattered litter around park bench",
    "Construction debris mixed with household waste",
    "Food waste and packaging near restaurant",
    "Electronics waste dumped illegally",
    "Broken glass and plastic containers",
    "Mixed recyclables in regular trash area",
    "Garbage bags torn open by animals",
    "Industrial waste near factory entrance"
]

# Severity distribution (weighted towards more common cases)
SEVERITY_WEIGHTS = {
    IncidentSeverity.LOW: 0.5,      # 50% low severity
    IncidentSeverity.MEDIUM: 0.35,  # 35% medium severity  
    IncidentSeverity.HIGH: 0.15     # 15% high severity
}

# Status distribution
STATUS_WEIGHTS = {
    IncidentStatus.PENDING: 0.3,
    IncidentStatus.ASSIGNED: 0.2,
    IncidentStatus.IN_PROGRESS: 0.15,
    IncidentStatus.CLEANED: 0.25,
    IncidentStatus.VERIFIED: 0.1
}


def generate_random_point(center_lat_lon, radius):
    """Generate a random point within a given radius of center"""
    lat, lon = center_lat_lon
    # Generate random offset within radius
    lat_offset = random.uniform(-radius, radius)
    lon_offset = random.uniform(-radius, radius)
    return lat + lat_offset, lon + lon_offset


def weighted_choice(items_weights):
    """Choose an item based on weights"""
    items, weights = zip(*items_weights.items())
    return random.choices(items, weights=weights)[0]


async def create_incident(session: AsyncSession, cluster_info: dict) -> Incident:
    """Create a single incident with random data"""
    
    # Generate random location within cluster
    lat, lon = generate_random_point(cluster_info["center"], cluster_info["radius"])
    
    # Create PostGIS point
    location = ST_Point(lon, lat, srid=4326)
    
    # Random severity and status
    severity = weighted_choice(SEVERITY_WEIGHTS)
    status = weighted_choice(STATUS_WEIGHTS)
    
    # Generate confidence based on severity
    if severity == IncidentSeverity.HIGH:
        confidence = random.uniform(0.7, 0.95)
    elif severity == IncidentSeverity.MEDIUM:
        confidence = random.uniform(0.45, 0.7)
    else:  # LOW
        confidence = random.uniform(0.25, 0.45)
    
    # Generate priority score based on severity and status
    base_priority = {
        IncidentSeverity.HIGH: 80,
        IncidentSeverity.MEDIUM: 50,
        IncidentSeverity.LOW: 20
    }[severity]
    
    # Adjust priority based on status
    status_multiplier = {
        IncidentStatus.PENDING: 1.0,
        IncidentStatus.ASSIGNED: 0.9,
        IncidentStatus.IN_PROGRESS: 0.8,
        IncidentStatus.CLEANED: 0.3,
        IncidentStatus.VERIFIED: 0.1
    }[status]
    
    priority_score = base_priority * status_multiplier
    
    # Random timestamp within last 30 days
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    created_at = datetime.utcnow() - timedelta(
        days=days_ago, hours=hours_ago, minutes=minutes_ago
    )
    
    # Create incident
    incident = Incident(
        image_url=random.choice(IMAGE_URLS),
        location=location,
        address_text=f"{cluster_info['name']} area",
        note=random.choice(NOTES),
        waste_detected=severity != IncidentSeverity.NONE,
        confidence=confidence,
        severity=severity,
        bounding_boxes={
            "detections": [
                {
                    "label": random.choice(["bottle", "cup", "bag", "can"]),
                    "confidence": confidence,
                    "box": [random.uniform(0, 400), random.uniform(0, 300), 
                           random.uniform(0, 400), random.uniform(0, 300)]
                }
                for _ in range(random.randint(1, 3))
            ]
        } if severity != IncidentSeverity.NONE else None,
        status=status,
        priority_score=priority_score,
        is_hotspot=random.random() < 0.2,  # 20% chance of being in hotspot
        created_at=created_at,
        updated_at=created_at
    )
    
    session.add(incident)
    return incident


async def seed_database():
    """Seed the database with sample incidents"""
    print("Starting database seeding...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if incidents already exist
            result = await session.execute(select(Incident).limit(1))
            existing = result.scalar_one_or_none()
            
            if existing:
                print("Database already contains incidents. Skipping seed.")
                return
            
            # Create incidents for each cluster
            total_incidents = 0
            for cluster in CLUSTERS:
                print(f"Creating {cluster['count']} incidents for {cluster['name']} cluster...")
                
                for i in range(cluster['count']):
                    incident = await create_incident(session, cluster)
                    total_incidents += 1
                    
                    # Commit in batches of 5 to avoid memory issues
                    if total_incidents % 5 == 0:
                        await session.commit()
                        print(f"  Created {total_incidents} incidents so far...")
            
            # Final commit
            await session.commit()
            
            print(f"Successfully created {total_incidents} incidents across {len(CLUSTERS)} clusters!")
            
            # Show summary
            for cluster in CLUSTERS:
                result = await session.execute(
                    select(Incident).where(
                        Incident.address_text == f"{cluster['name']} area"
                    )
                )
                count = len(result.scalars().all())
                print(f"  {cluster['name']}: {count} incidents")
                
        except Exception as e:
            print(f"Error during seeding: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
