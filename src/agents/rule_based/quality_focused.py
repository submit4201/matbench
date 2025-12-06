from src.agents.base_agent import BaseAgent, Observation, Action, ActionType

class QualityFocusedAgent(BaseAgent):
    """High price, excellent service, always stocked"""
    
    def __init__(self, agent_id: str, name: str = "Quality Focused"):
        super().__init__(agent_id, name)
        self.premium_price = 8.0
        self.stock_target = 60  # Keep high inventory
    
    def decide_action(self, observation: Observation) -> Action:
        my_stats = observation.my_stats
        
        # Maintain premium pricing
        if abs(my_stats.get('price', 5.0) - self.premium_price) > 0.5:
            return Action(ActionType.SET_PRICE, {"price": self.premium_price})
        
        # ALWAYS resolve tickets first (quality service)
        tickets = my_stats.get('tickets', [])
        open_tickets = [t for t in tickets if t.status == 'open']
        if open_tickets:
            return Action(ActionType.RESOLVE_TICKET, {"ticket_id": open_tickets[0].id})
        
        # Keep inventory well-stocked
        inventory = my_stats.get('inventory', {})
        balance = my_stats.get('balance', 0)
        
        if inventory.get('soap', 0) < self.stock_target and balance > 100:
            buy_qty = self.stock_target - inventory.get('soap', 0)
            return Action(ActionType.BUY_SUPPLIES, {"item": "soap", "quantity": min(buy_qty, 50)})
        
        if inventory.get('softener', 0) < self.stock_target and balance > 100:
            buy_qty = self.stock_target - inventory.get('softener', 0)
            return Action(ActionType.BUY_SUPPLIES, {"item": "softener", "quantity": min(buy_qty, 50)})
        
        if inventory.get('parts', 0) < 8 and balance > 200:
            return Action(ActionType.BUY_SUPPLIES, {"item": "parts", "quantity": 5})
        
        # Invest in marketing to maintain premium image
        if balance > 400 and observation.week % 4 == 0:
            return Action(ActionType.MARKETING_CAMPAIGN, {"cost": 100})
        
        # Upgrade machines if profitable
        if balance > 800:
            return Action(ActionType.UPGRADE_MACHINE, {})
        
        return Action(ActionType.WAIT)
