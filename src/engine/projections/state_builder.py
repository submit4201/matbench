from typing import List
from src.models.world import LaundromatState
from src.models.events.core import GameEvent
from src.engine.projections.registry import EventRegistry

# Import handlers to ensure they are registered
from src.engine.projections import handlers  # noqa: F401

class StateBuilder:
    """
    Reconstructs LaundromatState from an event stream using the Event Registry.
    """
    
    @staticmethod
    def rebuild_state(agent_id: str, events: List[GameEvent]) -> LaundromatState:
        # Start with empty state
        state = LaundromatState(id=agent_id, name="Loading...")
        
        for event in events:
            EventRegistry.apply(state, event)
            
        return state

    @staticmethod
    def apply_event(state: LaundromatState, event: GameEvent):
        """
        Public API to apply a single event to a state (Incremental projection).
        """
        EventRegistry.apply(state, event)
