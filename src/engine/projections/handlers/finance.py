from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.projections.registry import EventRegistry

if TYPE_CHECKING:
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
    """Mark a bill as paid and deduct from ledger."""
    payload = event.payload if hasattr(event, "payload") else {}
    bill_id = getattr(event, "bill_id", payload.get("bill_id"))
    amount = getattr(event, "amount_paid", payload.get("amount_paid", 0))
    
    # Find and mark bill as paid
    for bill in state.bills:
        if bill.id == bill_id:
            bill.is_paid = True
            break
    
    # Deduct from ledger
    if amount > 0:
        state.agent.ledger.add(-amount, "expense", f"Bill Payment: {bill_id}", event.week)

@EventRegistry.register("BILL_IGNORED")
def apply_bill_ignored(state: LaundromatState, event: GameEvent):
    """Mark a bill as ignored/overdue (triggers credit score penalty)."""
    payload = event.payload if hasattr(event, "payload") else {}
    bill_id = getattr(event, "bill_id", payload.get("bill_id"))
    
    for bill in state.bills:
        if bill.id == bill_id:
            if hasattr(bill, "is_ignored"):
                bill.is_ignored = True
            break

@EventRegistry.register("LOAN_ORIGINATED")
def apply_loan(state: LaundromatState, event: GameEvent):
    pass

@EventRegistry.register("BILL_GENERATED")
def apply_bill_generated(state: LaundromatState, event: GameEvent):
    """Add a new bill to state.bills list."""
    from src.engine.finance import Bill
    
    payload = event.payload if hasattr(event, "payload") else {}
    
    bill = Bill(
        id=getattr(event, "bill_id", payload.get("bill_id", "")),
        name=getattr(event, "bill_type", payload.get("bill_type", "Unknown")),
        amount=getattr(event, "amount", payload.get("amount", 0)),
        due_week=getattr(event, "due_week", payload.get("due_week", event.week + 1)),
        category=getattr(event, "bill_type", payload.get("bill_type", "misc")).lower(),
        recipient_id="system",
        generated_week=event.week
    )
    state.bills.append(bill)

@EventRegistry.register("WEEKLY_SPENDING_RESET")
def apply_weekly_spending_reset(state: LaundromatState, event: GameEvent):
    """Reset weekly spending accumulators after bills have been generated."""
    state.primary_location.weekly_spending["utility"] = 0.0
    state.primary_location.weekly_spending["supplies"] = 0.0

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
    # Physics costs
    util_cost = get_val("utility_cost", 0.0)
    supply_cost = get_val("supply_cost", 0.0)
    
    day = getattr(event, "day", "?")
    
    total_rev = rev_wash + rev_dry + rev_soap + rev_sheets
    
    # 1. Update Ledger (Revenue Only - Costs are accrued or paid weekly)
    if total_rev > 0:
        state.agent.ledger.add(
            total_rev, 
            "revenue", 
            f"Daily Revenue (Day {day})", 
            event.week
        )

    # 2. Update Revenue Streams
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
    if soap_stream and soap_stream.price > 0 and rev_soap > 0:
        qty = int(rev_soap / soap_stream.price)
        cur = state.inventory.get("detergent", 0)
        state.inventory["detergent"] = max(0, cur - qty)
        
    # 5. Track Physics Costs (Accrue for Weekly Report)
    # Ensure weekly_spending dict exists (it was added to LocationState)
    if not hasattr(state.primary_location, "weekly_spending"):
        state.primary_location.weekly_spending = {}
    
    current_util = state.primary_location.weekly_spending.get("utility", 0.0)
    state.primary_location.weekly_spending["utility"] = current_util + util_cost
    
    current_supply = state.primary_location.weekly_spending.get("supplies", 0.0)
    state.primary_location.weekly_spending["supplies"] = current_supply + supply_cost


@EventRegistry.register("WEEKLY_REPORT_GENERATED")
def apply_weekly_report_generated(state: LaundromatState, event: GameEvent):
    """
    Apply all state mutations from weekly financial report generation.
    This handler centralizes: active_customers, parts inventory, stream resets, report archiving.
    """
    from src.engine.finance import FinancialReport
    
    payload = event.payload if hasattr(event, "payload") else {}
    
    def get_val(name, default=0.0):
        return getattr(event, name, payload.get(name, default))
    
    # 1. Update active customers
    state.active_customers = int(get_val("active_customers", 0))
    
    # 2. Deduct parts from inventory
    parts_used = int(get_val("parts_used", 0))
    if parts_used > 0:
        current_parts = state.inventory.get("parts", 0)
        state.inventory["parts"] = max(0, current_parts - parts_used)
    
    # 3. Reset revenue stream counters
    for stream in state.revenue_streams.values():
        stream.weekly_revenue = 0.0
    
    # 4. Reconstruct and archive financial report
    report = FinancialReport(week=event.week)
    report.revenue_wash = get_val("revenue_wash")
    report.revenue_dry = get_val("revenue_dry")
    report.revenue_vending = get_val("revenue_vending")
    report.revenue_premium = get_val("revenue_premium")
    report.revenue_membership = get_val("revenue_membership")
    report.revenue_other = get_val("revenue_other")
    report.total_revenue = get_val("total_revenue")
    report.cogs_supplies = get_val("cogs_supplies")
    report.cogs_vending = get_val("cogs_vending")
    report.total_cogs = get_val("total_cogs")
    report.gross_profit = get_val("gross_profit")
    report.expense_rent = get_val("expense_rent")
    report.expense_utilities = get_val("expense_utilities")
    report.expense_labor = get_val("expense_labor")
    report.expense_maintenance = get_val("expense_maintenance")
    report.expense_insurance = get_val("expense_insurance")
    report.expense_other = get_val("expense_other")
    report.total_operating_expenses = get_val("total_operating_expenses")
    report.operating_income = get_val("operating_income")
    report.expense_interest = get_val("expense_interest")
    report.net_income_before_tax = get_val("net_income_before_tax")
    report.tax_provision = get_val("tax_provision")
    report.net_income = get_val("net_income")
    report.cash_beginning = get_val("cash_beginning")
    report.cash_ending = get_val("cash_ending")
    
    state.financial_reports.append(report)


# --- Orphan Event Handlers (Future Feature Support) ---

@EventRegistry.register("BALANCE_ADJUSTED")
def apply_balance_adjusted(state: LaundromatState, event: GameEvent):
    """Manual balance adjustment (god-mode or corrections)."""
    payload = event.payload if hasattr(event, "payload") else {}
    amount = getattr(event, "adjustment_amount", payload.get("adjustment_amount", 0))
    state.balance += amount


@EventRegistry.register("TAX_ASSESSED")
def apply_tax_assessed(state: LaundromatState, event: GameEvent):
    """Stub for quarterly tax assessment."""
    pass  # Future: Track tax liability


@EventRegistry.register("TAX_FILING_STATUS_CHANGED")
def apply_tax_filing_status_changed(state: LaundromatState, event: GameEvent):
    """Stub for tax filing status."""
    pass


@EventRegistry.register("TAX_PENALTY_APPLIED")
def apply_tax_penalty_applied(state: LaundromatState, event: GameEvent):
    """Stub for tax penalties."""
    pass


@EventRegistry.register("FISCAL_QUARTER_ENDED")
def apply_fiscal_quarter_ended(state: LaundromatState, event: GameEvent):
    """Stub for fiscal quarter transitions."""
    pass


@EventRegistry.register("BANK_INITIALIZED")
def apply_bank_initialized(state: LaundromatState, event: GameEvent):
    """Initialize starting balance."""
    payload = event.payload if hasattr(event, "payload") else {}
    balance = getattr(event, "starting_balance", payload.get("starting_balance", 0))
    state.balance = balance


@EventRegistry.register("LOAN_PAYMENT_PROCESSED")
def apply_loan_payment_processed(state: LaundromatState, event: GameEvent):
    """Process loan payment - reduce balance."""
    payload = event.payload if hasattr(event, "payload") else {}
    loan_id = getattr(event, "loan_id", payload.get("loan_id"))
    remaining = getattr(event, "remaining_balance", payload.get("remaining_balance", 0))
    
    for loan in state.loans:
        if loan.id == loan_id:
            loan.balance = remaining
            break


@EventRegistry.register("LOAN_DEFAULTED")
def apply_loan_defaulted(state: LaundromatState, event: GameEvent):
    """Mark loan as defaulted."""
    payload = event.payload if hasattr(event, "payload") else {}
    loan_id = getattr(event, "loan_id", payload.get("loan_id"))
    
    for loan in state.loans:
        if loan.id == loan_id:
            if hasattr(loan, "is_defaulted"):
                loan.is_defaulted = True
            break


@EventRegistry.register("CREDIT_SCORE_UPDATED")
def apply_credit_score_updated(state: LaundromatState, event: GameEvent):
    """Update credit score."""
    payload = event.payload if hasattr(event, "payload") else {}
    new_score = getattr(event, "new_score", payload.get("new_score"))
    if hasattr(state, "credit_score") and new_score is not None:
        state.credit_score = new_score


@EventRegistry.register("REAL_ESTATE_MARKET_REFRESHED")
def apply_real_estate_market_refreshed(state: LaundromatState, event: GameEvent):
    """Stub for real estate market updates."""
    pass  # Market state is global, not per-agent


@EventRegistry.register("BUILDING_SOLD")
def apply_building_sold(state: LaundromatState, event: GameEvent):
    """Remove sold building from state."""
    payload = event.payload if hasattr(event, "payload") else {}
    building_id = getattr(event, "building_id", payload.get("building_id"))
    
    if hasattr(state.primary_location, "buildings"):
        state.primary_location.buildings = [
            b for b in state.primary_location.buildings if b.id != building_id
        ]


@EventRegistry.register("RENT_PAID")
def apply_rent_paid(state: LaundromatState, event: GameEvent):
    """Record rent payment in ledger."""
    payload = event.payload if hasattr(event, "payload") else {}
    amount = getattr(event, "amount", payload.get("amount", 0))
    
    state.agent.ledger.add(-amount, "expense", "Rent Payment", event.week)
