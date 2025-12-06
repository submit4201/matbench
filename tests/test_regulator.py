import pytest
from src.engine.game_engine import GameEngine

def test_predatory_pricing_detection():
    engine = GameEngine(["agent_1"])
    
    # Set price to $1.00 (below estimated variable cost of $2.00)
    engine.submit_action("agent_1", {"type": "SET_PRICE", "amount": 1.00})
    
    # Process turn
    result = engine.process_turn()
    
    # Check for violations
    violations = result["violations"]
    predatory_violations = [v for v in violations if v["type"] == "PREDATORY_PRICING"]
    
    assert len(predatory_violations) > 0
    assert predatory_violations[0]["type"] == "PREDATORY_PRICING"
    
    # Check penalty application
    state = engine.get_state("agent_1")
    # Initial balance 100 + revenue (small) - expenses (~1500) - penalty (500)
    # Revenue will be small: 1.00 * 100 * 1.0 * 1.0 = 100
    # Expenses: 200 + (15*40*2) = 1400
    # Net: 100 - 1400 = -1300
    # Penalty: 500
    # Expected balance: 100 - 1300 - 500 = -1700
    
    # We just check if balance is significantly lower than if no penalty
    # Without penalty: -1200
    assert state.balance < -1500

def test_market_concentration_monitoring():
    # Setup: 2 agents. Agent 1 gets massive revenue, Agent 2 gets zero.
    engine = GameEngine(["agent_1", "agent_2"])
    
    # Hack history to simulate market dominance
    state1 = engine.get_state("agent_1")
    state2 = engine.get_state("agent_2")
    
    state1.history["revenue"] = [10000.0]
    state2.history["revenue"] = [100.0]
    
    # Run check manually (since process_turn overwrites history with current turn calculation)
    violations = engine.regulator.check_for_violations(engine)
    
    assert len(violations) > 0
    assert violations[0]["type"] == "MARKET_CONCENTRATION"
    assert "Monopoly Alert" in violations[0]["message"]

if __name__ == "__main__":
    test_predatory_pricing_detection()
    test_market_concentration_monitoring()
    print("All regulatory tests passed!")
