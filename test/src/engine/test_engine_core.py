from src.engine.game_engine import GameEngine
from src.world.laundromat import LaundromatState
import logging

def test_engine_initialization(setup_test_logging):
    """Test that engine initializes with correct agents"""
    agent_ids = ["p1", "p2"]
    engine = GameEngine(agent_ids)
    
    assert len(engine.states) == 2
    assert "p1" in engine.states
    assert isinstance(engine.states["p1"], LaundromatState)
    
    # Verify logger was initialized in engine
    assert engine.logger.name == "src.engine"

def test_engine_turn_processing(setup_test_logging):
    """Test processing a daily turn"""
    engine = GameEngine(["p1"])
    initial_day = engine.time_system.current_day
    
    results = engine.process_daily_turn()
    
    # Time should advance
    assert engine.time_system.current_day != initial_day
    assert results is not None
    # If mid-week, results might be basic dict
    assert "status" in results or "p1" in results
