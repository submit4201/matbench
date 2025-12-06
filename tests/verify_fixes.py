
import sys
import os
sys.path.append(os.getcwd())

from src.engine.game_engine import GameEngine
from src.world.laundromat import LaundromatState
from src.agents.base_agent import BaseAgent

def test_fixes():
    print("Initializing Game Engine...")
    engine = GameEngine(agent_ids=['p1'])
    
    # Get the state created by engine
    p1 = engine.states["p1"]
    
    # Run a turn
    print("Processing Turn 1...")
    engine.process_turn()
    
    # Check customer count
    print(f"Active Customers: {p1.active_customers}")
    if p1.active_customers > 10:
        print("PASS: Customer count is significantly higher than 5.")
    else:
        print(f"FAIL: Customer count is {p1.active_customers} (Expected > 10)")
        
    # Check Revenue Persistence
    print("\nChecking Revenue Streams:")
    has_revenue = False
    for name, stream in p1.revenue_streams.items():
        print(f"  - {name}: ${stream.weekly_revenue:.2f}")
        if stream.weekly_revenue > 0:
            has_revenue = True
            
    if has_revenue:
        print("PASS: Revenue streams have populated weekly_revenue.")
    else:
        print("FAIL: All revenue streams have 0 weekly_revenue.")
        
    # Check Reputation Sync
    print(f"\nReputation: {p1.reputation}")
    print(f"Social Score: {p1.social_score.total_score}")
    if abs(p1.reputation - p1.social_score.total_score) < 0.001:
        print("PASS: Reputation is synced with Social Score.")
    else:
        print("FAIL: Reputation desync.")

if __name__ == "__main__":
    test_fixes()
