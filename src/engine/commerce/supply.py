import random
from typing import Optional, Dict, List
from src.models.commerce import SupplyChainEventType, SupplyChainEvent

class SupplyChainManager:
    def __init__(self):
        self.active_events: List[SupplyChainEvent] = []

    def check_for_regular_events(self, order_context: Dict) -> List[SupplyChainEvent]:
        """
        Check for per-order events like delays or quality issues.
        order_context should contain: vendor_reliability (0.0-1.0)
        """
        events = []
        reliability = order_context.get("vendor_reliability", 1.0)
        
        # Base probabilities modified by reliability (lower reliability = higher chance of bad stuff)
        # 1.0 reliability = 0.5x chance, 0.5 reliability = 1.5x chance
        risk_modifier = 2.0 - reliability
        
        # Delivery Delay Minor (10% base)
        if random.random() < 0.10 * risk_modifier:
            events.append(SupplyChainEvent(
                type=SupplyChainEventType.DELIVERY_DELAY_MINOR,
                vendor_id=order_context.get("vendor_id"),
                description="Minor delivery delay (+3-5 days)",
                duration_weeks=0,
                effect_data={"delay_days": random.randint(3, 5)},
                start_week=order_context.get("week", 0),
                severity="low"
            ))
            
        # Delivery Delay Major (5% base)
        elif random.random() < 0.05 * risk_modifier:
            events.append(SupplyChainEvent(
                type=SupplyChainEventType.DELIVERY_DELAY_MAJOR,
                vendor_id=order_context.get("vendor_id"),
                description="Major delivery delay (+7-14 days)",
                duration_weeks=0,
                effect_data={"delay_days": random.randint(7, 14)},
                start_week=order_context.get("week", 0),
                severity="medium"
            ))

        # Partial Shipment (8% base)
        if random.random() < 0.08 * risk_modifier:
            events.append(SupplyChainEvent(
                type=SupplyChainEventType.PARTIAL_SHIPMENT,
                vendor_id=order_context.get("vendor_id"),
                description="Partial shipment received (50-75%)",
                duration_weeks=0,
                effect_data={"quantity_multiplier": random.uniform(0.50, 0.75)},
                start_week=order_context.get("week", 0),
                severity="medium"
            ))

        # Quality Issue Minor (5% base)
        if random.random() < 0.05 * risk_modifier:
            events.append(SupplyChainEvent(
                type=SupplyChainEventType.QUALITY_ISSUE_MINOR,
                vendor_id=order_context.get("vendor_id"),
                description="Minor quality issue (20% defective)",
                duration_weeks=0,
                effect_data={"defective_rate": 0.20},
                start_week=order_context.get("week", 0),
                severity="low"
            ))
            
        # Lost Shipment (1% base)
        if random.random() < 0.01 * risk_modifier:
            events.append(SupplyChainEvent(
                type=SupplyChainEventType.LOST_SHIPMENT,
                vendor_id=order_context.get("vendor_id"),
                description="Shipment lost in transit",
                duration_weeks=0,
                effect_data={"quantity_multiplier": 0.0},
                start_week=order_context.get("week", 0),
                severity="high"
            ))

        return events

    def check_for_major_events(self, week: int, vendors: List[str]) -> List[SupplyChainEvent]:
        """
        Check for major weekly disruptions.
        """
        new_events = []
        
        # Vendor Shortage (5% per week)
        if random.random() < 0.05:
            target_vendor = random.choice(vendors)
            new_events.append(SupplyChainEvent(
                type=SupplyChainEventType.VENDOR_SHORTAGE,
                vendor_id=target_vendor,
                description=f"Vendor Shortage at {target_vendor}",
                duration_weeks=random.randint(2, 4),
                effect_data={
                    "fulfillment_cap": 0.5,
                    "price_increase": random.uniform(0.2, 0.3)
                },
                start_week=week,
                severity="high"
            ))

        # Price Spike (8% per week)
        if random.random() < 0.08:
            # Affects a category or vendor. Let's say a random vendor for now.
            target_vendor = random.choice(vendors)
            severity = random.choice(["minor", "moderate", "severe"])
            increase = {
                "minor": random.uniform(0.1, 0.2),
                "moderate": random.uniform(0.2, 0.4),
                "severe": random.uniform(0.4, 0.75)
            }[severity]
            
            new_events.append(SupplyChainEvent(
                type=SupplyChainEventType.PRICE_SPIKE,
                vendor_id=target_vendor,
                description=f"{severity.capitalize()} Price Spike at {target_vendor}",
                duration_weeks=random.randint(2, 6),
                effect_data={"price_increase": increase},
                start_week=week,
                severity="medium" if severity == "minor" else "high"
            ))

        # Vendor Bankruptcy (1% per quarter per vendor -> approx 0.08% per week per vendor)
        for v_id in vendors:
            if random.random() < 0.0008:
                new_events.append(SupplyChainEvent(
                    type=SupplyChainEventType.VENDOR_BANKRUPTCY,
                    vendor_id=v_id,
                    description=f"Vendor Bankruptcy: {v_id} has ceased operations",
                    duration_weeks=999, # Permanent
                    effect_data={"available": 0.0},
                    start_week=week,
                    severity="critical"
                ))

        # Transportation Disruption (3% per month -> approx 0.75% per week)
        if random.random() < 0.0075:
            new_events.append(SupplyChainEvent(
                type=SupplyChainEventType.TRANSPORTATION_DISRUPTION,
                vendor_id=None, # Global
                description="Regional Transportation Disruption",
                duration_weeks=random.randint(1, 4),
                effect_data={
                    "delivery_delay_add": random.randint(5, 10),
                    "delivery_cost_increase": random.uniform(0.25, 0.50)
                },
                start_week=week,
                severity="high"
            ))

        self.active_events.extend(new_events)
        return new_events

    def update_events(self, week: int):
        """Clean up expired events"""
        self.active_events = [
            e for e in self.active_events 
            if (week - e.start_week) < e.duration_weeks or e.duration_weeks == 999
        ]

    def get_active_effects(self, vendor_id: str) -> Dict[str, float]:
        """Aggregate effects for a specific vendor"""
        effects = {
            "price_multiplier": 1.0,
            "delivery_delay_add": 0,
            "fulfillment_cap": 1.0,
            "available": 1.0
        }
        
        for e in self.active_events:
            if e.vendor_id is None or e.vendor_id == vendor_id:
                if "price_increase" in e.effect_data:
                    effects["price_multiplier"] *= (1.0 + e.effect_data["price_increase"])
                if "delivery_delay_add" in e.effect_data:
                    effects["delivery_delay_add"] += e.effect_data["delivery_delay_add"]
                if "fulfillment_cap" in e.effect_data:
                    effects["fulfillment_cap"] = min(effects["fulfillment_cap"], e.effect_data["fulfillment_cap"])
                if "available" in e.effect_data:
                    effects["available"] = min(effects["available"], e.effect_data["available"])
                if "delivery_cost_increase" in e.effect_data:
                     # Handle separately or fold into price for now
                     pass
                     
        return effects
