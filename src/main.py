import sys
import os
import json
sys.path.append(os.getcwd())

from src.engine.core.time import TimeSystem
from src.world.laundromat import LaundromatState
from src.agents.base_agent import Observation, ActionType, Message
from src.agents.human_agent import HumanAgent
from src.agents.llm_agent import LLMAgent
from src.engine.llm_npc_factory import NPCFactory
from src.engine.processing import process_week_logic
from src.engine.game_engine import GameEngine

def main():
    print("Initializing Laundromat Tycoon...")
    
    # 1. Setup Time
    time_system = TimeSystem(total_weeks=4)
    
    # Create NPCs
    npcs = NPCFactory.from_env()
    event_manager = npcs["event_manager"]
    vendor = npcs["vendor_manager"]
    customers = npcs["customers"]
    
    # 2. Setup Laundromats & Agents
    # We map Agent ID -> Laundromat State
    laundromats = {
        "p1": LaundromatState(id="p1", name="Clean & Green", price=6.0, social_score=80),
        "p2": LaundromatState(id="p2", name="Cheap Wash", price=3.0, social_score=30),
        "p3": LaundromatState(id="p3", name="Luxury Suds", price=10.0, social_score=60)
    }
    
    # p1 is Human, p2 and p3 are LLMs (or dummy humans if disabled)
    use_llm_npcs = os.getenv("USE_LLM_NPCS", "true").lower() == "true"
    if use_llm_npcs:
        agents = [
            HumanAgent("p1", "Human Player"),
            LLMAgent("p2", "Cheap AI", model="gemini-1.5-flash"),
            LLMAgent("p3", "Luxury AI", model="gemini-1.5-flash")
        ]
    else:
        agents = [
            HumanAgent("p1", "Human Player"),
            HumanAgent("p2", "Cheap AI (Dummy)"),
            HumanAgent("p3", "Luxury AI (Dummy)")
        ]
    
    # Init Engine for Actions
    engine = GameEngine(list(laundromats.keys()))
    engine.states = laundromats
    engine.time_system = time_system # Sync time
    
    message_queue = {pid: [] for pid in laundromats}
    
    history_log = {
        "weeks": [],
        "agents": {pid: {"balance": [], "revenue": [], "visits": [], "social_score": []} for pid in laundromats}
    }

    # 4. Simulation Loop
    while time_system.advance_week():
        print(f"\n--- Week {time_system.current_week} ({time_system.current_season.value}) ---")
        history_log["weeks"].append(f"Week {time_system.current_week}")
        
        # Vendor Updates
        vendor.update_all_markets(time_system.current_week)
        
        # Events
        event_manager.update_events(time_system.current_week)
        new_events = event_manager.generate_random_events(time_system.current_week, list(laundromats.keys()))
        for e in new_events:
            print(f"!!! EVENT ({e.target_agent_id}): {e.description} !!!")
            import uuid
            message_queue[e.target_agent_id].append(Message(
                id=str(uuid.uuid4()),
                sender_id="system", recipient_id=e.target_agent_id, 
                content=f"EVENT: {e.description}", week=time_system.current_week, intent="warning"
            ))

        # Agent Decisions
        for agent in agents:
            my_state = laundromats[agent.id]
            competitors = [laundromats[pid] for pid in laundromats if pid != agent.id]
            my_messages = message_queue[agent.id]
            message_queue[agent.id] = [] # Clear
            
            active_event_descs = [e.description for e in event_manager.get_active_events(agent.id)]
            
            obs = Observation(
                week=time_system.current_week,
                day=time_system.current_day.value,
                phase=time_system.current_phase.value,
                season=time_system.current_season.value,
                my_stats={
                    "id": my_state.id, "name": my_state.name, "balance": my_state.balance,
                    "reputation": my_state.reputation, "social_score": my_state.social_score.total_score,
                    "price": my_state.price, "machines": my_state.machines,
                    "inventory": my_state.inventory, "active_customers": my_state.active_customers,
                    "tickets": my_state.tickets, "marketing_boost": my_state.marketing_boost
                },
                competitor_stats=[{
                    "id": c.id, "name": c.name, "balance": c.balance,
                    "reputation": c.reputation, "social_score": c.social_score.total_score,
                    "price": c.price
                } for c in competitors],
                messages=my_messages,
                events=active_event_descs
            )
            
            actions = agent.decide_action(obs)
            for action in actions:
                print(f"Agent {agent.name} chose: {action.type.value if hasattr(action.type, 'value') else action.type} {action.parameters}")
                
                # Apply Action via Engine
                payload = action.parameters.copy()
                payload["type"] = action.type.value if hasattr(action.type, 'value') else action.type
                success = engine._apply_action(my_state, payload)
                if not success:
                    print(f"Action failed or processed via legacy path.")

        # World Simulation (Legacy for now)
        weekly_revenue = {pid: 0.0 for pid in laundromats}
        weekly_visits = {pid: 0 for pid in laundromats}
        laundromat_list = list(laundromats.values())
        
        for customer in customers:
            choice = customer.decide_laundromat(laundromat_list)
            if choice:
                if customer.visit_laundromat(choice, time_system.current_week):
                    weekly_visits[choice.id] += 1
                    weekly_revenue[choice.id] += choice.price
                
        for pid, p in laundromats.items():
            revenue = weekly_revenue[pid]
            effects = event_manager.get_active_effects(pid)
            active_machines = max(0, len(p.machines) - effects["machine_loss"])
            expenses = 100 + (active_machines * 5)
            
            process_week_logic(p, revenue, expenses)
            print(f"{p.name}: Visits={weekly_visits[pid]}, Revenue=${revenue:.2f}, Balance=${p.balance:.2f}")

    print("\n=== GAME OVER ===")

if __name__ == "__main__":
    main()
