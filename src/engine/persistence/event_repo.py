from typing import List, Dict
from src.models.events.core import GameEvent

class EventRepository:
    """
    In-memory storage for GameEvents.
    Acting as a singleton or scoped store for the game session.
    """
    def __init__(self):
        # agent_id -> List[GameEvent]
        self._store: Dict[str, List[GameEvent]] = {}
        # Global tape (for debug/replay all)
        self._all_events: List[GameEvent] = []

    def save(self, event: GameEvent):
        """Append an event to the store."""
        if event.agent_id not in self._store:
            self._store[event.agent_id] = []
        
        self._store[event.agent_id].append(event)
        self._all_events.append(event)
        
    def save_batch(self, events: List[GameEvent]):
        for e in events:
            self.save(e)

    def get_history(self, agent_id: str) -> List[GameEvent]:
        """Retrieve full event history for an agent."""
        return self._store.get(agent_id, [])

    def get_all_events(self) -> List[GameEvent]:
        """Return global event tape."""
        return self._all_events
