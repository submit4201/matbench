import pytest
import os
import shutil
from src.agents.llm_agent import LLMAgent
from src.agents.base_agent import Observation, Action, ActionType

def test_strategy_logging():
    # Setup
    agent = LLMAgent("test_agent", "Test Bot", llm_provider="mock")
    week = 999
    thinking = ["I need to test the logging system.", "Writing a file is a good test."]
    action = Action(ActionType.SET_PRICE, {"price": 5.0})
    
    # Clean up previous test run
    log_dir = "logs/strategy"
    log_file = f"{log_dir}/test_agent_week_{week}.md"
    if os.path.exists(log_file):
        os.remove(log_file)
        
    # Execute
    agent.log_strategy(week, thinking, action)
    
    # Verify
    assert os.path.exists(log_file), "Log file should be created"
    
    with open(log_file, "r") as f:
        content = f.read()
        
    assert "# Strategy Log - Week 999" in content
    assert "**Agent**: Test Bot" in content
    assert "I need to test the logging system." in content
    assert "#pricing" in content
    
    # Clean up
    if os.path.exists(log_file):
        os.remove(log_file)

if __name__ == "__main__":
    test_strategy_logging()
    print("Strategy log test passed!")
