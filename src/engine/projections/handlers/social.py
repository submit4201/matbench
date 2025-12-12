from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.projections.registry import EventRegistry

if TYPE_CHECKING:
    from src.models.world import LaundromatState
    from src.models.events.core import GameEvent

@EventRegistry.register("REPUTATION_UPDATED")
@EventRegistry.register("REPUTATION_CHANGED")
def apply_reputation_change(state: LaundromatState, event: GameEvent):
    payload = event.payload
    delta = getattr(event, "delta", payload.get("delta", 0))
    current_rep = state.agent.social_score.community_standing
    state.agent.social_score.community_standing = max(0, min(100, current_rep + delta))

@EventRegistry.register("TICKET_RESOLVED")
def apply_ticket_resolved(state: LaundromatState, event: GameEvent):
    # Pending detailed ticket tracking model
    pass

@EventRegistry.register("DILEMMA_RESOLVED")
def apply_dilemma_resolved(state: LaundromatState, event: GameEvent):
    # Placeholder for dilemma resolution effects if not covered by other events (like money/rep)
    pass


# --- Orphan Event Handlers (Future Feature Support) ---

@EventRegistry.register("INVESTIGATION_OPENED")
def apply_investigation_opened(state: LaundromatState, event: GameEvent):
    """Stub for regulatory investigation tracking."""
    pass


@EventRegistry.register("INVESTIGATION_STAGE_ADVANCED")
def apply_investigation_stage_advanced(state: LaundromatState, event: GameEvent):
    """Stub for investigation progression."""
    pass


@EventRegistry.register("REGULATORY_EVIDENCE_SUBMITTED")
def apply_regulatory_evidence_submitted(state: LaundromatState, event: GameEvent):
    """Stub for evidence submission."""
    pass


@EventRegistry.register("REGULATORY_FINDING")
def apply_regulatory_finding(state: LaundromatState, event: GameEvent):
    """Stub for regulatory verdict."""
    pass


@EventRegistry.register("APPEAL_FILED")
def apply_appeal_filed(state: LaundromatState, event: GameEvent):
    """Stub for appeal tracking."""
    pass


@EventRegistry.register("APPEAL_OUTCOME")
def apply_appeal_outcome(state: LaundromatState, event: GameEvent):
    """Stub for appeal result."""
    pass


@EventRegistry.register("REGULATORY_STATUS_CHANGED")
def apply_regulatory_status_changed(state: LaundromatState, event: GameEvent):
    """Stub for regulatory status."""
    pass


@EventRegistry.register("FORCED_DIVESTITURE_ORDERED")
def apply_forced_divestiture_ordered(state: LaundromatState, event: GameEvent):
    """Stub for forced divestiture."""
    pass


@EventRegistry.register("SCANDAL_STARTED")
def apply_scandal_started(state: LaundromatState, event: GameEvent):
    """Track active scandal affecting reputation."""
    payload = event.payload if hasattr(event, "payload") else {}
    # Store scandal info for reputation penalties
    if not hasattr(state, "active_scandals"):
        state.active_scandals = []
    state.active_scandals.append({
        "type": getattr(event, "scandal_type", payload.get("scandal_type")),
        "severity": getattr(event, "severity", payload.get("severity", 0.5)),
        "expiry_week": getattr(event, "expiry_week", payload.get("expiry_week"))
    })


@EventRegistry.register("SCANDAL_RESOLVED")
def apply_scandal_resolved(state: LaundromatState, event: GameEvent):
    """Remove resolved scandal."""
    payload = event.payload if hasattr(event, "payload") else {}
    scandal_id = getattr(event, "scandal_id", payload.get("scandal_id"))
    if hasattr(state, "active_scandals"):
        state.active_scandals = [s for s in state.active_scandals if s.get("id") != scandal_id]


@EventRegistry.register("DILEMMA_TRIGGERED")
def apply_dilemma_triggered(state: LaundromatState, event: GameEvent):
    """Stub for dilemma presentation."""
    pass


@EventRegistry.register("RISK_CONSEQUENCE_TRIGGERED")
def apply_risk_consequence_triggered(state: LaundromatState, event: GameEvent):
    """Apply penalties from bad luck consequences of risky dilemma choices."""
    payload = event.payload if hasattr(event, "payload") else {}
    penalty = getattr(event, "penalty_applied", payload.get("penalty_applied", {}))
    
    # Apply balance penalty if present
    if "balance" in penalty:
        state.balance += penalty["balance"]  # Negative value expected
    
    # Apply reputation penalty if present
    if "reputation" in penalty:
        if hasattr(state, "reputation"):
            state.reputation = max(0, state.reputation + penalty["reputation"])


@EventRegistry.register("TRUST_SCORE_CHANGED")
def apply_trust_score_changed(state: LaundromatState, event: GameEvent):
    """Update trust score with another agent."""
    payload = event.payload if hasattr(event, "payload") else {}
    target_id = getattr(event, "target_agent_id", payload.get("target_agent_id"))
    new_score = getattr(event, "new_score", payload.get("new_score"))
    if hasattr(state, "trust_scores") and target_id and new_score is not None:
        state.trust_scores[target_id] = new_score


@EventRegistry.register("ALLIANCE_PROPOSED")
def apply_alliance_proposed(state: LaundromatState, event: GameEvent):
    """Stub for alliance proposal."""
    pass


@EventRegistry.register("ALLIANCE_FORMED")
def apply_alliance_formed(state: LaundromatState, event: GameEvent):
    """Add alliance to state."""
    payload = event.payload if hasattr(event, "payload") else {}
    if not hasattr(state, "alliances"):
        state.alliances = []
    state.alliances.append({
        "id": getattr(event, "alliance_id", payload.get("alliance_id")),
        "members": getattr(event, "members", payload.get("members", [])),
        "type": getattr(event, "alliance_type", payload.get("alliance_type")),
        "end_week": getattr(event, "end_week", payload.get("end_week"))
    })


@EventRegistry.register("ALLIANCE_BROKEN")
def apply_alliance_broken(state: LaundromatState, event: GameEvent):
    """Remove broken alliance."""
    payload = event.payload if hasattr(event, "payload") else {}
    alliance_id = getattr(event, "alliance_id", payload.get("alliance_id"))
    if hasattr(state, "alliances"):
        state.alliances = [a for a in state.alliances if a.get("id") != alliance_id]


@EventRegistry.register("ALLIANCE_EXPIRED")
def apply_alliance_expired(state: LaundromatState, event: GameEvent):
    """Remove expired alliance."""
    payload = event.payload if hasattr(event, "payload") else {}
    alliance_id = getattr(event, "alliance_id", payload.get("alliance_id"))
    if hasattr(state, "alliances"):
        state.alliances = [a for a in state.alliances if a.get("id") != alliance_id]


@EventRegistry.register("MESSAGE_SENT")
def apply_message_sent(state: LaundromatState, event: GameEvent):
    """Stub for message tracking."""
    pass


@EventRegistry.register("MESSAGE_ANALYZED")
def apply_message_analyzed(state: LaundromatState, event: GameEvent):
    """Stub for message analysis."""
    pass


@EventRegistry.register("GROUP_CREATED")
def apply_group_created(state: LaundromatState, event: GameEvent):
    """Stub for group tracking."""
    pass


@EventRegistry.register("GROUP_MEMBER_ADDED")
def apply_group_member_added(state: LaundromatState, event: GameEvent):
    """Stub for group membership."""
    pass
