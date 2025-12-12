from typing import List, Optional, Dict, Any

from pydantic import Field

from .core import GameEvent


# --- Legal & Regulatory Events ---

class InvestigationOpened(GameEvent):
    """Event for when a regulatory investigation is opened."""
    type: str = "INVESTIGATION_OPENED"
    case_id: str
    violation_type: str
    evidence_strength: float


class InvestigationStageAdvanced(GameEvent):
    """Event for investigation stage progression."""
    type: str = "INVESTIGATION_STAGE_ADVANCED"
    case_id: str
    new_stage: str
    week_of_advancement: int


class RegulatoryEvidenceSubmitted(GameEvent):
    """Event for player submitting evidence."""
    type: str = "REGULATORY_EVIDENCE_SUBMITTED"
    case_id: str
    document_type: str
    compliance_cost: float


class RegulatoryFinding(GameEvent):
    """Event for final regulatory finding/verdict."""
    type: str = "REGULATORY_FINDING"
    case_id: str
    verdict: str  # Cleared, Settlement, Liable
    base_penalty: float
    social_impact: float


class AppealFiled(GameEvent):
    """Event for filing an appeal."""
    type: str = "APPEAL_FILED"
    case_id: str
    legal_cost: float


class AppealOutcome(GameEvent):
    """Event for appeal outcome."""
    type: str = "APPEAL_OUTCOME"
    case_id: str
    success: bool
    penalty_reduction: float


class RegulatoryStatusChanged(GameEvent):
    """Event for regulatory status change (e.g. watchlist)."""
    type: str = "REGULATORY_STATUS_CHANGED"
    new_status: str
    market_share: float
    reason: str


class ForcedDivestitureOrdered(GameEvent):
    """Event for forced divestiture order."""
    type: str = "FORCED_DIVESTITURE_ORDERED"
    deadline_week: int
    target_share: float


# --- Scandal Events ---

class ScandalStarted(GameEvent):
    """Event for when a scandal starts."""
    type: str = "SCANDAL_STARTED"
    scandal_type: str
    severity: float
    expiry_week: int
    description: str


class ScandalResolved(GameEvent):
    """Event for when a scandal is resolved."""
    type: str = "SCANDAL_RESOLVED"
    scandal_id: str  # Assuming we track ID, derived from type or separate
    method: str


# --- Dilemma Events ---

class DilemmaTriggered(GameEvent):
    """Event for when a dilemma is presented."""
    type: str = "DILEMMA_TRIGGERED"
    dilemma_id: str
    dilemma_type: str


class DilemmaResolved(GameEvent):
    """Event for when a dilemma is resolved."""
    type: str = "DILEMMA_RESOLVED"
    dilemma_id: str
    choice_id: str
    outcome_text: str
    effects: Dict[str, Any]


class RiskConsequenceTriggered(GameEvent):
    """Event for bad luck consequences of risky choices."""
    type: str = "RISK_CONSEQUENCE_TRIGGERED"
    dilemma_id: str
    penalty_applied: Dict[str, Any]
    description: str


# --- Relationship & Alliance Events ---

class ReputationChanged(GameEvent):
    """Event for reputation changes."""
    type: str = "REPUTATION_CHANGED"
    delta: float
    reason: str
    source_event_id: Optional[str] = None


class TrustScoreChanged(GameEvent):
    """Event for trust score changes."""
    type: str = "TRUST_SCORE_CHANGED"
    target_agent_id: str
    new_score: float
    delta: float
    reason: str


class AllianceProposed(GameEvent):
    """Event for alliance proposal."""
    type: str = "ALLIANCE_PROPOSED"
    proposal_id: str
    target_agent_id: str
    alliance_type: str
    terms: Dict[str, Any]


class AllianceFormed(GameEvent):
    """Event for alliance formation."""
    type: str = "ALLIANCE_FORMED"
    alliance_id: str
    members: List[str]
    alliance_type: str
    start_week: int
    end_week: int


class AllianceBroken(GameEvent):
    """Event for alliance breaking."""
    type: str = "ALLIANCE_BROKEN"
    alliance_id: str
    breaker_agent_id: str
    reason: str


class AllianceExpired(GameEvent):
    """Event for alliance expiration."""
    type: str = "ALLIANCE_EXPIRED"
    alliance_id: str


# --- Communication & Group Events ---

class MessageSent(GameEvent):
    """Event for sending a message."""
    type: str = "MESSAGE_SENT"
    msg_id: str
    recipients: List[str]
    channel: str
    content: str
    intent: Optional[str] = None


class MessageAnalyzed(GameEvent):
    """Event for message analysis (sentiment, etc.)."""
    type: str = "MESSAGE_ANALYZED"
    msg_id: str
    sentiment_score: float
    honesty_estimate: float
    manipulation_risk: float


class GroupCreated(GameEvent):
    """Event for group creation."""
    type: str = "GROUP_CREATED"
    group_id: str
    name: str
    owner_id: str
    initial_members: List[str]


class GroupMemberAdded(GameEvent):
    """Event for adding a member to a group."""
    type: str = "GROUP_MEMBER_ADDED"
    group_id: str
    new_member_id: str
