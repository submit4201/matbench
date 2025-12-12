from typing import List, Dict

from .core import GameEvent


# --- Machine Events ---

class MachinePurchased(GameEvent):
    """Event for purchasing a machine."""
    type: str = "MACHINE_PURCHASED"
    machine_id: str
    model_type: str
    price: float
    location_id: str


class MachineStateChanged(GameEvent):
    """Event for machine state change (Broken/Idle/Running)."""
    type: str = "MACHINE_STATE_CHANGED"
    machine_id: str
    new_state: str
    condition: float


class MachineWearUpdated(GameEvent):
    """Event for machine wear update."""
    type: str = "MACHINE_WEAR_UPDATED"
    machine_id: str
    wear_amount: float
    current_condition: float


class CleanlinessUpdated(GameEvent):
    """Event for location cleanliness update."""
    type: str = "CLEANLINESS_UPDATED"
    new_cleanliness: float
    delta: float = 0.0
    reason: str = "weekly_decay"


class MaintenancePerformed(GameEvent):
    """Event for performing maintenance."""
    type: str = "MAINTENANCE_PERFORMED"
    location_id: str
    cost: float
    parts_used: Dict[str, int]
    machines_fixed: List[str]


# --- Staff Events ---

class StaffHired(GameEvent):
    """Event for hiring staff."""
    type: str = "STAFF_HIRED"
    staff_id: str
    role: str
    wage: float
    skill_level: float


class StaffFired(GameEvent):
    """Event for firing staff."""
    type: str = "STAFF_FIRED"
    staff_id: str
    reason: str


class StaffQuits(GameEvent):
    """Event for staff quitting."""
    type: str = "STAFF_QUITS"
    staff_id: str
    reason: str


class StaffTrained(GameEvent):
    """Event for training staff."""
    type: str = "STAFF_TRAINED"
    staff_id: str
    skill_gained: float
    cost: float


# --- Customer Events ---

class CustomerVisitStarted(GameEvent):
    """Event for a customer visit starting."""
    type: str = "CUSTOMER_VISIT_STARTED"
    customer_id: str
    laundromat_id: str
    persona_segment: str


class CustomerVisitBounced(GameEvent):
    """Event for a customer bouncing."""
    type: str = "CUSTOMER_VISIT_BOUNCED"
    customer_id: str
    laundromat_id: str
    reason: str


class CustomerComplaintFiled(GameEvent):
    """Event for a customer filing a complaint (Ticket)."""
    type: str = "CUSTOMER_COMPLAINT_FILED"
    ticket_id: str
    customer_id: str
    ticket_type: str
    description: str
    severity: int


class CustomerServiceCompleted(GameEvent):
    """Event for a successful service completion."""
    type: str = "CUSTOMER_SERVICE_COMPLETED"
    customer_id: str
    laundromat_id: str
    revenue_generated: float


class CustomerSentimentRecorded(GameEvent):
    """Event for recording customer sentiment."""
    type: str = "CUSTOMER_SENTIMENT_RECORDED"
    customer_id: str
    laundromat_id: str
    thought_text: str
    bias_delta: float


# --- Ticket Events ---

class TicketResolved(GameEvent):
    """Event for resolving a ticket."""
    type: str = "TICKET_RESOLVED"
    ticket_id: str
    resolution_method: str
    cost_incurred: float


class TicketIgnored(GameEvent):
    """Event for ignoring a ticket."""
    type: str = "TICKET_IGNORED"
    ticket_id: str


# --- R&D & Proposals ---

class ProposalSubmitted(GameEvent):
    """Event for submitting a proposal."""
    type: str = "PROPOSAL_SUBMITTED"
    proposal_id: str
    name: str
    category: str
    setup_cost: float
    description: str


class ProposalEvaluated(GameEvent):
    """Event for proposal evaluation."""
    type: str = "PROPOSAL_EVALUATED"
    proposal_id: str
    feasibility_score: float
    profitability: float
    customer_appeal: float
    reasoning: str


class ProposalApproved(GameEvent):
    """Event for proposal approval."""
    type: str = "PROPOSAL_APPROVED"
    proposal_id: str
    final_setup_cost: float
    revenue_stream_name: str


class ProposalRejected(GameEvent):
    """Event for proposal rejection."""
    type: str = "PROPOSAL_REJECTED"
    proposal_id: str
    reason: str


# --- Marketing & Location Events ---

class LocationAssigned(GameEvent):
    """Event for assigning a location."""
    type: str = "LOCATION_ASSIGNED"
    zone_id: str


class ZoneTrafficShifted(GameEvent):
    """Event for zone traffic shifts."""
    type: str = "ZONE_TRAFFIC_SHIFTED"
    zone_id: str
    new_traffic_multiplier: float
    reason: str


class MarketingCampaignStarted(GameEvent):
    """Event for starting a marketing campaign."""
    type: str = "MARKETING_CAMPAIGN_STARTED"
    campaign_type: str
    cost: float
    boost_amount: float
    duration_weeks: int


class MarketingBoostDecayed(GameEvent):
    """Event for marketing boost decay."""
    type: str = "MARKETING_BOOST_DECAYED"
    decay_amount: float
    remaining_boost: float
