"""
Pydantic models for commerce system (Vendors, Supply Chain, Proposals).
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from .base import GameModel


# ═══════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════

class SupplyChainEventType(str, Enum):
    """Types of supply chain events."""
    # Regular (Per Order/Weekly)
    DELIVERY_DELAY_MINOR = "delivery_delay_minor"
    DELIVERY_DELAY_MAJOR = "delivery_delay_major"
    PARTIAL_SHIPMENT = "partial_shipment"
    QUALITY_ISSUE_MINOR = "quality_issue_minor"
    QUALITY_ISSUE_MAJOR = "quality_issue_major"
    PRICE_FLUCTUATION = "price_fluctuation"
    LOST_SHIPMENT = "lost_shipment"
    
    # Major (Strategic)
    VENDOR_SHORTAGE = "vendor_shortage"
    PRICE_SPIKE = "price_spike"
    VENDOR_BANKRUPTCY = "vendor_bankruptcy"
    QUALITY_RECALL = "quality_recall"
    TRANSPORTATION_DISRUPTION = "transportation_disruption"
    REGULATORY_CHANGE = "regulatory_change"


class VendorTier(str, Enum):
    """Vendor relationship tiers."""
    NEW = "NEW"
    REGULAR = "REGULAR"
    PREFERRED = "PREFERRED"
    STRATEGIC = "STRATEGIC"


class ProposalStatus(str, Enum):
    """Status of a business proposal."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"


# ═══════════════════════════════════════════════════════════════════════
# SUPPLY CHAIN
# ═══════════════════════════════════════════════════════════════════════

class SupplyChainEvent(GameModel):
    """Event affecting the supply chain."""
    type: SupplyChainEventType
    vendor_id: Optional[str] = None  # None if global/all vendors
    description: str
    duration_weeks: int  # 0 for one-time
    effect_data: Dict[str, float]
    start_week: int
    severity: str = "medium"  # low, medium, high, critical


# ═══════════════════════════════════════════════════════════════════════
# VENDOR
# ═══════════════════════════════════════════════════════════════════════

class SupplyOffer(GameModel):
    """Special offer from a vendor."""
    item_name: str
    price: float
    description: str
    min_quantity: int = 1


class VendorProfile(GameModel):
    """Static profile data for a vendor."""
    id: str
    name: str
    slogan: str
    description: str
    base_prices: Dict[str, float]
    reliability: float = Field(ge=0.0, le=1.0)
    sustainability: float  # -5 to +5 social score impact
    min_order: int
    delivery_days: int
    payment_terms: str
    special_features: List[str]
    risks: List[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# PROPOSAL
# ═══════════════════════════════════════════════════════════════════════

class Proposal(GameModel):
    """Business proposal submitted by an agent."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str
    name: str
    category: str  # wash, dry, bundle, premium, ancillary, other
    description: str
    pricing_model: str
    resource_requirements: str
    setup_cost: float = 0.0
    status: ProposalStatus = ProposalStatus.PENDING
    evaluation: Dict[str, Any] = Field(default_factory=dict)
    created_week: int = 0
