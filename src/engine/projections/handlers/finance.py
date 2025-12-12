from src.engine.projections.registry import EventRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent

@EventRegistry.register("TRANSACTION_RECORDED")
@EventRegistry.register("FUNDS_TRANSFERRED")
def apply_funds_transfer(state: LaundromatState, event: GameEvent):
    payload = event.payload if hasattr(event, "payload") else {}
    amount = getattr(event, "amount", payload.get("amount", 0))
    category = getattr(event, "category", payload.get("category", "misc"))
    desc = getattr(event, "description", payload.get("description", ""))
    
    # Use week from event
    state.agent.ledger.add(amount, category, desc, event.week)

@EventRegistry.register("BILL_PAID")
def apply_bill_paid(state: LaundromatState, event: GameEvent):
    pass

@EventRegistry.register("LOAN_ORIGINATED")
def apply_loan(state: LaundromatState, event: GameEvent):
    pass

@EventRegistry.register("DAILY_REVENUE_PROCESSED")
def apply_daily_revenue(state: LaundromatState, event: GameEvent):
    # Handle both direct attrs (Pydantic) and payload (Dict)
    payload = event.payload if hasattr(event, "payload") else {}
    def get_val(name, default=0.0):
        return getattr(event, name, payload.get(name, default))

    rev_wash = get_val("revenue_wash")
    rev_dry = get_val("revenue_dry")
    rev_soap = get_val("revenue_soap")
    rev_sheets = get_val("revenue_sheets")
    cust_count = int(get_val("customer_count", 0))
    day = getattr(event, "day", "?")
    
    total_rev = rev_wash + rev_dry + rev_soap + rev_sheets
    
    # 1. Update Ledger
    if total_rev > 0:
        state.agent.ledger.add(
            total_rev, 
            "revenue", 
            f"Daily Revenue (Day {day})", 
            event.week
        )

    # 2. Update Revenue Streams
    # Helper to update stream safely
    def update_stream(name, amount):
        s = state.revenue_streams.get(name)
        if s:
            s.weekly_revenue = (s.weekly_revenue or 0) + amount
            return s
        return None

    update_stream("Standard Wash", rev_wash)
    update_stream("Standard Dry", rev_dry)
    soap_stream = update_stream("Detergent Sale", rev_soap)
    sheets_stream = update_stream("Dryer Sheets", rev_sheets)
    
    # 3. Update Active Customers
    state.active_customers = cust_count
    
    # 4. Infer Inventory Usage from Revenue (Deterministic projection)
    # Detergent
    if soap_stream and soap_stream.price > 0 and rev_soap > 0:
        qty = int(rev_soap / soap_stream.price)
        cur = state.inventory.get("detergent", 0)
        state.inventory["detergent"] = max(0, cur - qty)
        
    # Note: Dryer sheets (inventory tracking not explicitly standardized in previous code but could match)
