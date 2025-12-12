from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class ScenarioDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    CHAOS = "chaos"

@dataclass
class EventConfig:
    """Configuration for a specific event in a scenario"""
    week: int
    event_type: str  # e.g., "heatwave", "equipment_failure"
    target_agent: Optional[str] = None
    severity: float = 1.0

@dataclass
class InitialConditions:
    """Initial state for each laundromat in scenario"""
    balance: float = 100.0
    machines: int = 4
    price: float = 5.0
    social_score: float = 50.0
    inventory: Dict[str, int] = None
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = {"detergent": 50, "softener": 50, "parts": 5}

@dataclass
class Scenario:
    """A canonical benchmark scenario with fixed configuration"""
    name: str
    description: str
    difficulty: ScenarioDifficulty
    seed: int
    weeks: int = 52
    
    # Initial conditions for each player
    p1_initial: InitialConditions = None
    p2_initial: InitialConditions = None
    p3_initial: InitialConditions = None
    
    # Scheduled events
    events: List[EventConfig] = None
    
    # Special rules for this scenario
    special_rules: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.p1_initial is None:
            self.p1_initial = InitialConditions()
        if self.p2_initial is None:
            self.p2_initial = InitialConditions()
        if self.p3_initial is None:
            self.p3_initial = InitialConditions()
        if self.events is None:
            self.events = []
        if self.special_rules is None:
            self.special_rules = {}


# =========================================
# CANONICAL SCENARIOS
# =========================================

SCENARIOS = {
    "stable_market": Scenario(
        name="stable_market",
        description="No events, balanced competition. Pure strategy test.",
        difficulty=ScenarioDifficulty.EASY,
        seed=42,
        p1_initial=InitialConditions(balance=100, machines=4, price=6.0, social_score=80),
        p2_initial=InitialConditions(balance=100, machines=4, price=3.0, social_score=30),
        p3_initial=InitialConditions(balance=100, machines=4, price=10.0, social_score=60),
        events=[]
    ),
    
    "price_war": Scenario(
        name="price_war",
        description="Aggressive competitors start with very low prices.",
        difficulty=ScenarioDifficulty.MEDIUM,
        seed=101,
        p1_initial=InitialConditions(balance=100, machines=4, price=6.0, social_score=50),
        p2_initial=InitialConditions(balance=150, machines=5, price=2.0, social_score=40),
        p3_initial=InitialConditions(balance=150, machines=5, price=2.5, social_score=45),
        events=[]
    ),
    
    "supply_crisis": Scenario(
        name="supply_crisis",
        description="Limited starting inventory, must manage resources carefully.",
        difficulty=ScenarioDifficulty.HARD,
        seed=202,
        p1_initial=InitialConditions(
            balance=80, 
            machines=4, 
            price=5.0, 
            social_score=50,
            inventory={"detergent": 10, "softener": 10, "parts": 2}
        ),
        p2_initial=InitialConditions(
            balance=80,
            inventory={"detergent": 10, "softener": 10, "parts": 2}
        ),
        p3_initial=InitialConditions(
            balance=80,
            inventory={"detergent": 10, "softener": 10, "parts": 2}
        ),
        events=[
            EventConfig(week=6, event_type="supply_shortage", severity=0.5),
            EventConfig(week=12, event_type="supply_shortage", severity=0.5),
            EventConfig(week=18, event_type="supply_shortage", severity=0.5)
        ]
    ),
    
    "heatwave": Scenario(
        name="heatwave",
        description="Summer demand spike in weeks 7-12. Can you capitalize?",
        difficulty=ScenarioDifficulty.MEDIUM,
        seed=303,
        events=[
            EventConfig(week=7, event_type="heatwave"),
            EventConfig(week=8, event_type="heatwave"),
            EventConfig(week=9, event_type="heatwave"),
            EventConfig(week=10, event_type="heatwave"),
            EventConfig(week=11, event_type="heatwave"),
            EventConfig(week=12, event_type="heatwave")
        ]
    ),
    
    "equipment_failure": Scenario(
        name="equipment_failure",
        description="Random machine breakdowns every few weeks.",
        difficulty=ScenarioDifficulty.HARD,
        seed=404,
        events=[
            EventConfig(week=4, event_type="machine_breakdown", target_agent="p1"),
            EventConfig(week=8, event_type="machine_breakdown", target_agent="p2"),
            EventConfig(week=12, event_type="machine_breakdown", target_agent="p3"),
            EventConfig(week=16, event_type="machine_breakdown", target_agent="p1"),
            EventConfig(week=20, event_type="machine_breakdown", target_agent="p2")
        ]
    ),
    
    "luxury_rush": Scenario(
        name="luxury_rush",
        description="High-paying customers prefer quality. High prices win.",
        difficulty=ScenarioDifficulty.MEDIUM,
        seed=505,
        p1_initial=InitialConditions(balance=100, machines=4, price=6.0, social_score=80),
        p2_initial=InitialConditions(balance=100, machines=4, price=3.0, social_score=30),
        p3_initial=InitialConditions(balance=100, machines=4, price=10.0, social_score=90),
        special_rules={"customer_preference": "quality"},
        events=[
            EventConfig(week=5, event_type="luxury_customer_influx"),
            EventConfig(week=15, event_type="luxury_customer_influx")
        ]
    ),
    
    "economic_downturn": Scenario(
        name="economic_downturn",
        description="Reduced customer spending. Lower prices dominate.",
        difficulty=ScenarioDifficulty.HARD,
        seed=606,
        events=[
            EventConfig(week=6, event_type="economic_downturn"),
            EventConfig(week=12, event_type="economic_downturn"),
            EventConfig(week=18, event_type="economic_downturn")
        ],
        special_rules={"customer_spending": "low"}
    ),
    
    "new_competitor": Scenario(
        name="new_competitor",
        description="A 4th player enters the market at week 8.",
        difficulty=ScenarioDifficulty.HARD,
        seed=707,
        special_rules={"late_entry": {"agent_id": "p4", "week": 8}},
        events=[
            EventConfig(week=8, event_type="new_competitor")
        ]
    ),
    
    "seasonal_swing": Scenario(
        name="seasonal_swing",
        description="Extreme seasonal demand variation throughout the year.",
        difficulty=ScenarioDifficulty.HARD,
        seed=808,
        events=[
            EventConfig(week=1, event_type="spring_cleaning"),
            EventConfig(week=7, event_type="summer_slump"),
            EventConfig(week=13, event_type="back_to_school"),
            EventConfig(week=19, event_type="winter_surge")
        ],
        special_rules={"seasonal_multiplier": 2.0}
    ),
    
    "chaos_mode": Scenario(
        name="chaos_mode",
        description="Random events EVERY week. Adapt or die.",
        difficulty=ScenarioDifficulty.CHAOS,
        seed=999,
        p1_initial=InitialConditions(balance=150, machines=5, price=5.0),
        p2_initial=InitialConditions(balance=150, machines=5, price=5.0),
        p3_initial=InitialConditions(balance=150, machines=5, price=5.0),
        events=[
            # Will be populated by random event generator
        ],
        special_rules={"chaos_mode": True, "event_probability": 1.0}
    )
}


def get_scenario(name: str) -> Scenario:
    """Get a scenario by name"""
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {name}. Available: {list(SCENARIOS.keys())}")
    return SCENARIOS[name]


def list_scenarios() -> List[str]:
    """List all available scenario names"""
    return list(SCENARIOS.keys())
