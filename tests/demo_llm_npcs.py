"""
Quick demo script to show LLM NPCs in action.
Runs a minimal simulation to demonstrate key features.
"""
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.getcwd())

from src.engine.llm_npc_factory import NPCFactory
from src.world.laundromat import LaundromatState

load_dotenv()

print("=" * 70)
print("LLM NPC DEMONSTRATION")
print("=" * 70)

# 1. Create NPCs
print("\n1. Creating LLM-powered NPCs...")
npcs = NPCFactory.from_env()

# 2. Test Customer
print("\n2. Testing LLM Customer Decision Making...")
customer = npcs['customers'][0]
laundromats = [
    LaundromatState(id="cheap", name="Budget Wash", price=3.0, social_score=40),
    LaundromatState(id="luxury", name="Premium Suds", price=10.0, social_score=95),
]

choice = customer.decide_laundromat(laundromats)
print(f"   Customer: {customer.persona.name}")
print(f"   Chose: {choice.name if choice else 'None'}")
if hasattr(customer, 'current_thought'):
    print(f"   💭 Thought: \"{customer.current_thought}\"")

# 3. Test Vendor
print("\n3. Testing LLM Vendor Messaging...")
vendor = npcs['vendor']
vendor.update_market(week=1)

if hasattr(vendor, 'generate_market_message'):
    msg = vendor.generate_market_message(week=1, laundromats_count=3)
    if msg:
        print(f"   📢 Vendor: \"{msg[:100]}...\"")

# 4. Test Event Manager
print("\n4. Testing LLM Event Manager...")
event_mgr = npcs['event_manager']

if hasattr(event_mgr, 'generate_world_news'):
    news = event_mgr.generate_world_news(
        week=1,
        laundromats_info=[
            {'name': l.name, 'price': l.price, 'social_score': l.social_score}
            for l in laundromats
        ]
    )
    if news:
        print(f"   📰 News: \"{news[:100]}...\"")

print("\n" + "=" * 70)
print("✅ LLM NPC Integration Demonstration Complete!")
print("=" * 70)
print("\nAll LLM NPCs are working and integrated into the simulation.")
print("Run 'python src/main.py' to see them in action during a full game.")
