from typing import List, Dict, Any, Optional
from pydantic import model_validator
from src.config import settings
from src.engine.finance.models import FinancialLedger, RevenueStream, Loan, Bill, FinancialReport, TransactionCategory
from src.models.base import GameModel

# Import from hierarchy to maintain compatibility and use new definitions
from src.models.hierarchy import (
    Machine, StaffMember, Building, 
    AgentState, LocationState, WorldState
)
from src.models.social import SocialScore

class LaundromatState(GameModel):
    """
    DEPRECATED: This class is being replaced by AgentState and LocationState.
    It currently acts as a compatibility layer or 'Session State' holding both.
    Methods have been removed to enforce pure data separation.
    """
    id: str
    name: str # Agent Name? Or Laundromat Name?
    
    # Composition
    agent: Optional[AgentState] = None
    primary_location: Optional[LocationState] = None
    
    @model_validator(mode='before')
    @classmethod
    def compat_mapper(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Extract basic ID/Name
            uid = data.get('id')
            name = data.get('name')
            
            # Agent Init
            if data.get('agent') is None and uid:
                # Handle social_score int -> SocialScore obj
                ss = data.get('social_score')
                ss_obj = None
                if isinstance(ss, (int, float)):
                    ss_obj = SocialScore(community_standing=float(ss))
                elif isinstance(ss, SocialScore):
                    ss_obj = ss
                
                agent_data = {'id': uid, 'name': name}
                if ss_obj:
                    agent_data['social_score'] = ss_obj
                    
                data['agent'] = AgentState(**agent_data)
                
            # Location Init
            if data.get('primary_location') is None and uid:
                loc_data = {'id': f"loc-{uid}", 'name': f"{name} HQ", 'agent_id': uid}
                if 'price' in data:
                    loc_data['price'] = data['price']
                if 'inventory' in data:
                    loc_data['inventory'] = data['inventory']
                if 'machines' in data:
                    # Ensure machines are handled. If list of objs, pass directly.
                    # If Main passes list of Machine, it works.
                    loc_data['machines'] = data['machines']
                
                data['primary_location'] = LocationState(**loc_data)
        return data

    def model_post_init(self, __context):
        # Initialize sub-states if empty (double safe)
        if self.agent is None:
             self.agent = AgentState(id=self.id, name=self.name)
            
        if self.primary_location is None:
            self.primary_location = LocationState(id=f"loc-{self.id}", name=f"{self.name} - HQ", agent_id=self.id)
            
            # Initialize default assets in primary location
            if not self.primary_location.machines:
                for i in range(10):
                    self.primary_location.machines.append(Machine(id=f"W{i}", type="standard_washer", condition=0.80))
                for i in range(5):
                    self.primary_location.machines.append(Machine(id=f"D{i}", type="standard_dryer", condition=0.80))
            
            if not self.primary_location.buildings:
                default_building = Building(
                    id=f"HQ-{self.id}",
                    name=f"{self.name} Headquarters",
                    type="storefront",
                    condition=1.0,
                    capacity_machines=20,
                    location_multiplier=1.0
                )
                self.primary_location.buildings.append(default_building)
        
        # Seed capital
        if not self.agent.ledger.transactions:
             self.agent.ledger.add(settings.economy.initial_balance, TransactionCategory.CAPITAL, "Initial Capital", week=0)
             
    # --- Proxy Properties for Backward Compatibility ---
    
    @property
    def machines(self) -> List[Machine]:
        return self.primary_location.machines
    
    @machines.setter
    def machines(self, value):
        self.primary_location.machines = value
        
    @property
    def inventory(self) -> Dict[str, int]:
        return self.primary_location.inventory
        
    @property
    def balance(self) -> float:
        return self.agent.balance
        
    @balance.setter
    def balance(self, value):
        # Direct setter supported for compat, though logic removed
        # Ideally we use an action to update balance.
        current = self.agent.ledger.balance
        diff = value - current
        if abs(diff) > 0.001:
            self.agent.ledger.add(diff, TransactionCategory.ADJUSTMENT, "Manual Balance Adjustment", week=0)

    @property
    def social_score(self):
        return self.agent.social_score
        
    @property
    def reputation(self) -> float:
        return self.agent.reputation
        
    @reputation.setter
    def reputation(self, value):
        self.agent.reputation = value

    @property
    def price(self) -> float:
        return self.primary_location.price
        
    @price.setter
    def price(self, value):
        self.primary_location.price = value
        
    @property
    def active_customers(self) -> int:
        return self.primary_location.active_customers
        
    @active_customers.setter
    def active_customers(self, value):
        self.primary_location.active_customers = value

    @property
    def marketing_boost(self) -> float:
        return self.primary_location.marketing_boost
        
    @marketing_boost.setter
    def marketing_boost(self, value):
        self.primary_location.marketing_boost = value

    @property
    def tickets(self):
        return self.primary_location.tickets
        
    @property
    def revenue_streams(self) -> Dict[str, RevenueStream]:
        return self.primary_location.revenue_streams

    # --- REMOVED METHODS ---
    # update_reputation, update_social_score, update_inventory_usage, process_week
    # These must be handled by the Engine or Services now.
