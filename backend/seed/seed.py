"""
CleanGrid Database Seed Script
Creates default admin user and initializes the database
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt
from structlog import get_logger

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User

logger = get_logger(__name__)

async def create_default_admin():
    """Create or update default admin user from environment variables"""
    
    admin_email = settings.DEFAULT_ADMIN_EMAIL
    admin_password = settings.DEFAULT_ADMIN_PASSWORD
    
    # Get database session
    async for db in get_db():
        try:
            # Check if admin user exists
            result = await db.execute(
                select(User).where(User.email == admin_email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update password if user exists
                hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
                existing_user.password_hash = hashed_password.decode('utf-8')
                existing_user.role = "admin"
                await db.commit()
                logger.info(f"Updated admin user: {admin_email}")
            else:
                # Create new admin user
                hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
                admin_user = User(
                    email=admin_email,
                    password_hash=hashed_password.decode('utf-8'),
                    display_name="Admin",
                    role="admin"
                )
                db.add(admin_user)
                await db.commit()
                await db.refresh(admin_user)
                logger.info(f"Created admin user: {admin_email}")
                
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            await db.rollback()
            raise
        
        # Exit after first iteration
        break

async def main():
    """Main seed function"""
    logger.info("Starting database seed...")
    
    try:
        await create_default_admin()
        logger.info("Database seed completed successfully!")
        
        # Print admin credentials for user
        print(f"\n{'='*50}")
        print(f"DEFAULT ADMIN CREDENTIALS:")
        print(f"Email: {settings.DEFAULT_ADMIN_EMAIL}")
        print(f"Password: {settings.DEFAULT_ADMIN_PASSWORD}")
        print(f"{'='*50}\n")
        
    except Exception as e:
        logger.error(f"Database seed failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
