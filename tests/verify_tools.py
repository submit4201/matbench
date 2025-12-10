import sys
import os
from src.agents.llm_agent import LLMAgent
from src.models.agent import Observation, Action
from src.agents.base_agent import ActionType
from src.agents.tools.registry import ToolRegistry

# Mock classes
class MockLLM:
    pass

def verify_tools():
    print("Verifying Tool Registry...")
    tools = ToolRegistry.get_all_tools()
    print(f"Total tools: {len(tools)}")
    
    # Check new tools exist
    expected_tools = ["inspect_competitor", "check_market_trends", "read_news", 
                      "emergency_repair", "check_regulatory_requirements", 
                      "check_reputation_score", "inspect_public_records"]
    
    tool_names = [t["function"]["name"] for t in tools]
    for t in expected_tools:
        assert t in tool_names, f"Tool {t} not found in registry"
    
    print("Verifying LLM Agent Parsing...")
    agent = LLMAgent("agent_007", "James Bond", MockLLM())
    
    # Check parsing logic
    # Active Perception
    action = agent._parse_single_tool("inspect_competitor", {"competitor_id": "c1"})
    print(f"Parsed inspect_competitor: {action}")
    assert action.type == ActionType.INSPECT_COMPETITOR
    
    action = agent._parse_single_tool("check_market_trends", {})
    print(f"Parsed check_market_trends: {action}")
    assert action.type == ActionType.CHECK_MARKET_TRENDS
    
    action = agent._parse_single_tool("read_news", {})
    print(f"Parsed read_news: {action}")
    assert action.type == ActionType.READ_NEWS

    # Final Gaps
    action = agent._parse_single_tool("emergency_repair", {"machine_id": "m1"})
    print(f"Parsed emergency_repair: {action}")
    assert action.type == ActionType.EMERGENCY_REPAIR

    action = agent._parse_single_tool("check_regulatory_requirements", {})
    print(f"Parsed check_regulatory_requirements: {action}")
    assert action.type == ActionType.CHECK_REGULATIONS

    action = agent._parse_single_tool("check_reputation_score", {})
    print(f"Parsed check_reputation_score: {action}")
    assert action.type == ActionType.CHECK_REPUTATION

    action = agent._parse_single_tool("inspect_public_records", {"entity_id": "target"})
    print(f"Parsed inspect_public_records: {action}")
    assert action.type == ActionType.INSPECT_PUBLIC_RECORDS
    
    print("✅ All tools verified successfully!")

if __name__ == "__main__":
    verify_tools()
