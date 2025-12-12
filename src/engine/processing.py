from typing import Dict
from src.config import settings
from src.models.world import LaundromatState
# from src.models.hierarchy import AgentState, LocationState # If we want to be specific later

def process_week_logic(state: LaundromatState, revenue: float, expenses: float):
    """
    Logic moved from LaundromatState.process_week.
    Mutates state (Agent and Location).
    """
    # Archive current state to history (Agent Data)
    state.agent.history["balance"].append(state.balance)
    state.agent.history["reputation"].append(state.reputation)
    state.agent.history["social_score"].append(state.social_score.total_score)
    state.agent.history["revenue"].append(revenue)
    state.agent.history["expenses"].append(expenses)
    state.agent.history["customers"].append(state.active_customers)
    
    # Decay marketing boost naturally over time (Location Data)
    if state.marketing_boost > 0:
        decay = settings.economy.marketing_decay_rate
        state.marketing_boost = max(0, state.marketing_boost - decay)
        
    # Machine wear and tear (Location Data)
    for machine in state.machines:
        if not machine.is_broken:
            machine.condition = max(0, machine.condition - settings.simulation.machine_wear_rate)
            machine.age_weeks += 1
            if machine.condition < settings.simulation.machine_breakdown_threshold:
                import random
                if random.random() < settings.simulation.machine_breakdown_chance:
                    machine.is_broken = True

def update_inventory_logic(state: LaundromatState, usage: Dict[str, int]):
    """
    Logic moved from LaundromatState.update_inventory_usage.
    """
    total_loads = usage.get("detergent", 0)
    
    # Update stock
    inventory = state.inventory # Accessed via property proxy
    for item, amount in usage.items():
        if item in inventory:
            inventory[item] = max(0, inventory[item] - amount)
            
    # Update burn rate (simple moving average)
    daily_usage = total_loads / 7.0
    alpha = 0.3 # Smoothing factor
    state.primary_location.avg_daily_burn_rate = (alpha * daily_usage) + ((1 - alpha) * state.primary_location.avg_daily_burn_rate)
