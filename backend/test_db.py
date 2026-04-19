#!/usr/bin/env python3
"""
CleanGrid Database Connection Test
Verifies PostGIS connection and basic functionality
"""

import asyncio
import sys
import os
from typing import Any

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import get_db, check_db_health
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def test_database_connection():
    """
    Test database connection and PostGIS functionality
    """
    print("=== CleanGrid Database Connection Test ===")
    
    try:
        # Test basic connection health
        print("1. Testing basic database connection...")
        is_healthy = await check_db_health()
        
        if not is_healthy:
            print("   FAILED: Database connection failed")
            return False
        
        print("   SUCCESS: Database connection established")
        
        # Test PostGIS extension
        print("2. Testing PostGIS extension...")
        async for db in get_db():
            try:
                result = await db.execute(text("SELECT PostGIS_version();"))
                postgis_version = result.scalar()
                print(f"   SUCCESS: PostGIS version: {postgis_version}")
                
                # Test spatial functions
                print("3. Testing spatial functions...")
                await db.execute(text("""
                    SELECT ST_Distance(
                        ST_GeomFromText('POINT(0 0)', 4326),
                        ST_GeomFromText('POINT(1 1)', 4326)
                    );
                """))
                print("   SUCCESS: Spatial distance calculation works")
                
                # Test geometry column creation
                print("4. Testing geometry column creation...")
                await db.execute(text("""
                    DROP TABLE IF EXISTS test_spatial;
                    CREATE TABLE test_spatial (
                        id SERIAL PRIMARY KEY,
                        location GEOGRAPHY(POINT, 4326)
                    );
                    
                    INSERT INTO test_spatial (location) VALUES (
                        ST_GeomFromText('POINT(-74.0060 40.7128)', 4326)
                    );
                    
                    SELECT COUNT(*) FROM test_spatial;
                """))
                count = result.scalar()
                print(f"   SUCCESS: Test spatial table created with {count} records")
                
                # Clean up test table
                await db.execute(text("DROP TABLE IF EXISTS test_spatial;"))
                
                break
                
            except Exception as e:
                print(f"   FAILED: PostGIS test failed: {e}")
                return False
        
        print("\n=== All database tests PASSED ===")
        return True
        
    except Exception as e:
        print(f"FAILED: Database test failed with error: {e}")
        return False


async def test_redis_connection():
    """
    Test Redis connection
    """
    print("\n=== Redis Connection Test ===")
    
    try:
        from app.core.redis import get_redis, set_cache, get_cache
        
        # Test Redis connection
        redis_client: Any = await get_redis()
        
        # Test basic operations
        await redis_client.ping()
        print("1. SUCCESS: Redis ping successful")
        
        # Test cache operations
        test_key = "cleangrid:test"
        test_value = {"message": "Hello CleanGrid!"}
        
        await set_cache(test_key, test_value, ttl=60)
        print("2. SUCCESS: Redis cache set successful")
        
        retrieved_value = await get_cache(test_key)
        if retrieved_value == test_value:
            print("3. SUCCESS: Redis cache retrieval successful")
        else:
            print("3. FAILED: Redis cache retrieval mismatch")
            return False
        
        # Clean up
        await redis_client.delete(test_key)
        print("4. SUCCESS: Redis cleanup successful")
        
        print("\n=== All Redis tests PASSED ===")
        return True
        
    except Exception as e:
        print(f"FAILED: Redis test failed with error: {e}")
        return False


async def main():
    """
    Main test runner
    """
    print("CleanGrid Phase 0 Validation Tests")
    print("=" * 50)
    
    # Test database
    db_success = await test_database_connection()
    
    # Test Redis
    redis_success = await test_redis_connection()
    
    # Overall result
    print("\n" + "=" * 50)
    if db_success and redis_success:
        print("OVERALL RESULT: ALL TESTS PASSED")
        print("Database and Redis are ready for Phase 1!")
        return 0
    else:
        print("OVERALL RESULT: SOME TESTS FAILED")
        print("Please check the errors above before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
