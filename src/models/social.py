"""
Pydantic models for social systems.

These are pure data models - business logic belongs in services/managers.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Dict, Any, List, Optional
from enum import Enum

from .base import GameModel


# ═══════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════

class SocialTier(str, Enum):
    """Social standing tiers based on total score."""
    COMMUNITY_HERO = "Community Hero"
    TRUSTED_BUSINESS = "Trusted Business"
    GOOD_STANDING = "Good Standing"
    NEUTRAL_STANDING = "Neutral Standing"
    QUESTIONABLE_REPUTATION = "Questionable Reputation"
    COMMUNITY_CONCERN = "Community Concern"
    NEIGHBORHOOD_PARIAH = "Neighborhood Pariah"


class TicketType(str, Enum):
    """Types of customer complaint tickets."""
    OUT_OF_SOAP = "out_of_soap"
    MACHINE_BROKEN = "machine_broken"
    DIRTY_FLOOR = "dirty_floor"
    LONG_WAIT = "long_wait"
    OTHER = "other"


class TicketStatus(str, Enum):
    """Status of a support ticket."""
    OPEN = "open"
    RESOLVED = "resolved"
    IGNORED = "ignored"
    EXPIRED = "expired"


# ═══════════════════════════════════════════════════════════════════════
# SOCIAL SCORE
# ═══════════════════════════════════════════════════════════════════════

# Weights as module-level constants (not business logic, just configuration)
SOCIAL_SCORE_WEIGHTS = {
    "customer_satisfaction": 0.30,
    "community_standing": 0.25,
    "ethical_conduct": 0.20,
    "employee_relations": 0.15,
    "environmental_responsibility": 0.10
}

# Tier info configuration (pure data)
TIER_INFO_CONFIG: Dict[SocialTier, Dict[str, Any]] = {
    SocialTier.COMMUNITY_HERO: {
        "badge": "⭐⭐⭐⭐⭐ Gold Badge",
        "benefits": [
            "+25% customer preference",
            "15% vendor discount",
            "Priority for grants",
            "Immunity from minor fines",
            "Free marketing promotion"
        ],
        "penalties": []
    },
    SocialTier.TRUSTED_BUSINESS: {
        "badge": "⭐⭐⭐⭐ Silver Badge",
        "benefits": [
            "+15% customer preference",
            "10% vendor discount",
            "Green energy subsidies",
            "Positive word-of-mouth"
        ],
        "penalties": []
    },
    SocialTier.GOOD_STANDING: {
        "badge": "⭐⭐ Bronze Badge",
        "benefits": [
            "+5% customer preference",
            "5% vendor discount (loyalty only)"
        ],
        "penalties": []
    },
    SocialTier.NEUTRAL_STANDING: {
        "badge": "No Badge",
        "benefits": ["Standard treatment"],
        "penalties": []
    },
    SocialTier.QUESTIONABLE_REPUTATION: {
        "badge": "⚠️ Yellow Warning",
        "benefits": [],
        "penalties": [
            "-10% customer preference",
            "No vendor credit",
            "+2% loan interest",
            "Quarterly audits"
        ]
    },
    SocialTier.COMMUNITY_CONCERN: {
        "badge": "🔶 Orange Alert",
        "benefits": [],
        "penalties": [
            "-25% customer preference",
            "Vendors refuse credit",
            "+5% loan interest",
            "Monthly audits",
            "Ineligible for grants"
        ]
    },
    SocialTier.NEIGHBORHOOD_PARIAH: {
        "badge": "🔴 Red Critical",
        "benefits": [],
        "penalties": [
            "-50% customer preference",
            "Vendors refuse service",
            "Loans called in",
            "Weekly audits",
            "Boycotts"
        ]
    }
}


class SocialScore(GameModel):
    """
    Social reputation score with five weighted components.
    
    Total score is computed from weighted components.
    Tier is derived from total score thresholds.
    """
    customer_satisfaction: float = Field(default=50.0, ge=0.0, le=100.0)
    community_standing: float = Field(default=50.0, ge=0.0, le=100.0)
    ethical_conduct: float = Field(default=50.0, ge=0.0, le=100.0)
    employee_relations: float = Field(default=50.0, ge=0.0, le=100.0)
    environmental_responsibility: float = Field(default=50.0, ge=0.0, le=100.0)
    
    @computed_field
    @property
    def total_score(self) -> float:
        """Weighted sum of all components."""
        return (
            self.customer_satisfaction * SOCIAL_SCORE_WEIGHTS["customer_satisfaction"] +
            self.community_standing * SOCIAL_SCORE_WEIGHTS["community_standing"] +
            self.ethical_conduct * SOCIAL_SCORE_WEIGHTS["ethical_conduct"] +
            self.employee_relations * SOCIAL_SCORE_WEIGHTS["employee_relations"] +
            self.environmental_responsibility * SOCIAL_SCORE_WEIGHTS["environmental_responsibility"]
        )
    
    @computed_field
    @property
    def tier(self) -> SocialTier:
        """Current social tier based on total score."""
        score = self.total_score
        if score >= 90: return SocialTier.COMMUNITY_HERO
        if score >= 75: return SocialTier.TRUSTED_BUSINESS
        if score >= 60: return SocialTier.GOOD_STANDING
        if score >= 45: return SocialTier.NEUTRAL_STANDING
        if score >= 30: return SocialTier.QUESTIONABLE_REPUTATION
        if score >= 15: return SocialTier.COMMUNITY_CONCERN
        return SocialTier.NEIGHBORHOOD_PARIAH
    
    @computed_field
    @property
    def tier_info(self) -> Dict[str, Any]:
        """Get badge, benefits, and penalties for current tier."""
        config = TIER_INFO_CONFIG.get(self.tier, {})
        return {
            "tier_name": self.tier.value,
            "badge": config.get("badge", ""),
            "benefits": config.get("benefits", []),
            "penalties": config.get("penalties", [])
        }


# ═══════════════════════════════════════════════════════════════════════
# TICKET
# ═══════════════════════════════════════════════════════════════════════

class Ticket(GameModel):
    """
    Customer complaint/support ticket.
    
    Pure data model for tracking customer issues.
    """
    id: str
    type: TicketType
    description: str
    customer_id: str
    laundromat_id: str
    created_week: int
    severity: str = Field(default="medium")
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    resolution_week: int = Field(default=-1)
