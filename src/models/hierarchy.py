from typing import List, Dict, Any, Optional
from pydantic import Field, PrivateAttr
from src.config import settings
from src.engine.finance.models import FinancialLedger, RevenueStream, Loan, FinancialReport
from src.models.base import GameModel
from src.models.social import SocialScore, Ticket

# --- Moved Classes (from world.py) ---

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

# --- New Hierarchy ---

class WorldState(GameModel):
    """Holds global data."""
    current_week: int = 1
    market_trends: Dict[str, Any] = Field(default_factory=dict)
    weather: str = "Sunny"
    regulatory_laws: List[str] = Field(default_factory=list)

class AgentState(GameModel):
    """Holds Player-specific data."""
    id: str
    name: str
    
    # Financials (Global to the agent/company)
    ledger: FinancialLedger = Field(default_factory=FinancialLedger)
    financial_reports: List[FinancialReport] = Field(default_factory=list)
    loans: List[Loan] = Field(default_factory=list)
    
    # Reputation (Global Score)
    social_score: SocialScore = Field(default_factory=SocialScore)
    _reputation: float = PrivateAttr(default=50.0)

    # Research/Perks
    unlocked_research: List[str] = Field(default_factory=list)
    perks: List[str] = Field(default_factory=list)
    
    # Social & Relationships
    active_scandals: List[Dict[str, Any]] = Field(default_factory=list)
    trust_scores: Dict[str, float] = Field(default_factory=dict)
    alliances: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Vendor Relationships
    vendor_discounts: Dict[str, float] = Field(default_factory=dict)
    vendor_relationships: Dict[str, float] = Field(default_factory=dict)
    
    # Data Tracking
    history: Dict[str, List[float]] = Field(default_factory=lambda: {
        "balance": [],
        "reputation": [],
        "social_score": [],
        "revenue": [],
        "expenses": [],
        "customers": []
    })

    @property
    def reputation(self) -> float:
        return self.social_score.total_score
        
    @reputation.setter
    def reputation(self, value: float):
        self._reputation = value
        self.social_score.community_standing = value

    @property
    def balance(self) -> float:
        return self.ledger.balance

class LocationState(GameModel):
    """Holds Business-specific data."""
    id: str
    name: str
    agent_id: str 
    
    # Assets
    buildings: List[Building] = Field(default_factory=list)
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
    pending_deliveries: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metrics
    cleanliness: float = 0.8
    security_level: float = 0.5
    avg_daily_burn_rate: float = 20.0
    
    # Commercial
    price: float = settings.economy.default_price
    revenue_streams: Dict[str, RevenueStream] = Field(default_factory=dict) # Rev streams per location? Or global? Likely location.
    weekly_spending: Dict[str, float] = Field(default_factory=lambda: {"utility": 0.0, "supplies": 0.0})
    
    # Active
    active_customers: int = 0
    tickets: List[Ticket] = Field(default_factory=list)
    marketing_boost: float = 0.0 # Applied to this location
