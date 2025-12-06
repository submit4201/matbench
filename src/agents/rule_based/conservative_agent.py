from src.agents.base_agent import BaseAgent, Observation, Action, ActionType

class ConservativeAgent(BaseAgent):
    """Maintains safe balance, avoids risky moves"""
    
    def __init__(self, agent_id: str, name: str = "Conservative Agent"):
        super().__init__(agent_id, name)
        self.safe_balance = 500.0  # Always keep this much
        self.target_price = 5.0
    
    def decide_action(self, observation: Observation) -> Action:
        my_stats = observation.my_stats
        balance = my_stats.get('balance', 0)
        
        # Stay at safe price
        if abs(my_stats.get('price', 5.0) - self.target_price) > 0.5:
            return Action(ActionType.SET_PRICE, {"price": self.target_price})
        
        # Only buy if we have excess balance
        if balance > (self.safe_balance + 100):
            inventory = my_stats.get('inventory', {})
            
            # Buy soap if low
            if inventory.get('soap', 0) < 30:
                return Action(ActionType.BUY_SUPPLIES, {"item": "soap", "quantity": 20})
            
            # Buy parts if low
            if inventory.get('parts', 0) < 4:
                return Action(ActionType.BUY_SUPPLIES, {"item": "parts", "quantity": 3})
        
        # Resolve tickets (safe move, improves reputation)
        tickets = my_stats.get('tickets', [])
        open_tickets = [t for t in tickets if t.status == 'open']
        if open_tickets:
            return Action(ActionType.RESOLVE_TICKET, {"ticket_id": open_tickets[0].id})
        
        # If we have LOTS of extra money, upgrade
        if balance > (self.safe_balance + 600):
            return Action(ActionType.UPGRADE_MACHINE, {})
        
        return Action(ActionType.WAIT)
