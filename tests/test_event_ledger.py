"""
Test GameEventLedger

Tests for the event ledger system that tracks all game events.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.world.event_ledger import GameEventLedger, GameEvent, EventCategory


class TestGameEventLedger:
    """Tests for GameEventLedger."""
    
    def test_record_event(self):
        """Test recording a basic event."""
        ledger = GameEventLedger()
        event = ledger.record(
            category="ticket",
            entity_id="ticket_001",
            details={"severity": "high", "description": "Machine broken"},
            week=5,
            agent_id="p1"
        )
        
        assert event.category == EventCategory.TICKET
        assert event.entity_id == "ticket_001"
        assert event.week == 5
        assert event.agent_id == "p1"
        assert len(ledger.events) == 1
    
    def test_query_by_category(self):
        """Test filtering events by category."""
        ledger = GameEventLedger()
        ledger.record("ticket", "t1", {}, week=1, agent_id="p1")
        ledger.record("dilemma", "d1", {}, week=2, agent_id="p1")
        ledger.record("ticket", "t2", {}, week=3, agent_id="p1")
        
        tickets = ledger.query(category="ticket")
        assert len(tickets) == 2
        assert all(e.category == EventCategory.TICKET for e in tickets)
    
    def test_query_by_agent(self):
        """Test filtering events by agent."""
        ledger = GameEventLedger()
        ledger.record("ticket", "t1", {}, week=1, agent_id="p1")
        ledger.record("ticket", "t2", {}, week=2, agent_id="p2")
        ledger.record("ticket", "t3", {}, week=3, agent_id="p1")
        
        p1_events = ledger.query(agent_id="p1")
        assert len(p1_events) == 2
    
    def test_query_by_week_range(self):
        """Test filtering events by week range."""
        ledger = GameEventLedger()
        for week in range(1, 11):
            ledger.record("market", f"m{week}", {}, week=week, agent_id="p1")
        
        mid_weeks = ledger.query(week_start=4, week_end=7)
        assert len(mid_weeks) == 4
        assert all(4 <= e.week <= 7 for e in mid_weeks)
    
    def test_count_by_category(self):
        """Test category counting for dashboards."""
        ledger = GameEventLedger()
        ledger.record("ticket", "t1", {}, week=1, agent_id="p1")
        ledger.record("ticket", "t2", {}, week=2, agent_id="p1")
        ledger.record("dilemma", "d1", {}, week=3, agent_id="p1")
        
        counts = ledger.count_by_category()
        assert counts["ticket"] == 2
        assert counts["dilemma"] == 1
        assert counts["message"] == 0
    
    def test_export_json(self):
        """Test JSON export for API responses."""
        ledger = GameEventLedger()
        ledger.record("ticket", "t1", {"severity": "low"}, week=1, agent_id="p1")
        
        json_str = ledger.export_json()
        assert "ticket" in json_str
        assert "severity" in json_str
    
    def test_to_list(self):
        """Test serialization to list of dicts."""
        ledger = GameEventLedger()
        ledger.record("ticket", "t1", {}, week=1, agent_id="p1")
        
        events_list = ledger.to_list()
        assert isinstance(events_list, list)
        assert len(events_list) == 1
        assert "category" in events_list[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
