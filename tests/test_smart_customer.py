from src.engine.customer import Customer
from src.world.laundromat import LaundromatState

def test_customer_thoughts():
    customer = Customer("c1")
    laundromat = LaundromatState(id="p1", name="Test Laundromat", price=5.0, social_score=50)
    
    # Test initial thought
    assert customer.current_thought == ""
    
    # Test decision making thought
    choice = customer.decide_laundromat([laundromat])
    print(f"Choice: {choice}")
    print(f"Thought: {customer.current_thought}")
    assert "Test Laundromat" in customer.current_thought
    
    # Test visit thought (success)
    laundromat.inventory["soap"] = 10
    customer.visit_laundromat(laundromat, 1)
    assert "Great wash" in customer.current_thought or "Fresh and clean" in customer.current_thought

def test_customer_reaction_to_no_soap():
    customer = Customer("c2")
    laundromat = LaundromatState(id="p1", name="No Soap Laundry", price=5.0, social_score=50)
    laundromat.inventory["soap"] = 0
    
    customer.visit_laundromat(laundromat, 1)
    assert "out of soap" in customer.current_thought
    assert len(laundromat.tickets) > 0

if __name__ == "__main__":
    print("Running Customer Thoughts Test...")
    test_customer_thoughts()
    print("PASS: Customer Thoughts")
    
    print("Running Customer Reaction Test...")
    test_customer_reaction_to_no_soap()
    print("PASS: Customer Reaction")
