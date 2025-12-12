from __future__ import annotations
from typing import Callable, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.world import LaundromatState
    from src.models.events.core import GameEvent

# Type definition for an event handler
# Function takes (State, Event) -> None (Mutates state in place)
EventHandler = Callable[["LaundromatState", "GameEvent"], None]

class EventRegistry:
    _handlers: Dict[str, List[EventHandler]] = {}

    @classmethod
    def register(cls, event_type: str):
        """Decorator to register a function as a handler for an event type."""
        def decorator(func: EventHandler):
            if event_type not in cls._handlers:
                cls._handlers[event_type] = []
            cls._handlers[event_type].append(func)
            return func
        return decorator

    @classmethod
    def apply(cls, state: LaundromatState, event: GameEvent):
        """Finds all handlers for this event type and executes them."""
        event_type = event.type
        handlers = cls._handlers.get(event_type, [])
        
        # Also support finding by class name if type string doesn't match?
        # For now, we assume event.type matches the registered string.
        
        if not handlers:
            # Optional: Log warning for unhandled events if strict
            return

        for handler in handlers:
            handler(state, event)
