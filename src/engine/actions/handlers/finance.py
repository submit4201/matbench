from typing import List, Dict, Any
import uuid
from src.engine.actions.registry import ActionRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent
from src.models.events.finance import FundsTransferred, BillPaid, LoanApplied, BuildingPurchased

@ActionRegistry.register("PAY_BILL")
def handle_pay_bill(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    bill_id = payload.get("bill_id")

    # 1. Validation: Use State Source of Truth
    bill = next((b for b in state.bills if b.id == bill_id), None)

    if not bill:
        return [] # Or ActionFailed? For now silent fail if bill gone.

    if bill.is_paid:
        return []

    amount = bill.amount

    if state.balance < amount:
        return [] # Fail silently or ActionFailed (Legacy returned False)

    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-amount,
            category="liability",
            description=f"Paid Bill {bill.name}"
        ),
        BillPaid(
            week=week,
            agent_id=state.id,
            bill_id=bill_id,
            amount_paid=amount,
            payment_week=week,
            was_late=week > bill.due_week
        )
    ]

@ActionRegistry.register("BUY_BUILDING")
def handle_buy_building(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    price = float(payload.get("price", 0))
    listing_id = payload.get("listing_id")

    if price <= 0 or state.balance < price:
        return []

    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-price,
            category="real_estate",
            description=f"Purchased Building {listing_id}"
        ),
        BuildingPurchased(
            week=week,
            agent_id=state.id,
            building_id=listing_id, # Simplified: ID matches listing
            price=price,
            location_multiplier=1.0
        )
    ]

@ActionRegistry.register("APPLY_FOR_LOAN")
def handle_apply_for_loan(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    loan_type = payload.get("loan_type", "equipment_loan")
    amount = float(payload.get("amount", 5000.0))

    # Check max loans? (Logic for handler vs reaction)
    # We allow application, reaction decides approval.

    return [
        LoanApplied(
            week=week,
            agent_id=state.id,
            application_id=str(uuid.uuid4()),
            loan_type=loan_type,
            amount=amount
        )
    ]

@ActionRegistry.register("MAKE_PAYMENT") # For Credit Payment
def handle_make_payment(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    # This handler is tricky because it depends on Credit System "Due Payments" logic which is complex.
    # However, if we just want to pay X amount to Loan Y, we can emit FundsTransferred + LoanPaymentProcessed.
    # But LoanPaymentProcessed logic (splitting principal/interest) is in Credit System.
    #
    # APPROACH: Emit generic "CreditPaymentInitiated".
    # Reaction calls `credit_system.make_payment` -> Emits "LoanPaymentProcessed".
    #
    # Wait, we don't have "CreditPaymentInitiated".
    # We can use FundsTransferred?
    # If we iterate cleanly:
    # 1. Deduct funds (FundsTransferred).
    # 2. Emit "BillPaid" (generic) or new "LoanPaymentInitiated".
    # Reaction listens and updates credit system.
    #
    # Simpler: Call credit_system in Reaction to `FundsTransferred`? No, side effect heavy.
    #
    # Let's rely on the API flow for now: `take_action` -> standard action.
    # If we use `FundsTransferred` with category `repayment` and `related_entity_id`=payment_id.
    # `FinanceReactions` listens to `FundsTransferred` (checking category) and calls `credit_system`.

    payment_id = payload.get("payment_id")
    amount = float(payload.get("amount", 0))

    if amount <= 0 or state.balance < amount:
         return []

    # We trust payload for now.
    return [
        FundsTransferred(
             week=week,
             agent_id=state.id,
             transaction_id=str(uuid.uuid4()),
             amount=-amount,
             category="repayment",
             description=f"Loan Repayment",
             related_entity_id=payment_id
        )
    ]
