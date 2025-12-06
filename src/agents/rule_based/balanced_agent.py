from src.agents.base_agent import BaseAgent, Observation, Action, ActionType

class BalancedAgent(BaseAgent):
    """Mid-range pricing, moderate risk-taking"""
    
    def __init__(self, agent_id: str, name: str = "Balanced Agent"):
        super().__init__(agent_id, name)
        self.base_price = 5.5
    
    def decide_action(self, observation: Observation) -> Action:
        my_stats = observation.my_stats
        competitors = observation.competitor_stats
        balance = my_stats.get('balance', 0)
        
        # Adjust price based on competitors
        if competitors:
            avg_competitor_price = sum(c.get('price', 5.0) for c in competitors) / len(competitors)
            # Price slightly below average
            target_price = max(4.0, avg_competitor_price * 0.95)
            
            if abs(my_stats.get('price', 5.0) - target_price) > 0.7:
                return Action(ActionType.SET_PRICE, {"price": round(target_price, 1)})
        
        # Resolve tickets with moderate priority
        tickets = my_stats.get('tickets', [])
        open_tickets = [t for t in tickets if t.get('status') == 'open']
        if len(open_tickets) > 2:  # Only if multiple tickets
            return Action(ActionType.RESOLVE_TICKET, {"ticket_id": open_tickets[0].get('id')})
        
        # Buy supplies when getting low
        inventory = my_stats.get('inventory', {})
        if inventory.get('soap', 0) < 25 and balance > 80:
            return Action(ActionType.BUY_SUPPLIES, {"item": "soap", "quantity": 30})
        
        if inventory.get('parts', 0) < 4 and balance > 150:
            return Action(ActionType.BUY_SUPPLIES, {"item": "parts", "quantity": 4})
        
        # Occasional marketing
        if balance > 300 and observation.week % 6 == 0:
            return Action(ActionType.MARKETING_CAMPAIGN, {"cost": 50})
        
        # Upgrade if affordable
        if balance > 650:
            return Action(ActionType.UPGRADE_MACHINE, {})
        
        return Action(ActionType.WAIT)
