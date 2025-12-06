import pytest
from src.engine.customer import Customer, Persona
from src.world.laundromat import LaundromatState
from src.world.ticket import TicketType

def test_customer_irrationality():
    # Create a "Karen" customer (high irrationality)
    customer = Customer("c1")
    customer.persona = Persona("Karen", 0.4, 0.8, 0.1, 0.1, irrationality_factor=1.0)
    
    # Create a perfect laundromat
    laundromat = LaundromatState(name="Perfect Laundry", id="l1")
    laundromat.reputation = 100
    laundromat.price = 0.1 # Super cheap
    laundromat.inventory["soap"] = 100
    
    # Test Drama Event (20% chance per visit if irrational)
    # We force it by running multiple times
    drama_triggered = False
    for i in range(50):
        result = customer.visit_laundromat(laundromat, week=1)
        if not result and len(laundromat.tickets) > 0:
            last_ticket = laundromat.tickets[-1]
            if "[DRAMA]" in last_ticket.description:
                drama_triggered = True
                break
    
    assert drama_triggered, "Karen should have caused drama eventually"

def test_bias_mechanic():
    customer = Customer("c2")
    customer.persona.irrationality_factor = 0.0 # Rational for this test
    
    laundromat = LaundromatState(name="Test Laundry", id="l2")
    
    # Initial visit - good
    customer.record_experience(laundromat.id, is_good=True, week=1)
    assert customer.bias_map[laundromat.id] > 0
    
    # Bad visit
    customer.record_experience(laundromat.id, is_good=False, week=2)
    # Should decrease bias
    assert customer.bias_map[laundromat.id] < 0.1 # Was 0.1, -0.2 = -0.1

if __name__ == "__main__":
    test_customer_irrationality()
    test_bias_mechanic()
    print("All customer tests passed!")
