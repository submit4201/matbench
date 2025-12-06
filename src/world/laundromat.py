from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from src.world.ticket import Ticket
from src.world.financials import RevenueStream, Loan, TaxRecord, FinancialReport
from src.world.social import SocialScore

@dataclass
class Machine:
    id: str
    type: str = "standard_washer"
    condition: float = 1.0  # 0.0 to 1.0
    is_broken: bool = False
    age_weeks: int = 0

@dataclass
class StaffMember:
    id: str
    name: str
    role: str = "attendant"
    skill_level: float = 0.5  # 0.0 to 1.0
    morale: float = 0.8       # 0.0 to 1.0
    wage: float = 15.0        # Hourly rate

@dataclass
class LaundromatState:
    name: str
    id: str
    # World Bible Starting Resources (1_2_starting_resources_equitment.md)
    balance: float = 2500.0  # $2,500 cash on hand
    reputation: float = 50.0
    social_score: SocialScore = field(default_factory=SocialScore)
    price: float = 5.0
    
    # Detailed Assets
    machines: List[Machine] = field(default_factory=list)
    staff: List[StaffMember] = field(default_factory=list)  # Starts with 0 staff
    
    # Inventory & Supplies (World Bible: 200 detergent, 100 softener, 150 dryer sheets)
    inventory: Dict[str, int] = field(default_factory=lambda: {
        "detergent": 200,    # 200 loads worth
        "softener": 100,     # 100 loads worth  
        "dryer_sheets": 150, # 150 units
        "snacks": 50,        # 50 units for vending machine
        "cleaning_supplies": 14,  # 2 weeks worth (days)
        "parts": 5
    })
    
    # Operational State
    marketing_boost: float = 0.0
    cleanliness: float = 0.8  # 0.0 to 1.0
    security_level: float = 0.5 # 0.0 to 1.0
    
    # Inventory Metrics
    avg_daily_burn_rate: float = 20.0 # Loads per day
    
    # Active Data
    tickets: List[Ticket] = field(default_factory=list)
    active_events: List[str] = field(default_factory=list) # IDs of active effects
    
    # Real-time Metrics (Current Week)
    active_customers: int = 0
    
    # Historical Data (for analysis)
    history: Dict[str, List[float]] = field(default_factory=lambda: {
        "balance": [],
        "reputation": [],
        "social_score": [],
        "revenue": [],
        "expenses": [],
        "customers": []
    })

    # Financial System
    revenue_streams: Dict[str, RevenueStream] = field(default_factory=dict)
    loans: List[Loan] = field(default_factory=list)
    financial_reports: List[FinancialReport] = field(default_factory=list)
    tax_records: List[TaxRecord] = field(default_factory=list)
    
    # Supply Chain
    pending_deliveries: List[Dict] = field(default_factory=list) # List of {item, quantity, arrival_week, vendor_name}
    
    # Internal reputation storage if needed, but we prefer property
    _reputation: float = 50.0

    @property
    def broken_machines(self) -> int:
        return sum(1 for m in self.machines if m.is_broken)

    @property
    def reputation(self) -> float:
        """Reputation is now directly linked to Social Score for consistency."""
        return self.social_score.total_score
        
    @reputation.setter
    def reputation(self, value: float):
        """Allow setting for legacy compatibility, but it won't persist independently of social score components in the long run."""
        self._reputation = value

    def __post_init__(self):
        # Initialize machines per World Bible: 10 washers, 5 dryers at 80% condition
        if not self.machines:
            for i in range(10):
                self.machines.append(Machine(id=f"W{i}", type="standard_washer", condition=0.80))
            for i in range(5):
                self.machines.append(Machine(id=f"D{i}", type="standard_dryer", condition=0.80))
        
        # World Bible: Start with 0 employees (owner-operated)
        # Staff can be hired during gameplay
        # self.staff stays empty by default

    def update_reputation(self, delta: float):
        # Legacy method: distribute delta across social score components evenly or to community_standing
        self.update_social_score("community_standing", delta)

    def update_social_score(self, component: str, delta: float):
        self.social_score.update_component(component, delta)
    
    def update_inventory_usage(self, usage: Dict[str, int]):
        """Update inventory based on usage and recalculate burn rate."""
        total_loads = usage.get("detergent", 0) # Use detergent as proxy for loads
        
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
        
        # Recommendations based on "Moderate" risk tolerance (14 days supply)
        target_days = 14
        reorder_point = 9 # days
        
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

        self.balance += revenue - expenses
        
        # Decay marketing boost naturally over time
        if self.marketing_boost > 0:
            decay = 5.0  # Lose 5 boost points per week
            self.marketing_boost = max(0, self.marketing_boost - decay)
            
        # Machine wear and tear (simplified)
        for machine in self.machines:
            if not machine.is_broken:
                machine.condition = max(0, machine.condition - 0.01) # 1% degradation per week
                machine.age_weeks += 1
                if machine.condition < 0.2: # High chance to break if poor condition
                    import random
                    if random.random() < 0.3:
                        machine.is_broken = True
