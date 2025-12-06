from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum

class SocialTier(Enum):
    COMMUNITY_HERO = "Community Hero"
    TRUSTED_BUSINESS = "Trusted Business"
    GOOD_STANDING = "Good Standing"
    NEUTRAL_STANDING = "Neutral Standing"
    QUESTIONABLE_REPUTATION = "Questionable Reputation"
    COMMUNITY_CONCERN = "Community Concern"
    NEIGHBORHOOD_PARIAH = "Neighborhood Pariah"

@dataclass
class SocialScore:
    customer_satisfaction: float = 50.0
    community_standing: float = 50.0
    ethical_conduct: float = 50.0
    employee_relations: float = 50.0
    environmental_responsibility: float = 50.0
    
    # Weights
    WEIGHTS = {
        "customer_satisfaction": 0.30,
        "community_standing": 0.25,
        "ethical_conduct": 0.20,
        "employee_relations": 0.15,
        "environmental_responsibility": 0.10
    }

    @property
    def total_score(self) -> float:
        return (
            self.customer_satisfaction * self.WEIGHTS["customer_satisfaction"] +
            self.community_standing * self.WEIGHTS["community_standing"] +
            self.ethical_conduct * self.WEIGHTS["ethical_conduct"] +
            self.employee_relations * self.WEIGHTS["employee_relations"] +
            self.environmental_responsibility * self.WEIGHTS["environmental_responsibility"]
        )

    @property
    def tier(self) -> SocialTier:
        score = self.total_score
        if score >= 90: return SocialTier.COMMUNITY_HERO
        if score >= 75: return SocialTier.TRUSTED_BUSINESS
        if score >= 60: return SocialTier.GOOD_STANDING
        if score >= 45: return SocialTier.NEUTRAL_STANDING
        if score >= 30: return SocialTier.QUESTIONABLE_REPUTATION
        if score >= 15: return SocialTier.COMMUNITY_CONCERN
        return SocialTier.NEIGHBORHOOD_PARIAH

    def update_component(self, component: str, delta: float):
        if hasattr(self, component):
            current = getattr(self, component)
            new_val = max(0.0, min(100.0, current + delta))
            setattr(self, component, new_val)

    def get_tier_info(self) -> Dict[str, Any]:
        tier = self.tier
        info = {
            "tier_name": tier.value,
            "badge": "",
            "benefits": [],
            "penalties": []
        }
        
        if tier == SocialTier.COMMUNITY_HERO:
            info["badge"] = "⭐⭐⭐⭐⭐ Gold Badge"
            info["benefits"] = [
                "+25% customer preference",
                "15% vendor discount",
                "Priority for grants",
                "Immunity from minor fines",
                "Free marketing promotion"
            ]
        elif tier == SocialTier.TRUSTED_BUSINESS:
            info["badge"] = "⭐⭐⭐⭐ Silver Badge"
            info["benefits"] = [
                "+15% customer preference",
                "10% vendor discount",
                "Green energy subsidies",
                "Positive word-of-mouth"
            ]
        elif tier == SocialTier.GOOD_STANDING:
            info["badge"] = "⭐⭐ Bronze Badge"
            info["benefits"] = [
                "+5% customer preference",
                "5% vendor discount (loyalty only)"
            ]
        elif tier == SocialTier.NEUTRAL_STANDING:
            info["badge"] = "No Badge"
            info["benefits"] = ["Standard treatment"]
        elif tier == SocialTier.QUESTIONABLE_REPUTATION:
            info["badge"] = "⚠️ Yellow Warning"
            info["penalties"] = [
                "-10% customer preference",
                "No vendor credit",
                "+2% loan interest",
                "Quarterly audits"
            ]
        elif tier == SocialTier.COMMUNITY_CONCERN:
            info["badge"] = "🔶 Orange Alert"
            info["penalties"] = [
                "-25% customer preference",
                "Vendors refuse credit",
                "+5% loan interest",
                "Monthly audits",
                "Ineligible for grants"
            ]
        elif tier == SocialTier.NEIGHBORHOOD_PARIAH:
            info["badge"] = "🔴 Red Critical"
            info["penalties"] = [
                "-50% customer preference",
                "Vendors refuse service",
                "Loans called in",
                "Weekly audits",
                "Boycotts"
            ]
            
        return info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": self.total_score,
            "components": {
                "customer_satisfaction": self.customer_satisfaction,
                "community_standing": self.community_standing,
                "ethical_conduct": self.ethical_conduct,
                "employee_relations": self.employee_relations,
                "environmental_responsibility": self.environmental_responsibility
            },
            "tier_info": self.get_tier_info()
        }
