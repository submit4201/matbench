from typing import Dict, List, Callable, Type
from src.models.events.core import GameEvent
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """
    Central Message Bus for the Event Sourcing architecture.
    Decouples Command Handlers (Producers) from Side-Effect Handlers (Consumers).
    """
    def __init__(self):
        # Mapping: EventType (str) -> List[Callable[[GameEvent], None]]
        self._subscribers: Dict[str, List[Callable[[GameEvent], None]]] = {}
        
    def subscribe(self, event_type: str, handler: Callable[[GameEvent], None]):
        """Register a handler callback for a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed {handler.__name__} to {event_type}")

    def publish(self, event: GameEvent):
        """Publish an event to all subscribers."""
        event_type = event.event_type
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in reaction handler {handler.__name__} for {event_type}: {e}", exc_info=True)
                    # We catch exceptions so one failing reaction doesn't stop others
