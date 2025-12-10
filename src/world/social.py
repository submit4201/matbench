"""
Proxy for backward compatibility.

All models have been migrated to src/models/social.py.
Import from there for new code.
"""

# Re-export from new location for backward compatibility
from src.models.social import (
    SocialScore,
    SocialTier,
    SOCIAL_SCORE_WEIGHTS,
    TIER_INFO_CONFIG
)

__all__ = [
    'SocialScore',
    'SocialTier',
    'SOCIAL_SCORE_WEIGHTS',
    'TIER_INFO_CONFIG'
]
