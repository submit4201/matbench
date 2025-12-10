# [ ]↔T: Game Event Ledger System
#   - [x] GameEvent dataclass
#   - [x] EventCategory enum
#   - [x] GameEventLedger class with record/query/export
# PRIORITY: P1 - Core architecture
# STATUS: Complete

"""
Game Event Ledger

Generic event repository for all game events (non-financial).
Extends the pattern from FinancialLedger to cover:
- Tickets (customer complaints)
- Dilemmas (ethical choices)
- Messages (communication log)
- Trades (vendor transactions)
- Regulator actions
- Game Master events

Usage:
    ledger = GameEventLedger()
    ledger.record("TICKET", "ticket_001", {"severity": "high", "description": "..."}, week=5, agent_id="p1")
    tickets = ledger.query(category="TICKET", agent_id="p1")
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid
import json


class EventCategory(Enum):
    """Categories of game events for filtering and reporting."""
    TICKET = "ticket"
    DILEMMA = "dilemma"
    MESSAGE = "message"
    TRADE = "trade"
    REGULATOR = "regulator"
    GAME_MASTER = "game_master"
    ALLIANCE = "alliance"
    MARKET = "market"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"


@dataclass
class GameEvent:
    """A single game event record (immutable after creation)."""
    category: EventCategory
    entity_id: str  # ID of the related entity (ticket_id, message_id, etc.)
    details: Dict[str, Any]  # Event-specific data
    week: int
    agent_id: Optional[str] = None  # Which agent this event affects
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "entity_id": self.entity_id,
            "details": self.details,
            "week": self.week,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class GameEventLedger:
    """
    Immutable event store for all game events.
    
    Provides:
    - record(): Add new events
    - query(): Filter events by category, agent, week range
    - export_json(): Serialize for API/dashboards
    """
    events: List[GameEvent] = field(default_factory=list)
    
    def record(
        self,
        category: str,
        entity_id: str,
        details: Dict[str, Any],
        week: int,
        agent_id: Optional[str] = None
    ) -> GameEvent:
        """Record a new game event."""
        try:
            cat = EventCategory(category.lower()) if isinstance(category, str) else category
        except ValueError:
            cat = EventCategory.SYSTEM
        
        event = GameEvent(
            category=cat,
            entity_id=entity_id,
            details=details,
            week=week,
            agent_id=agent_id
        )
        self.events.append(event)
        return event
    
    def query(
        self,
        category: Optional[str] = None,
        agent_id: Optional[str] = None,
        week_start: Optional[int] = None,
        week_end: Optional[int] = None,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[GameEvent]:
        """Query events with optional filters."""
        results = self.events
        
        if category:
            cat = EventCategory(category.lower()) if isinstance(category, str) else category
            results = [e for e in results if e.category == cat]
        
        if agent_id:
            results = [e for e in results if e.agent_id == agent_id]
        
        if week_start is not None:
            results = [e for e in results if e.week >= week_start]
        
        if week_end is not None:
            results = [e for e in results if e.week <= week_end]
        
        if entity_id:
            results = [e for e in results if e.entity_id == entity_id]
        
        # Sort by timestamp descending (newest first)
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        
        return results[:limit]
    
    def get_by_category(self, category: str) -> List[GameEvent]:
        """Convenience method to get all events of a category."""
        return self.query(category=category)
    
    def get_recent(self, count: int = 10) -> List[GameEvent]:
        """Get most recent events across all categories."""
        return self.query(limit=count)
    
    def export_json(self, **filters) -> str:
        """Export filtered events as JSON string."""
        events = self.query(**filters)
        return json.dumps([e.to_dict() for e in events], indent=2)
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Serialize all events for API responses."""
        return [e.to_dict() for e in self.events]
    
    def count_by_category(self) -> Dict[str, int]:
        """Get counts per category for dashboards."""
        counts = {}
        for cat in EventCategory:
            counts[cat.value] = len([e for e in self.events if e.category == cat])
        return counts
