from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.projections.registry import EventRegistry

if TYPE_CHECKING:
    from src.models.world import LaundromatState
    from src.models.events.core import GameEvent

@EventRegistry.register("AGENT_CREATED")
def apply_agent_created(state: LaundromatState, event: GameEvent):
    payload = event.payload
    state.name = getattr(event, "name", payload.get("name", state.name))
    if state.agent:
        state.agent.name = getattr(event, "name", payload.get("name", state.agent.name))
