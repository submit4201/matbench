"""Quick test of baseline agents"""
import sys
sys.path.append(".")

from src.agents.rule_based import AggressivePricer, ConservativeAgent, QualityFocusedAgent
from src.agents.base_agent import Observation

# Test agent creation
print("Testing agent creation...")
agent1 = AggressivePricer("test1")
agent2 = ConservativeAgent("test2")
agent3 = QualityFocusedAgent("test3")

print(f"✓ Created {agent1.name}")
print(f"✓ Created {agent2.name}")
print(f"✓ Created {agent3.name}")

# Test decision making with mock observation
print("\nTesting decision making...")
mock_obs = Observation(
    week=1,
    season="Spring",
    my_stats={
        "balance": 100,
        "price": 5.0,
        "inventory": {"soap": 50, "softener": 50, "parts": 5},
        "tickets": [],
        "machines": 4
    },
    competitor_stats=[
        {"price": 4.0},
        {"price": 6.0}
    ],
    messages=[],
    events=[]
)

action1 = agent1.decide_action(mock_obs)
action2 = agent2.decide_action(mock_obs)
action3 = agent3.decide_action(mock_obs)

print(f"✓ {agent1.name} decided: {action1.type.name}")
print(f"✓ {agent2.name} decided: {action2.type.name}")
print(f"✓ {agent3.name} decided: {action3.type.name}")

print("\n✅ All baseline agents working correctly!")
