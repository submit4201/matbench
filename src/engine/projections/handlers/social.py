from src.engine.projections.registry import EventRegistry
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
