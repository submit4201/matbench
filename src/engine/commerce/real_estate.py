from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import random
import uuid

@dataclass
class Building:
    id: str
    name: str
    type: str = "commercial_storefront"  # storefront, warehouse, empty_lot
    condition: float = 1.0  # 0.0 to 1.0
    capacity_machines: int = 10
    capacity_storage: int = 100
    price: float = 50000.0
    location_multiplier: float = 1.0  # Affects customer traffic
    features: List[str] = field(default_factory=list) # e.g., "Main Street", "Parking Lot"

    @property
    def value(self) -> float:
        return self.price * self.condition

class RealEstateManager:
    """
    Manages the real estate market, generating listings and handling purchases.
    """
    def __init__(self):
        self.listings: List[Building] = []
        # Generate initial listings
        self.generate_listings(0)

    def generate_listings(self, current_week: int):
        """Generates new real estate listings based on the economy/randomness."""
        # Clean up old listings (chance to expire)
        self.listings = [l for l in self.listings if random.random() > 0.1]
        
        # Ensure minimum market depth
        target_listings = 5
        if len(self.listings) < target_listings:
             for _ in range(target_listings - len(self.listings)):
                self.listings.append(self._create_random_listing(current_week))

    def _create_random_listing(self, week: int) -> Building:
        types = [
            ("Small Storefront", 30000.0, 15, 0.8),
            ("Large Retail Space", 75000.0, 30, 1.2),
            ("Old Warehouse", 45000.0, 50, 0.6),
            ("Prime Corner Lot", 120000.0, 25, 1.5)
        ]
        
        chosen_name, base_price, cap, mult = random.choice(types)
        
        # Add variance
        price_variance = random.uniform(0.9, 1.1)
        condition = random.uniform(0.5, 1.0)
        
        unique_id = str(uuid.uuid4())[:8]
        
        return Building(
            id=unique_id,
            name=f"{chosen_name} {unique_id}",
            type="commercial",
            condition=condition,
            capacity_machines=cap,
            capacity_storage=cap * 5,
            price=base_price * price_variance,
            location_multiplier=mult
        )

    def get_listings(self) -> List[Building]:
        return self.listings

    def get_listing(self, listing_id: str) -> Optional[Building]:
        for l in self.listings:
            if l.id == listing_id:
                return l
        return None

    def process_purchase(self, listing_id: str) -> Optional[Building]:
        """
        Removes listing from market and returns the Building object.
        Returns None if not found.
        """
        for i, listing in enumerate(self.listings):
            if listing.id == listing_id:
                return self.listings.pop(i)
        return None
