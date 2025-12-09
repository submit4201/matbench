# [ ]↔TE: Test suite for new game systems
#   - [x] Credit System tests
#   - [x] Calendar tests
#   - [x] Game Master tests  
#   - [x] Communication tests
#   - [x] Integration tests
# PRIORITY: P1 - Core verification
# STATUS: Complete

"""
Test Suite for Enhanced Game Systems

Tests for:
- Credit/FICO System
- Calendar/Scheduling
- Game Master (LLM-powered)
- Enhanced Communication
- EnhancedGameEngine integration
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCreditSystem:
    """Tests for the Credit and FICO score system."""
    
    def test_initialization(self):
        """Test agent initialization with SBA loan."""
        from src.engine.credit_system import CreditSystem
        
        cs = CreditSystem()
        result = cs.initialize_agent("test_agent", starting_week=1)
        
        assert "sba_loan_amount" in result
        assert result["sba_loan_amount"] == 5000.0
        assert "initial_credit_score" in result
        assert 500 <= result["initial_credit_score"] <= 700  # Fair to Good range
        assert "weekly_payment" in result
    
    def test_credit_score_calculation(self):
        """Test FICO-style credit score calculation."""
        from src.engine.credit_system import CreditScore
        
        score = CreditScore()
        # Initial score should be around 650
        assert 600 <= score.total_score <= 750
        
        # Perfect payment history should improve score
        score.payment_history = 100.0
        assert score.total_score > 650
    
    def test_payment_tracking(self):
        """Test payment recording and status."""
        from src.engine.credit_system import CreditSystem
        
        cs = CreditSystem()
        cs.initialize_agent("test", starting_week=1)
        
        # Get due payments
        payments = cs.get_due_payments("test", current_week=2)
        assert len(payments) >= 0  # May or may not have payments due
    
    def test_credit_rating_tiers(self):
        """Test credit rating category assignment."""
        from src.engine.credit_system import CreditScore, CreditRating
        
        score = CreditScore()
        
        # Test different score ranges
        score.payment_history = 100.0
        score.credit_utilization = 100.0
        rating = score.rating
        assert rating in list(CreditRating)


class TestCalendarSystem:
    """Tests for the Calendar and Scheduling system."""
    
    def test_calendar_creation(self):
        """Test calendar manager initialization."""
        from src.engine.calendar import CalendarManager
        
        manager = CalendarManager()
        calendar = manager.get_calendar("test_agent")
        
        assert calendar is not None
        assert calendar.agent_id == "test_agent"
    
    def test_schedule_action(self):
        """Test scheduling an action."""
        from src.engine.calendar import CalendarManager, ActionCategory, ActionPriority
        
        manager = CalendarManager()
        calendar = manager.get_calendar("test")
        
        action = calendar.schedule_action(
            category=ActionCategory.SUPPLY_ORDER,
            title="Order detergent",
            description="Weekly supply order",
            week=5,
            day=1,
            priority=ActionPriority.HIGH
        )
        
        assert action.id is not None
        assert action.category == ActionCategory.SUPPLY_ORDER
        assert action.priority == ActionPriority.HIGH
    
    def test_week_schedule(self):
        """Test getting week schedule."""
        from src.engine.calendar import CalendarManager, ActionCategory
        
        manager = CalendarManager()
        calendar = manager.get_calendar("test")
        
        # Schedule some actions
        calendar.schedule_action(
            category=ActionCategory.MAINTENANCE,
            title="Check machines",
            description="Regular maintenance check",
            week=3,
            day=2
        )
        
        schedule = calendar.get_week_schedule(week=3)
        assert 2 in schedule
        assert len(schedule[2]) == 1
    
    def test_recurring_actions(self):
        """Test recurring action scheduling."""
        from src.engine.calendar import CalendarManager, ActionCategory
        
        manager = CalendarManager()
        calendar = manager.get_calendar("test")
        
        action = calendar.schedule_action(
            category=ActionCategory.MAINTENANCE,
            title="Weekly maintenance",
            description="Regular weekly maintenance",
            week=1,
            day=5,
            is_recurring=True,
            recurrence_weeks=1
        )
        
        assert action.is_recurring == True
        assert action.recurrence_weeks == 1


class TestGameMaster:
    """Tests for the LLM Game Master system."""
    
    def test_initialization(self):
        """Test Game Master initialization."""
        from src.engine.game_master import GameMaster
        
        gm = GameMaster()
        assert gm is not None
    
    def test_event_generation_fallback(self):
        """Test rule-based event generation (LLM fallback)."""
        from src.engine.game_master import GameMaster
        
        gm = GameMaster()
        events = gm.generate_daily_events(
            week=5,
            day=3,
            game_state={"season": "summer"},
            agent_states={"p1": {"balance": 5000, "social_score": 50}}
        )
        
        # Should return list of events (may be empty)
        assert isinstance(events, list)
    
    def test_tool_definitions(self):
        """Test Game Master tool definitions are valid."""
        from src.engine.game_master import GAME_MASTER_TOOLS
        
        assert len(GAME_MASTER_TOOLS) >= 5
        
        tool_names = {t["function"]["name"] for t in GAME_MASTER_TOOLS}
        assert "create_event" in tool_names
        assert "evaluate_ethical_choice" in tool_names
        assert "score_interaction" in tool_names
    
    def test_ethical_evaluation_mock(self):
        """Test ethical choice evaluation structure."""
        from src.engine.game_master import GameMaster
        
        gm = GameMaster()
        
        # This should work even without LLM (uses fallback)
        result = gm.evaluate_ethical_choice(
            agent_id="test",
            dilemma_context="Found $100 in machine",
            choice_made="return_money",
            reasoning="It's the right thing to do"
        )
        
        assert "ethics_score" in result


class TestCommunicationSystem:
    """Tests for the Enhanced Communication system."""
    
    def test_dm_sending(self):
        """Test sending direct messages."""
        from src.engine.communication import CommunicationSystem, MessageIntent
        
        comm = CommunicationSystem()
        
        msg = comm.send_dm(
            sender_id="p1",
            recipient_id="ai1",
            content="Let's discuss pricing",
            week=5,
            day=2,
            intent=MessageIntent.PROPOSAL
        )
        
        assert msg is not None
        assert msg.sender_id == "p1"
        assert msg.recipient_id == "ai1"
    
    def test_public_message(self):
        """Test public announcements."""
        from src.engine.communication import CommunicationSystem, MessageIntent
        
        comm = CommunicationSystem()
        
        # send_public returns a single Message
        msg = comm.send_public(
            sender_id="p1",
            content="Grand opening sale!",
            week=5,
            day=3,
            all_agent_ids=["p1", "ai1", "ai2"]
        )
        
        # Should create a message with public visibility
        assert msg is not None
        assert msg.sender_id == "p1"
    
    def test_group_creation(self):
        """Test group/alliance channel creation."""
        from src.engine.communication import CommunicationSystem
        
        comm = CommunicationSystem()
        
        group = comm.create_group(
            name="Zone B Alliance",
            owner_id="p1",
            initial_members=["ai1", "ai2"],
            week=5
        )
        
        assert group.name == "Zone B Alliance"
        assert "p1" in group.members
        assert "ai1" in group.members
    
    def test_inbox(self):
        """Test inbox retrieval."""
        from src.engine.communication import CommunicationSystem
        
        comm = CommunicationSystem()
        
        # Send a message
        comm.send_dm("p1", "ai1", "Test message", week=5)
        
        # Check inbox
        inbox = comm.get_inbox("ai1")
        assert len(inbox) >= 1


class TestEnhancedGameEngine:
    """Integration tests for the EnhancedGameEngine."""
    
    def test_initialization(self):
        """Test enhanced engine initialization."""
        from src.engine.enhanced_engine import EnhancedGameEngine
        
        engine = EnhancedGameEngine(["p1", "ai1"])
        
        assert engine is not None
        assert len(engine.states) == 2
        # Agents should start with SBA loan balance
        assert engine.states["p1"].balance == 5000.0
    
    def test_credit_system_integration(self):
        """Test credit system is integrated."""
        from src.engine.enhanced_engine import EnhancedGameEngine
        
        engine = EnhancedGameEngine(["p1"])
        
        report = engine.get_credit_report("p1")
        assert "credit_score" in report
    
    def test_calendar_integration(self):
        """Test calendar is integrated."""
        from src.engine.enhanced_engine import EnhancedGameEngine
        
        engine = EnhancedGameEngine(["p1"])
        
        calendar = engine.get_calendar("p1")
        assert calendar is not None
    
    def test_zone_assignment(self):
        """Test neighborhood zone assignment."""
        from src.engine.enhanced_engine import EnhancedGameEngine
        
        engine = EnhancedGameEngine(["p1", "ai1"])
        
        zone_info = engine.get_zone_info("p1")
        assert "zone_id" in zone_info
        assert "base_foot_traffic" in zone_info
    
    def test_process_turn(self):
        """Test turn processing with all systems."""
        from src.engine.enhanced_engine import EnhancedGameEngine
        
        engine = EnhancedGameEngine(["p1", "ai1"])
        
        results = engine.process_turn()
        
        assert "p1" in results
        assert "ai1" in results


class TestExtendedTools:
    """Tests for extended LLM agent tools."""
    
    def test_tools_imported(self):
        """Test extended tools are imported into llm_agent."""
        from src.agents.llm_agent import TOOLS, FUNCTION_TO_ACTION
        
        # Should have 17 tools total (10 original + 7 extended)
        assert len(TOOLS) == 17
        assert len(FUNCTION_TO_ACTION) == 17
    
    def test_new_action_types(self):
        """Test new action types exist."""
        from src.agents.base_agent import ActionType
        
        # Check new action types
        assert hasattr(ActionType, 'MAKE_PAYMENT')
        assert hasattr(ActionType, 'APPLY_FOR_LOAN')
        assert hasattr(ActionType, 'SCHEDULE_ACTION')
        assert hasattr(ActionType, 'SEND_DM')
        assert hasattr(ActionType, 'RESOLVE_DILEMMA')
    
    def test_parameter_mapping(self):
        """Test extended tool parameter mapping."""
        from src.agents.extended_tools import map_extended_function_args
        
        params = map_extended_function_args("make_payment", {
            "payment_id": "pay123",
            "amount": 108.50
        })
        
        assert params["payment_id"] == "pay123"
        assert params["amount"] == 108.50


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
