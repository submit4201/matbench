"""
Test script to verify LLM NPC integration.
Tests customer, vendor, and event manager LLM functionality.
"""
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.engine.llm_npc_factory import NPCFactory
from src.world.laundromat import LaundromatState

load_dotenv()

def test_llm_customer():
    """Test LLM customer decision making."""
    print("\n=== Testing LLM Customer ===")
    
    # Create a single LLM customer
    customers = NPCFactory.create_customers(
        count=1,
        use_llm=True,
        llm_provider="openai",
        llm_ratio=1.0
    )
    
    customer = customers[0]
    print(f"Created customer: {customer.id} ({customer.persona.name})")
    print(f"Persona: price_sens={customer.persona.price_sensitivity:.2f}, "
          f"quality_sens={customer.persona.quality_sensitivity:.2f}")
    
    from src.world.social import SocialScore

    # Create test laundromats
    # Helper to create social score with specific total
    def create_score(total):
        # Distribute roughly evenly
        val = total / 5.0
        return SocialScore(val, val, val, val, val)

    laundromats = [
        LaundromatState(id="l1", name="Cheap Wash", price=3.0, social_score=create_score(40)),
        LaundromatState(id="l2", name="Luxury Suds", price=10.0, social_score=create_score(90)),
        LaundromatState(id="l3", name="Value Clean", price=6.0, social_score=create_score(70))
    ]
    
    # Test decision
    choice = customer.decide_laundromat(laundromats)
    print(f"\nCustomer chose: {choice.name if choice else 'None'}")
    if hasattr(customer, 'current_thought'):
        print(f"Thought: \"{customer.current_thought}\"")
    
    return choice is not None


def test_llm_vendor():
    """Test LLM vendor messaging and negotiation."""
    print("\n=== Testing LLM Vendor ===")
    
    vendor = NPCFactory.create_vendor(
        use_llm=True,
        vendor_name="Test Supplies Inc.",
        llm_provider="openai"
    )
    
    # Update market to generate offers
    vendor.update_market(week=1)
    
    # Test market message generation
    if hasattr(vendor, 'generate_market_message'):
        message = vendor.generate_market_message(week=1, laundromats_count=3)
        print(f"\nVendor message: {message}")
    
    # Test price negotiation
    if hasattr(vendor, 'negotiate_price'):
        final_price, nego_msg = vendor.negotiate_price(
            item="soap",
            agent_name="Test Laundromat",
            agent_social_score=75
        )
        print(f"\nNegotiation result: ${final_price:.2f}")
        print(f"Message: {nego_msg}")
    
    return True


def test_llm_event_manager():
    """Test LLM event manager."""
    print("\n=== Testing LLM Event Manager ===")
    
    event_manager = NPCFactory.create_event_manager(
        use_llm=True,
        llm_provider="openai"
    )
    
    # Generate some events
    events = event_manager.generate_random_events(
        week=1,
        agent_ids=["l1", "l2", "l3"]
    )
    
    if events:
        print(f"\nGenerated {len(events)} events:")
        for e in events:
            print(f"- {e.description}")
    else:
        print("\nNo events generated this week (random chance)")
    
    # Test world news generation
    if hasattr(event_manager, 'generate_world_news'):
        laundromats_info = [
            {'name': 'Cheap Wash', 'price': 3.0, 'social_score': 40},
            {'name': 'Luxury Suds', 'price': 10.0, 'social_score': 90},
            {'name': 'Value Clean', 'price': 6.0, 'social_score': 70}
        ]
        
        news = event_manager.generate_world_news(week=1, laundromats_info=laundromats_info)
        if news:
            print(f"\nWorld News: {news}")
    
    return True


def main():
    print("=" * 60)
    print("LLM NPC Integration Test")
    print("=" * 60)
    
    results = {
        "customer": False,
        "vendor": False,
        "event_manager": False
    }
    
    try:
        results["customer"] = test_llm_customer()
    except Exception as e:
        print(f"\n❌ Customer test failed: {e}")
    
    try:
        results["vendor"] = test_llm_vendor()
    except Exception as e:
        print(f"\n❌ Vendor test failed: {e}")
    
    try:
        results["event_manager"] = test_llm_event_manager()
    except Exception as e:
        print(f"\n❌ Event manager test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component.capitalize()}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("=" * 60))
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check output above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
