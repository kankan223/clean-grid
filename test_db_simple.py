#!/usr/bin/env python3
"""
Simple database test for Phase 0 validation
"""

import asyncio
import sys
import os

# Add the app directory to path
sys.path.append('/app')

from app.core.database import get_db
from sqlalchemy import text

async def test_database():
    """Test database connection and PostGIS version"""
    try:
        print("=== CleanGrid Database Connection Test ===")
        
        # Test basic connection
        async for session in get_db():
            print("1. Testing basic database connection... SUCCESS")
            
            # Test PostgreSQL version
            result = await session.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL Version: {version}")
            
            # Test PostGIS extension
            result = await session.execute(text("SELECT PostGIS_full_version()"))
            postgis_version = result.fetchone()[0]
            print(f"PostGIS Version: {postgis_version}")
            
            # Test spatial type creation
            result = await session.execute(text("SELECT ST_AsText(ST_Point(0, 0))"))
            point = result.fetchone()[0]
            print(f"Spatial Point Test: {point}")
            
            print("2. PostGIS extension test... SUCCESS")
            print("3. Spatial type test... SUCCESS")
            
            break
            
        print("\n=== Database Test: PASSED ===")
        return True
        
    except Exception as e:
        print(f"FAILED: Database connection failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
