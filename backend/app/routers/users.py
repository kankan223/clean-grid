"""
Users router - CleanGrid Phase 3
User profile and management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.points import User, PointTransaction
from app.routers.auth import verify_access_token

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verify_access_token)
):
    """Get current user profile"""
    
    try:
        # Find user by ID
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        return {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role.value,
            "total_points": user.total_points,
            "badge_tier": user.badge_tier.value if user.badge_tier else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch user profile"
        )

@router.get("/me/reports")
async def get_user_reports(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verify_access_token)
):
    """Get current user's report history"""
    
    try:
        # Find user's reports (this would need to be implemented based on your incident/report model)
        # For now, returning empty list as placeholder
        return {
            "reports": []
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch user reports"
        )
