"""
User model import - CleanGrid Phase 2
Import User from points module to avoid duplication
"""

# Import User model from points module
from app.models.points import User

# Re-export for convenience
__all__ = ["User"]
