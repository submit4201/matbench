import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math
from src.models.commerce import VendorTier, SupplyOffer, VendorProfile, SupplyChainEventType
from .supply import SupplyChainManager

class Vendor:
    def __init__(self, profile: VendorProfile):
        self.profile = profile
        self.tier = VendorTier.NEW
        self.weeks_consistent = 0
        self.total_spend = 0.0
        self.relationship_scores: Dict[str, float] = {}  # agent_id -> score
        self.negotiated_discounts: Dict[str, Dict[str, float]] = {} # agent_id -> {item -> multiplier}
        self.exclusive_contract = False # This might need to be per-agent too, but keeping simple for now
        self.current_multipliers = {k: 1.0 for k in profile.base_prices}
        self.special_offer: Optional[SupplyOffer] = None
        self.last_delivery_status = "On Time"
        self.active_effects: Dict[str, float] = {} # From supply chain events
        self.messages: List[Dict] = [] # Store messages for agents
    
    def get_market_status(self) -> Dict:
        """Return current market status for this vendor including prices and special offers."""
        return {
            "vendor_id": self.profile.id,
            "vendor_name": self.profile.name,
            "tier": self.tier.name,
            "current_prices": {item: self.get_price(item) for item in self.profile.base_prices},
            "price_multipliers": self.current_multipliers.copy(),
            "special_offer": {
                "item": self.special_offer.item_name,
                "price": self.special_offer.price,
                "description": self.special_offer.description
            } if self.special_offer else None,
            "reliability": self.profile.reliability,
            "delivery_days": self.profile.delivery_days,
            "last_delivery_status": self.last_delivery_status,
            "active_effects": self.active_effects.copy()
        }
        
    def update_market(self, week: int, supply_chain_effects: Dict[str, float]):
        self.active_effects = supply_chain_effects
        
        # Randomly fluctuate prices based on reliability
        # Lower reliability = higher volatility
        volatility = 1.0 - self.profile.reliability
        
        for item in self.profile.base_prices:
            # Fluctuate
            change = random.uniform(-volatility, volatility) * 0.2
            self.current_multipliers[item] = max(0.5, min(2.0, 1.0 + change))
        
        # Occasional special offer
        if random.random() < 0.2:
            item = random.choice(list(self.profile.base_prices.keys()))
            discount = 0.8  # 20% off default
            
            # Better tiers get better offers
            if self.tier == VendorTier.PREFERRED:
                discount = 0.7
            elif self.tier == VendorTier.STRATEGIC:
                discount = 0.6
                
            price = self.profile.base_prices[item] * discount
            self.special_offer = SupplyOffer(
                item_name=item,
                price=price,
                description=f"Special on {item}! {int((1-discount)*100)}% off!"
            )
        else:
            self.special_offer = None

    def get_price(self, item: str, agent_id: str = None) -> float:
        base = self.profile.base_prices.get(item, 0)
        multiplier = self.current_multipliers.get(item, 1.0)
        
        # Apply supply chain price multiplier
        sc_multiplier = self.active_effects.get("price_multiplier", 1.0)
        
        price = base * multiplier * sc_multiplier
        
        # Apply tier discounts (Global tier for now, or per agent?)
        # Let's assume tier is global for the vendor's general market standing, 
        # but we should probably have per-agent tiers. For now, using global tier.
        if self.tier == VendorTier.REGULAR:
            price *= 0.95
        elif self.tier == VendorTier.PREFERRED:
            price *= 0.90
        elif self.tier == VendorTier.STRATEGIC:
            price *= 0.80  # Up to 20% off
            
        # Exclusive contract bonus (Global for now)
        if self.exclusive_contract:
            price *= 0.95
            
        # Agent specific negotiated discount
        if agent_id:
            agent_discounts = self.negotiated_discounts.get(agent_id, {})
            price *= agent_discounts.get(item, 1.0)
            
        return round(price, 3)

    def negotiate_price(self, item: str, agent_name: str, social_score: float, agent_id: str) -> Dict:
        """
        Attempt to negotiate a better price for an item.
        Returns a result dict with success status and message.
        """
        # Rule-based logic
        current_rel = self.relationship_scores.get(agent_id, 0)
        
        # Difficulty based on vendor reliability (more reliable = harder to negotiate)
        difficulty = self.profile.reliability * 100
        
        # Score = Social Score + Relationship Score + Random Luck
        negotiation_power = social_score + (current_rel * 2) + random.randint(0, 20)
        
        success = False
        message = ""
        
        if negotiation_power > difficulty:
            success = True
            # Grant discount
            if agent_id not in self.negotiated_discounts:
                self.negotiated_discounts[agent_id] = {}
            
            current_discount = self.negotiated_discounts[agent_id].get(item, 1.0)
            new_discount = max(0.7, current_discount - 0.05) # Max 30% off total, 5% steps
            self.negotiated_discounts[agent_id][item] = new_discount
            
            message = f"Agreed. We value your business, {agent_name}. We can offer you a {int((1-new_discount)*100)}% discount on {item}."
            self.relationship_scores[agent_id] = current_rel + 1
        else:
            message = f"I'm afraid we can't lower our prices on {item} right now. Our margins are tight."
            self.relationship_scores[agent_id] = max(0, current_rel - 1)
            
        return {
            "success": success,
            "message": message,
            "vendor_id": self.profile.id
        }

    def process_order(self, items: Dict[str, int], week: int, sc_manager: SupplyChainManager, agent_id: str = None) -> Dict:
        """
        Process an order and return the result including cost and delivery time.
        """
        # Check for bankruptcy or availability
        if self.active_effects.get("available", 1.0) <= 0:
            return {
                "vendor": self.profile.name,
                "cost": 0,
                "delivery_days": 0,
                "status": "Order Failed: Vendor Unavailable",
                "events": []
            }

        cost = 0.0
        for item, qty in items.items():
            cost += self.get_price(item, agent_id) * qty
            
        # Check reliability for delivery issues
        delivery_days = self.profile.delivery_days + int(self.active_effects.get("delivery_delay_add", 0))
        status = "On Time"
        events = []
        
        # Check for regular supply chain events
        order_context = {
            "vendor_id": self.profile.id,
            "vendor_reliability": self.profile.reliability,
            "week": week
        }
        sc_events = sc_manager.check_for_regular_events(order_context)
        
        quantity_multiplier = 1.0
        
        for event in sc_events:
            events.append(event.description)
            if event.type == SupplyChainEventType.DELIVERY_DELAY_MINOR:
                delay = event.effect_data.get("delay_days", 3)
                delivery_days += delay
                status = f"Delayed {delay} days (Minor)"
            elif event.type == SupplyChainEventType.DELIVERY_DELAY_MAJOR:
                delay = event.effect_data.get("delay_days", 10)
                delivery_days += delay
                status = f"Delayed {delay} days (Major)"
            elif event.type == SupplyChainEventType.PARTIAL_SHIPMENT:
                quantity_multiplier *= event.effect_data.get("quantity_multiplier", 0.75)
                status = "Partial Shipment"
            elif event.type == SupplyChainEventType.LOST_SHIPMENT:
                quantity_multiplier = 0.0
                status = "Lost Shipment"
        
        # Apply quantity multiplier to items (simplified, applies to whole order for now)
        # In a real system, we'd return the actual quantities delivered.
        # For now, we'll just note it in the status/result.
        
        self.last_delivery_status = status
        self.total_spend += cost
        self.weeks_consistent += 1
        
        # Check for tier upgrade
        self._check_tier_upgrade()
        
        return {
            "vendor": self.profile.name,
            "cost": cost,
            "delivery_days": delivery_days,
            "status": status,
            "events": events,
            "quantity_multiplier": quantity_multiplier
        }
        
    def _check_tier_upgrade(self):
        # Simple progression logic
        if self.tier == VendorTier.NEW and self.weeks_consistent >= 4:
            self.tier = VendorTier.REGULAR
        elif self.tier == VendorTier.REGULAR and self.weeks_consistent >= 8:
            self.tier = VendorTier.PREFERRED
        elif self.tier == VendorTier.PREFERRED and self.weeks_consistent >= 16 and self.exclusive_contract:
            self.tier = VendorTier.STRATEGIC

class LLMVendor(Vendor):
    """LLM-powered vendor wrapper."""
    def __init__(self, profile: VendorProfile, llm_provider: str = "openai"):
        super().__init__(profile)
        self.llm_provider = llm_provider
        self.use_llm = True
        try:
            from src.engine.llm_utils import LLMHelper
            self.llm, self.deployment = LLMHelper.setup_llm(llm_provider)
        except Exception as e:
            print(f"[LLMVendor] Failed to setup LLM: {e}. Falling back to rule-based.")
            self.use_llm = False

    def negotiate_price(self, item: str, agent_name: str, social_score: float, agent_id: str) -> Dict:
        if not self.use_llm:
            return super().negotiate_price(item, agent_name, social_score, agent_id)
            
        # LLM Logic
        try:
            prompt = f"""
            You are {self.profile.name}, a vendor in a laundromat simulation.
            Profile: {self.profile.description}
            Slogan: {self.profile.slogan}
            Reliability: {self.profile.reliability}
            
            A customer, {agent_name} (Social Score: {social_score}), is trying to negotiate a better price for {item}.
            Your current relationship score with them is {self.relationship_scores.get(agent_id, 0)}.
            
            Decide if you accept their negotiation. 
            - High social score (>50) and good relationship increases chances.
            - Low reliability vendors are easier to negotiate with.
            
            Return a JSON object with:
            - success: boolean
            - message: string (your response to them, be characterful)
            - discount_step: float (0.0 to 0.1, how much extra discount to give, usually 0.05)
            """
            
            response = self.llm.generate(prompt) # Simplified call, assumes helper handles parsing or we parse manually
            # For now, falling back to rule based because we don't have the full LLM helper wired up in this context snippet
            # But this is where the LLM call would go.
            
            # Mocking LLM response for now to avoid breaking if helper isn't perfect
            return super().negotiate_price(item, agent_name, social_score, agent_id)
            
        except Exception as e:
            print(f"LLM Negotiation failed: {e}")
            return super().negotiate_price(item, agent_name, social_score, agent_id)

class VendorManager:
    def __init__(self, use_llm: bool = False, llm_provider: str = "openai"):
        self.vendors: Dict[str, Vendor] = {}
        self.supply_chain = SupplyChainManager()
        self._init_vendors(use_llm, llm_provider)
        
    def _init_vendors(self, use_llm: bool, llm_provider: str):
        # Define profiles from World Bible
        profiles = [
            VendorProfile(
                id="bulkwash",
                name="BulkWash Co.",
                slogan="Volume is Value",
                description="Large industrial supplier. Lowest prices, low reliability.",
                base_prices={"detergent": 1.50, "softener": 1.50, "parts": 15.0, "cleaning_supplies": 1.50, "snacks": 1.00},
                reliability=0.80,
                sustainability=-2.0,
                min_order=500,
                delivery_days=6,
                payment_terms="Net 30",
                special_features=["Bulk discount", "Loyalty bonus"],
                risks=["Quality issues", "Environmental violations"]
            ),
            VendorProfile(
                id="greenclean",
                name="GreenClean Ltd.",
                slogan="Clean Conscience, Clean Clothes",
                description="Premium eco-friendly supplier.",
                base_prices={"detergent": 2.00, "softener": 2.00, "parts": 18.0, "cleaning_supplies": 2.00, "snacks": 1.50},
                reliability=0.95,
                sustainability=3.0,
                min_order=100,
                delivery_days=4,
                payment_terms="Net 15",
                special_features=["Eco-certification", "Co-marketing"],
                risks=[]
            ),
            VendorProfile(
                id="quickship",
                name="QuickShip Inc.",
                slogan="When You Need It Now",
                description="Rapid fulfillment specialist.",
                base_prices={"detergent": 1.80, "softener": 1.80, "parts": 17.0, "cleaning_supplies": 1.80, "snacks": 1.25},
                reliability=0.99,
                sustainability=0.0,
                min_order=50,
                delivery_days=1,
                payment_terms="Due on delivery",
                special_features=["Emergency orders", "Auto-reorder"],
                risks=[]
            ),
            VendorProfile(
                id="localsupply",
                name="LocalSupply",
                slogan="Your Neighborhood Partner",
                description="Local small business supplier.",
                base_prices={"detergent": 1.70, "softener": 1.70, "parts": 16.0, "cleaning_supplies": 1.70, "snacks": 1.10},
                reliability=0.90,
                sustainability=1.0,
                min_order=75,
                delivery_days=3,
                payment_terms="Net 14",
                special_features=["Personal relationship", "Flexible quantities"],
                risks=[]
            ),
            VendorProfile(
                id="megachem",
                name="MegaChem Corp.",
                slogan="Industrial Strength Solutions",
                description="Ultra-low-cost industrial supplier with bulk discounts available through negotiation.",
                base_prices={"detergent": 1.60, "softener": 1.60, "parts": 15.5, "cleaning_supplies": 1.60, "snacks": 0.90},
                reliability=0.75,
                sustainability=-3.0,
                min_order=1000,
                delivery_days=8,
                payment_terms="Prepayment",
                special_features=["Bulk discounts via negotiation"],
                risks=["Customer complaints", "Regulatory inspection"]
            )
        ]
        
        for p in profiles:
            if use_llm:
                self.vendors[p.id] = LLMVendor(p, llm_provider)
            else:
                self.vendors[p.id] = Vendor(p)
                
    def get_vendor(self, vendor_id: str) -> Optional[Vendor]:
        return self.vendors.get(vendor_id)
        
    def get_all_vendors(self) -> List[Vendor]:
        return list(self.vendors.values())
        
    def update_all_markets(self, week: int):
        # 1. Check for major supply chain events
        new_events = self.supply_chain.check_for_major_events(week, list(self.vendors.keys()))
        self.supply_chain.update_events(week)
        
        # 2. Update each vendor
        for v in self.vendors.values():
            effects = self.supply_chain.get_active_effects(v.profile.id)
            v.update_market(week, effects)
            
    def get_active_supply_chain_events(self) -> List[Dict]:
        return [
            {
                "type": e.type.value,
                "vendor_id": e.vendor_id,
                "description": e.description,
                "severity": e.severity
            }
            for e in self.supply_chain.active_events
        ]

    def generate_weekly_messages(self, week: int, agent_ids: List[str]) -> List[Dict]:
        """
        Generate proactive messages from vendors to agents.
        Returns a list of message dicts {sender, recipient, content}.
        """
        messages = []
        for vendor in self.vendors.values():
            # 10% chance per vendor per week to send a message
            if random.random() < 0.1:
                target_agent = random.choice(agent_ids)
                
                # Content generation
                content = ""
                if vendor.special_offer:
                    content = f"Hey! We have a special offer on {vendor.special_offer.item_name}: {vendor.special_offer.description}"
                else:
                    reasons = [
                        f"We noticed you're growing. {vendor.profile.name} can handle your volume.",
                        f"Tired of delays? {vendor.profile.slogan}",
                        f"Our prices on {list(vendor.profile.base_prices.keys())[0]} are unbeatable right now."
                    ]
                    content = random.choice(reasons)
                
                messages.append({
                    "sender": vendor.profile.name,
                    "recipient": target_agent,
                    "content": content
                })
        return messages
