"""
Leaderboard router - CleanGrid Phase 1
Gamification and ranking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.points import User

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/")
async def get_leaderboard(
    db: AsyncSession = Depends(get_db),
    limit: int = 100
):
    """Get leaderboard rankings by points (public endpoint)"""
    
    try:
        # Get top users by points
        result = await db.execute(
            select(User)
            .order_by(desc(User.total_points))
            .limit(limit)
        )
        users = result.scalars().all()
        
        leaderboard = []
        for rank, user in enumerate(users, 1):
            leaderboard.append({
                "rank": rank,
                "user": {
                    "id": str(user.id),
                    "display_name": user.display_name,
                    "email": user.email,
                    "role": user.role.value
                },
                "total_points": user.total_points,
                "badge_tier": user.badge_tier.value if user.badge_tier else None,
                "reports_count": 0,
                "verifications_count": 0
            })
        
        return leaderboard
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch leaderboard"
        )

@router.get("/health")
async def health():
    return {"status": "leaderboard router healthy"}
