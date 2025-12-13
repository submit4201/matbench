from typing import List, Dict, Optional
from src.models.events.core import GameEvent
from src.engine.core.event_bus import EventBus

class EventRepository:
    """
    In-memory storage for GameEvents.
    Acting as a singleton or scoped store for the game session.
    Also acts as the Publisher for the EventBus.
    """
    def __init__(self, event_bus: Optional[EventBus] = None):
        # agent_id -> List[GameEvent]
        self._store: Dict[str, List[GameEvent]] = {}
        # Global tape (for debug/replay all)
        self._all_events: List[GameEvent] = []
        self._event_bus = event_bus

    def save(self, event: GameEvent):
        """Append an event to the store and publish it."""
        if event.agent_id not in self._store:
            self._store[event.agent_id] = []
        
        self._store[event.agent_id].append(event)
        self._all_events.append(event)
        
        # Publish to Event Bus
        if self._event_bus:
            self._event_bus.publish(event)
        
    def save_batch(self, events: List[GameEvent]):
        for e in events:
            self.save(e)

    def get_history(self, agent_id: str) -> List[GameEvent]:
        """Retrieve full event history for an agent."""
        return self._store.get(agent_id, [])

    def get_all_events(self) -> List[GameEvent]:
        """Return global event tape."""
        return self._all_events
