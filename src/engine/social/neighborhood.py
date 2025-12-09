# [ ]↔T: Neighborhood Zone System
#   - [x] Define Zone dataclass with traffic/rent/visibility
#   - [x] Implement 5 zones from World Bible
#   - [x] Customer distribution by zone demographics
#   - [ ] Integrate with laundromat placement
# PRIORITY: P1 - Critical
# STATUS: Complete

"""
Neighborhood Zone System

World Bible Reference: 2_0_world_bible_customer_neighborhood.md

Implements zone-based geography affecting:
- Foot traffic
- Rent costs
- Visibility bonuses
- Customer demographics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import random


class ZoneId(Enum):
    """Zone identifiers from World Bible map."""
    ZONE_A = "zone_a"  # University District
    ZONE_B = "zone_b"  # Family Residential
    ZONE_C = "zone_c"  # Shopping Center
    ZONE_D = "zone_d"  # Industrial/Warehouse
    ZONE_E = "zone_e"  # Downtown Business


@dataclass
class Zone:
    """
    A geographic zone in the neighborhood.
    
    Each zone has different characteristics affecting customer flow and costs.
    """
    id: ZoneId
    name: str
    description: str
    
    # Traffic & Visibility
    base_foot_traffic: float  # Multiplier (1.0 = average)
    visibility_bonus: float   # Bonus to marketing effectiveness
    
    # Costs
    weekly_rent: float        # Base rent per week
    utility_modifier: float   # Utility cost multiplier
    
    # Demographics (customer segment distribution)
    demographics: Dict[str, float]  # segment_name -> percentage
    
    # Time-based modifiers
    weekday_traffic_mod: float = 1.0
    weekend_traffic_mod: float = 1.0
    morning_traffic_mod: float = 1.0
    evening_traffic_mod: float = 1.0
    
    # Optional features
    parking_available: bool = True
    security_level: str = "medium"  # low, medium, high
    

class NeighborhoodSystem:
    """
    Manages the neighborhood map and zone-based mechanics.
    """
    
    def __init__(self, agent_ids: List[str] = None):
        self.zones: Dict[ZoneId, Zone] = self._init_zones()
        self.laundromat_locations: Dict[str, ZoneId] = {}  # agent_id -> zone
        if agent_ids:
             for aid in agent_ids:
                 self.assign_random_location(aid)
    
    def _init_zones(self) -> Dict[ZoneId, Zone]:
        """
        Initialize zones based on World Bible 2_0_world_bible_customer_neighborhood.md
        """
        return {
            ZoneId.ZONE_A: Zone(
                id=ZoneId.ZONE_A,
                name="University District",
                description="Near campus with high student population. Lower income but high volume.",
                base_foot_traffic=1.4,
                visibility_bonus=0.3,
                weekly_rent=200.0,
                utility_modifier=1.1,
                demographics={
                    "Student": 0.55,
                    "Young Adult": 0.25,
                    "Adult": 0.15,
                    "Family": 0.03,
                    "Senior": 0.02
                },
                weekday_traffic_mod=1.2,  # Students during week
                weekend_traffic_mod=0.7,  # Students go home
                morning_traffic_mod=0.8,
                evening_traffic_mod=1.3,
                parking_available=False,
                security_level="medium"
            ),
            
            ZoneId.ZONE_B: Zone(
                id=ZoneId.ZONE_B,
                name="Family Residential",
                description="Suburban neighborhood with families. Steady, predictable demand.",
                base_foot_traffic=1.0,
                visibility_bonus=0.1,
                weekly_rent=275.0,
                utility_modifier=1.0,
                demographics={
                    "Family": 0.45,
                    "Adult": 0.25,
                    "Senior": 0.15,
                    "Young Adult": 0.10,
                    "Student": 0.05
                },
                weekday_traffic_mod=0.8,
                weekend_traffic_mod=1.4,  # Families do laundry on weekends
                morning_traffic_mod=1.2,
                evening_traffic_mod=0.9,
                parking_available=True,
                security_level="high"
            ),
            
            ZoneId.ZONE_C: Zone(
                id=ZoneId.ZONE_C,
                name="Shopping Center",
                description="High foot traffic retail area. Good visibility but expensive.",
                base_foot_traffic=1.6,
                visibility_bonus=0.5,
                weekly_rent=400.0,
                utility_modifier=1.2,
                demographics={
                    "Adult": 0.30,
                    "Young Adult": 0.25,
                    "Family": 0.20,
                    "Student": 0.15,
                    "Senior": 0.10
                },
                weekday_traffic_mod=0.9,
                weekend_traffic_mod=1.5,
                morning_traffic_mod=0.7,
                evening_traffic_mod=1.2,
                parking_available=True,
                security_level="high"
            ),
            
            ZoneId.ZONE_D: Zone(
                id=ZoneId.ZONE_D,
                name="Industrial/Warehouse",
                description="Low rent area near warehouses. Limited foot traffic but loyal workers.",
                base_foot_traffic=0.7,
                visibility_bonus=0.0,
                weekly_rent=150.0,
                utility_modifier=0.9,
                demographics={
                    "Adult": 0.50,
                    "Young Adult": 0.25,
                    "Family": 0.15,
                    "Student": 0.05,
                    "Senior": 0.05
                },
                weekday_traffic_mod=1.3,  # Workers during week
                weekend_traffic_mod=0.5,
                morning_traffic_mod=0.6,
                evening_traffic_mod=1.4,  # After work
                parking_available=True,
                security_level="low"
            ),
            
            ZoneId.ZONE_E: Zone(
                id=ZoneId.ZONE_E,
                name="Downtown Business",
                description="Central business district. Mix of professionals and tourists.",
                base_foot_traffic=1.3,
                visibility_bonus=0.4,
                weekly_rent=350.0,
                utility_modifier=1.3,
                demographics={
                    "Young Adult": 0.35,
                    "Adult": 0.30,
                    "Student": 0.15,
                    "Senior": 0.10,
                    "Family": 0.10
                },
                weekday_traffic_mod=1.4,  # Business hours
                weekend_traffic_mod=0.8,
                morning_traffic_mod=1.0,
                evening_traffic_mod=1.1,
                parking_available=False,
                security_level="medium"
            )
        }
    
    def assign_location(self, agent_id: str, zone_id: ZoneId) -> bool:
        """Assign a laundromat to a zone."""
        if zone_id not in self.zones:
            return False
        self.laundromat_locations[agent_id] = zone_id
        return True
    
    def assign_random_location(self, agent_id: str) -> ZoneId:
        """Assign a random zone to a laundromat."""
        zone_id = random.choice(list(ZoneId))
        self.laundromat_locations[agent_id] = zone_id
        return zone_id
    
    def get_zone(self, agent_id: str) -> Optional[Zone]:
        """Get the zone for a laundromat."""
        zone_id = self.laundromat_locations.get(agent_id)
        if zone_id:
            return self.zones.get(zone_id)
        return None
    
    def get_traffic_modifier(
        self, 
        agent_id: str, 
        is_weekend: bool = False,
        time_of_day: str = "midday"
    ) -> float:
        """
        Calculate total traffic modifier for a laundromat based on zone and time.
        
        Args:
            agent_id: The laundromat agent
            is_weekend: Whether it's weekend
            time_of_day: "morning", "midday", or "evening"
            
        Returns:
            Traffic multiplier (1.0 = baseline)
        """
        zone = self.get_zone(agent_id)
        if not zone:
            return 1.0
        
        modifier = zone.base_foot_traffic
        
        # Apply day of week
        if is_weekend:
            modifier *= zone.weekend_traffic_mod
        else:
            modifier *= zone.weekday_traffic_mod
        
        # Apply time of day
        if time_of_day == "morning":
            modifier *= zone.morning_traffic_mod
        elif time_of_day == "evening":
            modifier *= zone.evening_traffic_mod
        
        return modifier
    
    def get_rent_cost(self, agent_id: str) -> float:
        """Get weekly rent for a laundromat's zone."""
        zone = self.get_zone(agent_id)
        return zone.weekly_rent if zone else 250.0  # Default rent
    
    def get_customer_segment_distribution(self, agent_id: str) -> Dict[str, float]:
        """
        Get expected customer segment distribution for a laundromat based on zone.
        """
        zone = self.get_zone(agent_id)
        if not zone:
            # Default distribution
            return {
                "Student": 0.25,
                "Family": 0.28,
                "Senior": 0.18,
                "Adult": 0.29,
                "Young Adult": 0.00  # Merged with Adult in default
            }
        return zone.demographics
    
    def get_visibility_bonus(self, agent_id: str) -> float:
        """Get marketing visibility bonus for zone."""
        zone = self.get_zone(agent_id)
        return zone.visibility_bonus if zone else 0.0
    
    def calculate_zone_competition(self, agent_id: str, all_locations: Dict[str, ZoneId]) -> float:
        """
        Calculate competition factor based on how many laundromats are in the same zone.
        
        Returns a modifier where 1.0 = no competition, lower = more competition
        """
        my_zone = self.laundromat_locations.get(agent_id)
        if not my_zone:
            return 1.0
        
        competitors_in_zone = sum(
            1 for aid, zone in all_locations.items() 
            if zone == my_zone and aid != agent_id
        )
        
        # Each competitor reduces share
        # 0 competitors: 1.0, 1 competitor: 0.6, 2: 0.4, 3+: 0.3
        if competitors_in_zone == 0:
            return 1.0
        elif competitors_in_zone == 1:
            return 0.6
        elif competitors_in_zone == 2:
            return 0.4
        else:
            return 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for API responses."""
        return {
            "zones": {
                zone_id.value: {
                    "name": zone.name,
                    "description": zone.description,
                    "foot_traffic": zone.base_foot_traffic,
                    "visibility_bonus": zone.visibility_bonus,
                    "weekly_rent": zone.weekly_rent,
                    "demographics": zone.demographics,
                    "parking": zone.parking_available,
                    "security": zone.security_level
                }
                for zone_id, zone in self.zones.items()
            },
            "laundromat_locations": {
                agent_id: zone_id.value 
                for agent_id, zone_id in self.laundromat_locations.items()
            }
        }
    
    def get_zone_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all zones for display."""
        return [
            {
                "id": zone_id.value,
                "name": zone.name,
                "description": zone.description,
                "traffic": "High" if zone.base_foot_traffic > 1.3 else ("Medium" if zone.base_foot_traffic > 0.8 else "Low"),
                "rent": f"${zone.weekly_rent}/week",
                "visibility": f"+{int(zone.visibility_bonus * 100)}%",
                "primary_demographic": max(zone.demographics.items(), key=lambda x: x[1])[0]
            }
            for zone_id, zone in self.zones.items()
        ]
