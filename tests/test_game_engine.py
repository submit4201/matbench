import pytest
from src.engine.game_engine import GameEngine
from src.engine.time import Season, Day, WeekPhase

def test_game_engine_initialization():
    agent_ids = ["agent_1", "agent_2"]
    engine = GameEngine(agent_ids)
    
    assert len(engine.states) == 2
    assert engine.time_system.current_week == 1
    assert engine.time_system.current_season == Season.SPRING
    assert engine.time_system.current_day == Day.MONDAY

def test_state_management():
    engine = GameEngine(["agent_1"])
    state = engine.get_state("agent_1")
    
    assert state.balance == 2500.0
    assert len(state.machines) == 15 # 10 washers + 5 dryers
    assert len(state.staff) == 0

def test_turn_processing():
    engine = GameEngine(["agent_1"])
    
    # Submit an action
    action = {"type": "SET_PRICE", "amount": 6.50}
    success = engine.submit_action("agent_1", action)
    assert success is True
    
    # Process turn
    result = engine.process_turn()
    
    # Check if price updated
    state = engine.get_state("agent_1")
    assert state.price == 6.50
    
    # Check if time advanced
    assert result["week"] == 2

def test_financial_reporting():
    engine = GameEngine(["agent_1"])
    state = engine.get_state("agent_1")
    
    # Process turn
    engine.process_turn()
    
    # Check if financial report exists
    assert len(state.financial_reports) == 1
    report = state.financial_reports[0]
    
    # Verify report structure
    assert report.week == 1
    assert report.total_revenue > 0
    assert report.total_operating_expenses > 0
    assert report.net_income != 0
    
    # Verify revenue streams initialization
    assert "Standard Wash" in state.revenue_streams
    assert state.revenue_streams["Standard Wash"].unlocked is True

def test_seasonal_modifiers():
    engine = GameEngine(["agent_1"])
    # Advance to Winter (Week 19+)
    engine.time_system.current_week = 20
    
    mods = engine.time_system.get_seasonal_modifier()
    assert mods["demand"] == 1.2
    assert mods["heating_cost"] == 1.5

if __name__ == "__main__":
    # Manual run if pytest not available
    test_game_engine_initialization()
    test_state_management()
    test_turn_processing()
    test_financial_reporting()
    test_seasonal_modifiers()
    print("All tests passed!")
