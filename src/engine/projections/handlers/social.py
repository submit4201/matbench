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
    payload = event.payload if hasattr(event, "payload") else {}
    effects = getattr(event, "effects", payload.get("effects", {}))
    
    # Apply Financial Effects
    money_delta = effects.get("money", 0.0)
    if money_delta != 0:
        # We record it in ledger if we can, but projection usually just updates state.
        # But Ledger needs transaction history? 
        # Ideally FundsTransferred event handles money. 
        # If this event implies money change WITHOUT FundsTransferred, we just update balance.
        # Strict ES: We should have emitted FundsTransferred too.
        # But for "Smart Event" pattern where one event does multiple things:
        state.balance += money_delta

    # Apply Reputation Effects
    rep_delta = effects.get("reputation", 0.0)
    if rep_delta != 0:
        current_rep = state.agent.social_score.community_standing
        state.agent.social_score.community_standing = max(0, min(100, current_rep + rep_delta))

    # Apply Marketing Boost
    marketing_delta = effects.get("marketing", 0.0)
    if marketing_delta != 0:
         state.primary_location.marketing_boost = max(0.0, state.primary_location.marketing_boost + marketing_delta)


# --- Orphan Event Handlers (Future Feature Support) ---

@EventRegistry.register("INVESTIGATION_OPENED")
def apply_investigation_opened(state: LaundromatState, event: GameEvent):
    """Track new investigation."""
    payload = event.payload if hasattr(event, "payload") else {}
    investigation = {
        "id": getattr(event, "case_id", payload.get("case_id")),
        "violation": getattr(event, "violation_type", payload.get("violation_type")),
        "status": "active",
        "week": event.week
    }
    state.agent.active_investigations.append(investigation)


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
    state.agent.active_scandals.append({
        "type": getattr(event, "scandal_type", payload.get("scandal_type")),
        "severity": getattr(event, "severity", payload.get("severity", 0.5)),
        "expiry_week": getattr(event, "expiry_week", payload.get("expiry_week"))
    })


@EventRegistry.register("SCANDAL_RESOLVED")
def apply_scandal_resolved(state: LaundromatState, event: GameEvent):
    """Remove resolved scandal."""
    payload = event.payload if hasattr(event, "payload") else {}
    scandal_id = getattr(event, "scandal_id", payload.get("scandal_id"))
    state.agent.active_scandals = [s for s in state.agent.active_scandals if s.get("id") != scandal_id]


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
        state.reputation = max(0, state.reputation + penalty["reputation"])


@EventRegistry.register("TRUST_SCORE_CHANGED")
def apply_trust_score_changed(state: LaundromatState, event: GameEvent):
    """Update trust score with another agent."""
    payload = event.payload if hasattr(event, "payload") else {}
    target_id = getattr(event, "target_agent_id", payload.get("target_agent_id"))
    new_score = getattr(event, "new_score", payload.get("new_score"))
    if target_id and new_score is not None:
        state.agent.trust_scores[target_id] = new_score


@EventRegistry.register("ALLIANCE_PROPOSED")
def apply_alliance_proposed(state: LaundromatState, event: GameEvent):
    """Track alliance proposals."""
    payload = event.payload if hasattr(event, "payload") else {}
    proposal = {
        "id": getattr(event, "proposal_id", payload.get("proposal_id")),
        "target": getattr(event, "target_agent_id", payload.get("target_agent_id")),
        "type": getattr(event, "alliance_type", payload.get("alliance_type")),
        "status": "pending_approval",
        "terms": getattr(event, "terms", payload.get("terms", {}))
    }
    state.agent.alliances.append(proposal)


@EventRegistry.register("ALLIANCE_FORMED")
def apply_alliance_formed(state: LaundromatState, event: GameEvent):
    """Add alliance to state."""
    payload = event.payload if hasattr(event, "payload") else {}
    state.agent.alliances.append({
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
    state.agent.alliances = [a for a in state.agent.alliances if a.get("id") != alliance_id]


@EventRegistry.register("ALLIANCE_EXPIRED")
def apply_alliance_expired(state: LaundromatState, event: GameEvent):
    """Remove expired alliance."""
    payload = event.payload if hasattr(event, "payload") else {}
    alliance_id = getattr(event, "alliance_id", payload.get("alliance_id"))
    state.agent.alliances = [a for a in state.agent.alliances if a.get("id") != alliance_id]


@EventRegistry.register("MESSAGE_SENT")
def apply_message_sent(state: LaundromatState, event: GameEvent):
    """Log message history."""
    payload = event.payload if hasattr(event, "payload") else {}
    msg = {
        "id": getattr(event, "msg_id", payload.get("msg_id")),
        "recipients": getattr(event, "recipients", payload.get("recipients", [])),
        "content": getattr(event, "content", payload.get("content")),
        "channel": getattr(event, "channel", payload.get("channel")),
        "intent": getattr(event, "intent", payload.get("intent")),
        "week": event.week
    }
    state.agent.message_history.append(msg)


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
