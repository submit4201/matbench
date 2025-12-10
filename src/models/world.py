from typing import List, Dict, Optional, Any
from pydantic import Field, PrivateAttr, model_validator
from src.models.base import GameModel
from src.models.financial import FinancialLedger, RevenueStream, Loan, FinancialReport, TransactionCategory
from src.models.social import SocialScore, Ticket

class Machine(GameModel):
    id: str
    type: str = "standard_washer"
    condition: float = 1.0
    is_broken: bool = False
    age_weeks: int = 0
    location_id: Optional[str] = None

class StaffMember(GameModel):
    id: str
    name: str
    role: str = "attendant"
    skill_level: float = 0.5
    morale: float = 0.8
    wage: float = 15.0

class Building(GameModel):
    id: str
    name: str
    type: str = "storefront"
    condition: float = 1.0
    capacity_machines: int = 20
    location_multiplier: float = 1.0
    price: float = 0.0
    rent: float = 0.0

class LaundromatState(GameModel):
    name: str
    id: str
    ledger: FinancialLedger = Field(default_factory=FinancialLedger)
    # event_ledger: Any = None # Skip for now or use Any, circular dep with GameEventLedger?
    # bills: List[Bill] = Field(default_factory=list)
    
    # Internal reputation storage
    _reputation: float = PrivateAttr(default=50.0)
    
    # Social Score (Pydantic model with computed properties)
    social_score: SocialScore = Field(default_factory=SocialScore)
    
    price: float = 5.0
    
    # Real Estate
    buildings: List[Building] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    
    # Assets
    machines: List[Machine] = Field(default_factory=list)
    staff: List[StaffMember] = Field(default_factory=list)
    
    # Inventory
    inventory: Dict[str, int] = Field(default_factory=lambda: {
        "detergent": 200,
        "softener": 100,
        "dryer_sheets": 150,
        "snacks": 50,
        "cleaning_supplies": 14,
        "parts": 5
    })
    
    # Status
    marketing_boost: float = 0.0
    cleanliness: float = 0.8
    security_level: float = 0.5
    avg_daily_burn_rate: float = 20.0
    active_customers: int = 0
    
    # Financials
    revenue_streams: Dict[str, RevenueStream] = Field(default_factory=dict)
    loans: List[Loan] = Field(default_factory=list)
    financial_reports: List[FinancialReport] = Field(default_factory=list)
    
    # Supply
    pending_deliveries: List[Dict[str, Any]] = Field(default_factory=list)
    
    # History
    history: Dict[str, List[float]] = Field(default_factory=lambda: {
        "balance": [],
        "reputation": [],
        "social_score": [],
        "revenue": [],
        "expenses": [],
        "customers": []
    })
    
    # Active Data
    tickets: List[Ticket] = Field(default_factory=list)
    active_events: List[str] = Field(default_factory=list)

    def model_post_init(self, __context):
        """Logic run after initialization (Pydantic V2)."""
        # Initialize machines if empty
        if not self.machines:
            for i in range(10):
                self.machines.append(Machine(id=f"W{i}", type="standard_washer", condition=0.80))
            for i in range(5):
                self.machines.append(Machine(id=f"D{i}", type="standard_dryer", condition=0.80))
        
        # Seed initial capital if ledger is empty
        if not self.ledger.transactions:
             self.ledger.add(2500.0, TransactionCategory.CAPITAL, "Initial Capital", week=0)

        # Initialize default building if none
        if not self.buildings:
            default_building = Building(
                id=f"HQ-{self.id}",
                name=f"{self.name} Headquarters",
                type="storefront",
                condition=1.0,
                capacity_machines=20,
                location_multiplier=1.0
            )
            self.buildings.append(default_building)
            self.locations.append(default_building.id)
            
            # Assign initial machines to this location
            for m in self.machines:
                m.location_id = default_building.id

    @property
    def broken_machines(self) -> int:
        return sum(1 for m in self.machines if m.is_broken)

    @property
    def reputation(self) -> float:
        """Reputation is now directly linked to Social Score."""
        return self.social_score.total_score
        
    @reputation.setter
    def reputation(self, value: float):
        self._reputation = value
        # Update social score component
        self.social_score.community_standing = value

    @property
    def balance(self) -> float:
        return self.ledger.balance
        
    @balance.setter
    def balance(self, value: float):
        """Allow setting balance directly by creating an adjustment transaction."""
        current = self.ledger.balance
        diff = value - current
        if abs(diff) > 0.001:
            self.ledger.add(diff, TransactionCategory.ADJUSTMENT, "Manual Balance Adjustment", week=0)

    def update_reputation(self, delta: float):
        self.update_social_score("community_standing", delta)

    def update_social_score(self, component: str, delta: float):
        """Update a social score component by delta."""
        if hasattr(self.social_score, component):
            current = getattr(self.social_score, component)
            new_val = max(0.0, min(100.0, current + delta))
            setattr(self.social_score, component, new_val)
    
    def update_inventory_usage(self, usage: Dict[str, int]):
        """Update inventory based on usage and recalculate burn rate."""
        total_loads = usage.get("detergent", 0)
        
        # Update stock
        for item, amount in usage.items():
            if item in self.inventory:
                self.inventory[item] = max(0, self.inventory[item] - amount)
                
        # Update burn rate (simple moving average)
        daily_usage = total_loads / 7.0
        alpha = 0.3 # Smoothing factor
        self.avg_daily_burn_rate = (alpha * daily_usage) + ((1 - alpha) * self.avg_daily_burn_rate)

    def get_inventory_metrics(self) -> Dict[str, Any]:
        """Calculate inventory health metrics."""
        burn_rate = self.avg_daily_burn_rate
        if burn_rate <= 0: burn_rate = 1.0
        
        detergent_stock = self.inventory.get("detergent", 0)
        days_supply = detergent_stock / burn_rate
        
        target_days = 14
        reorder_point = 9
        
        status = "Good"
        if days_supply < 3:
            status = "Critical"
        elif days_supply < reorder_point:
            status = "Low"
            
        return {
            "stock_level": detergent_stock,
            "burn_rate": round(burn_rate, 1),
            "days_of_supply": round(days_supply, 1),
            "status": status,
            "recommendation": f"Buy {int((target_days - days_supply) * burn_rate)} loads" if days_supply < target_days else "Stock is healthy"
        }
    
    def process_week(self, revenue: float, expenses: float):
        # Archive current state to history
        self.history["balance"].append(self.balance)
        self.history["reputation"].append(self.reputation)
        self.history["social_score"].append(self.social_score.total_score)
        self.history["revenue"].append(revenue)
        self.history["expenses"].append(expenses)
        self.history["customers"].append(self.active_customers)
        
        # Decay marketing boost naturally over time
        if self.marketing_boost > 0:
            decay = 5.0
            self.marketing_boost = max(0, self.marketing_boost - decay)
            
        # Machine wear and tear
        for machine in self.machines:
            if not machine.is_broken:
                machine.condition = max(0, machine.condition - 0.01)
                machine.age_weeks += 1
                if machine.condition < 0.2:
                    import random
                    if random.random() < 0.3:
                        machine.is_broken = True

    def add_funds(self, amount: float, category: str, description: str, week: int):
         try:
             cat = TransactionCategory(category)
         except ValueError:
             cat = TransactionCategory.ADJUSTMENT
         self.ledger.add(amount, cat, description, week)
