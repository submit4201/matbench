from src.agents.base_agent import BaseAgent, Observation, Action, ActionType

class AggressivePricer(BaseAgent):
    """Always undercuts the lowest competitor by 10%"""
    
    def __init__(self, agent_id: str, name: str = "Aggressive Pricer"):
        super().__init__(agent_id, name)
        self.min_price = 2.0  # Don't go below this
    
    def decide_action(self, observation: Observation) -> Action:
        my_stats = observation.my_stats
        competitors = observation.competitor_stats
        
        # Find lowest competitor price
        if competitors:
            lowest_price = min(c.get('price', 5.0) for c in competitors)
            # Undercut by 10%, but not below minimum
            target_price = max(self.min_price, lowest_price * 0.9)
            
            # Only change price if significantly different
            if abs(my_stats.get('price', 5.0) - target_price) > 0.5:
                return Action(ActionType.SET_PRICE, {"price": target_price})
        
        # If we have low inventory, buy supplies
        inventory = my_stats.get('inventory', {})
        if inventory.get('soap', 0) < 20 and my_stats.get('balance', 0) > 50:
            return Action(ActionType.BUY_SUPPLIES, {"item": "soap", "quantity": 30})
        
        if inventory.get('parts', 0) < 3 and my_stats.get('balance', 0) > 100:
            return Action(ActionType.BUY_SUPPLIES, {"item": "parts", "quantity": 5})
        
        # Resolve tickets if any
        tickets = my_stats.get('tickets', [])
        open_tickets = [t for t in tickets if t.status == 'open']
        if open_tickets:
            return Action(ActionType.RESOLVE_TICKET, {"ticket_id": open_tickets[0].id})
        
        return Action(ActionType.WAIT)
