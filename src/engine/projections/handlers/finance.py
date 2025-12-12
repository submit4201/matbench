from src.engine.projections.registry import EventRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent

@EventRegistry.register("TRANSACTION_RECORDED")
@EventRegistry.register("FUNDS_TRANSFERRED")
def apply_funds_transfer(state: LaundromatState, event: GameEvent):
    payload = event.payload
    amount = getattr(event, "amount", payload.get("amount", 0))
    category = getattr(event, "category", payload.get("category", "misc"))
    desc = getattr(event, "description", payload.get("description", ""))
    
    # Use week from event
    state.agent.ledger.add(amount, category, desc, event.week)

@EventRegistry.register("BILL_PAID")
def apply_bill_paid(state: LaundromatState, event: GameEvent):
    # Currently no-op in state projection as ledger handles the money.
    # Future: mark specific bill object as paid if we tracked them individually in state list.
    pass

@EventRegistry.register("LOAN_ORIGINATED")
def apply_loan(state: LaundromatState, event: GameEvent):
    # Logic to add loan to state.agent.loans
    # Current LaundromatState doesn't expose loans list directly on agent (it's in FinancialSystem or ledger?), 
    # but let's check AgentState definition or just implement the stub as per user example "pass".
    # User example code was:
    # def apply_loan(state: LaundromatState, event: LoanOriginated):
    #    # Logic to add loan to state.agent.loans
    #    pass
    pass
