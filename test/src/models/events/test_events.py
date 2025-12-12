from datetime import date, datetime

from src.models.events.core import GameEvent
from src.models.events.commerce import OrderPlaced, VendorNegotiationOutcome, DeliveryListUpdated
from src.models.events.finance import FundsTransferred, BillPaid, DailyRevenueProcessed, WeeklyReportGenerated, WeeklySpendingReset
from src.models.events.social import ScandalStarted, InvestigationOpened
from src.models.events.operations import StaffHired, MachineWearUpdated, MachinePurchased, CleanlinessUpdated, MarketingBoostDecayed
from src.models.events.world import TimeAdvanced


# --- Core Tests ---
def test_game_event_defaults():
    """Test default values for GameEvent."""
    event = GameEvent(week=1, type="GENERIC_EVENT", agent_id="agent1")
    assert isinstance(event.event_id, str)
    assert isinstance(event.timestamp, datetime)
    assert event.week == 1
    assert event.agent_id == "agent1"
    assert event.type == "GENERIC_EVENT"
    assert event.payload == {}
    assert event.metadata == {}

# --- Commerce Tests ---
def test_order_placed():
    event = OrderPlaced(
        week=1,
        agent_id="a1",
        order_id="o1",
        vendor_id="v1",
        items={"item1": 10},
        total_cost=100.0,
        expected_delivery_date=date(2025, 1, 1)
    )
    assert event.type == "ORDER_PLACED"
    assert event.total_cost == 100.0

def test_vendor_negotiation_outcome():
    event = VendorNegotiationOutcome(
        week=1,
        agent_id="a1",
        vendor_id="v1",
        success=True,
        new_price_multiplier=0.9,
        message="Deal!"
    )
    assert event.new_price_multiplier == 0.9

def test_delivery_list_updated():
    """Test DeliveryListUpdated event."""
    event = DeliveryListUpdated(
        week=1,
        agent_id="a1",
        remaining_deliveries=[
            {"order_id": "o1", "items": {"detergent": 100}},
            {"order_id": "o2", "items": {"parts": 5}}
        ]
    )
    assert len(event.remaining_deliveries) == 2
    assert event.remaining_deliveries[0]["order_id"] == "o1"

# --- Finance Tests ---
def test_funds_transferred():
    event = FundsTransferred(
        week=1,
        agent_id="a1",
        transaction_id="t1",
        amount=-50.0,
        category="Expense",
        description="Test"
    )
    assert event.amount == -50.0

def test_bill_paid():
    event = BillPaid(
        week=1,
        agent_id="a1",
        bill_id="b1",
        amount_paid=100.0,
        payment_week=1,
        was_late=False
    )
    assert event.amount_paid == 100.0

def test_daily_revenue_processed():
    """Test DailyRevenueProcessed event."""
    event = DailyRevenueProcessed(
        week=1,
        agent_id="a1",
        revenue_wash=150.0,
        revenue_dry=100.0,
        revenue_vending=25.0,
        revenue_soap=15.0,
        revenue_sheets=10.0,
        customer_count=10,
        utility_cost=35.0,
        supply_cost=5.0
    )
    assert event.revenue_wash == 150.0
    assert event.customer_count == 10
    assert event.utility_cost == 35.0

def test_weekly_report_generated():
    """Test WeeklyReportGenerated event."""
    event = WeeklyReportGenerated(
        week=1,
        agent_id="a1",
        total_revenue=1000.0,
        total_cogs=200.0,
        gross_profit=800.0,
        expense_rent=300.0,
        expense_utilities=150.0,
        expense_labor=200.0,
        total_operating_expenses=700.0,
        operating_income=100.0,
        net_income=90.0,
        active_customers=50,
        parts_used=2
    )
    assert event.total_revenue == 1000.0
    assert event.active_customers == 50
    assert event.parts_used == 2

def test_weekly_spending_reset():
    """Test WeeklySpendingReset event."""
    event = WeeklySpendingReset(
        week=1,
        agent_id="a1",
        utility_total=150.0,
        supply_total=75.0
    )
    assert event.utility_total == 150.0
    assert event.supply_total == 75.0

# --- Social Tests ---
def test_scandal_started():
    event = ScandalStarted(
        week=1,
        agent_id="a1",
        scandal_type="FRAUD",
        severity=0.8,
        expiry_week=5,
        description="Bad stuff"
    )
    assert event.severity == 0.8
    assert event.expiry_week == 5

def test_investigation_opened():
    event = InvestigationOpened(
        week=1,
        agent_id="a1",
        case_id="c1",
        violation_type="PRICE_FIXING",
        evidence_strength=0.7
    )
    assert event.evidence_strength == 0.7

# --- Operations Tests ---
def test_staff_hired():
    event = StaffHired(
        week=1,
        agent_id="a1",
        staff_id="s1",
        role="Clerk",
        wage=15.0,
        skill_level=0.5
    )
    assert event.role == "Clerk"

def test_machine_wear_updated():
    event = MachineWearUpdated(
        week=1,
        agent_id="a1",
        machine_id="m1",
        wear_amount=0.1,
        current_condition=0.9
    )
    assert event.wear_amount == 0.1

def test_machine_purchased():
    event = MachinePurchased(
        week=1,
        agent_id="a1",
        machine_id="m2",
        model_type="Washer2000",
        price=1000.0,
        location_id="loc1"
    )
    assert event.price == 1000.0

def test_cleanliness_updated():
    """Test CleanlinessUpdated event."""
    event = CleanlinessUpdated(
        week=1,
        agent_id="a1",
        new_cleanliness=0.75,
        delta=-0.05,
        reason="weekly_decay"
    )
    assert event.new_cleanliness == 0.75
    assert event.delta == -0.05
    assert event.reason == "weekly_decay"

def test_marketing_boost_decayed():
    """Test MarketingBoostDecayed event."""
    event = MarketingBoostDecayed(
        week=1,
        agent_id="a1",
        decay_amount=0.1,
        remaining_boost=0.4
    )
    assert event.decay_amount == 0.1
    assert event.remaining_boost == 0.4

# --- World Tests ---
def test_time_advanced():
    event = TimeAdvanced(
        week=1,
        agent_id="system",
        new_week=2,
        new_day=1,
        season="Spring"
    )
    assert event.new_week == 2
    assert event.season == "Spring"

