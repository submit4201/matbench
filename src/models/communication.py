"""
Pydantic models for enhanced social/communication system.

Includes: Alliances, Groups, Messages, and Channel types.
"""

from pydantic import Field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import uuid

from .base import GameModel


# ═══════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════

class AllianceType(str, Enum):
    """Types of business alliances."""
    NON_AGGRESSION = "non_aggression"
    PRICE_STABILITY = "price_stability"  # Borderline illegal
    JOINT_MARKETING = "joint_marketing" 
    FULL_PARTNERSHIP = "full_partnership"


class ChannelType(str, Enum):
    """Types of communication channels."""
    DM = "dm"              # Direct message - private
    GROUP = "group"        # Alliance/coalition group chat
    PUBLIC = "public"      # Public announcement - all agents see
    FORMAL = "formal"      # Formal/legal - logged for regulators
    SYSTEM = "system"      # System messages (events, notifications)


class MessageIntent(str, Enum):
    """Intent categories for messages."""
    CHAT = "chat"
    PROPOSAL = "proposal"
    COUNTER_PROPOSAL = "counter_proposal"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"
    THREAT = "threat"
    PROMISE = "promise"
    INQUIRY = "inquiry"
    ANNOUNCEMENT = "announcement"
    WARNING = "warning"
    NEGOTIATION = "negotiation"
    DILEMMA = "dilemma"
    DILEMMA_OUTCOME = "dilemma_outcome"


# ═══════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════

class Alliance(GameModel):
    """A formal alliance between agents."""
    id: str
    members: List[str]
    type: AllianceType
    start_week: int
    duration_weeks: int
    terms: str


class CommunicationGroup(GameModel):
    """A message group (alliance, coalition, etc.)."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    members: List[str] = Field(default_factory=list)  # Use List instead of Set for JSON
    owner_id: str
    created_week: int
    is_active: bool = True
    message_ids: List[str] = Field(default_factory=list)


class CommunicationMessage(GameModel):
    """
    Enhanced message with channel and visibility information.
    
    Renamed from 'Message' to avoid conflict with agent.Message.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    sender_id: str
    channel: ChannelType
    content: str
    week: int
    day: int = 1
    intent: MessageIntent = MessageIntent.CHAT
    
    # Visibility
    recipient_id: Optional[str] = None       # For DM
    group_id: Optional[str] = None           # For GROUP
    visible_to: List[str] = Field(default_factory=list)  # Use List for JSON
    
    # Metadata
    reply_to_id: Optional[str] = None        # Thread support
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Analysis (populated by Game Master)
    sentiment_score: Optional[float] = None  # -1 to 1
    honesty_estimate: Optional[float] = None # 0 to 1
    manipulation_risk: Optional[float] = None # 0 to 1
    
    # Tracking
    read_by: List[str] = Field(default_factory=list)  # Use List for JSON
    is_deleted: bool = False
