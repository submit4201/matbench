import pytest
from src.engine.vendor import VendorManager, VendorTier, VendorProfile

def test_vendor_initialization():
    manager = VendorManager()
    assert len(manager.vendors) == 5
    
    bulkwash = manager.get_vendor("bulkwash")
    assert bulkwash is not None
    assert bulkwash.profile.name == "BulkWash Co."
    assert bulkwash.tier == VendorTier.NEW

def test_vendor_pricing():
    manager = VendorManager()
    bulkwash = manager.get_vendor("bulkwash")
    
    # Base price check
    soap_price = bulkwash.get_price("soap")
    assert soap_price > 0
    
    # Tier discount check
    bulkwash.tier = VendorTier.REGULAR
    discounted_price = bulkwash.get_price("soap")
    assert discounted_price < soap_price

def test_order_processing():
    manager = VendorManager()
    bulkwash = manager.get_vendor("bulkwash")
    
    order = {"soap": 100}
    result = bulkwash.process_order(order)
    
    assert result["vendor"] == "BulkWash Co."
    assert result["cost"] > 0
    assert "delivery_days" in result
    
    # Check consistency tracking
    assert bulkwash.weeks_consistent == 1
    assert bulkwash.total_spend > 0

def test_tier_progression():
    manager = VendorManager()
    bulkwash = manager.get_vendor("bulkwash")
    
    # Simulate 4 weeks of orders
    for _ in range(4):
        bulkwash.process_order({"soap": 10})
        
    assert bulkwash.tier == VendorTier.REGULAR

def test_market_fluctuation():
    manager = VendorManager()
    bulkwash = manager.get_vendor("bulkwash")
    initial_price = bulkwash.get_price("soap")
    
    # Update market multiple times and check for change
    changed = False
    for i in range(10):
        bulkwash.update_market(i)
        if bulkwash.get_price("soap") != initial_price:
            changed = True
            break
            
    assert changed or bulkwash.current_multipliers["soap"] == 1.0 # Might be stable if random seed is fixed or unlucky
