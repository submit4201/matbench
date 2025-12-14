from typing import List, Dict, Any
import uuid
from src.engine.actions.registry import ActionRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent
from src.models.events.commerce import PriceSetEvent, SupplyOrdered, NegotiationRequested, BuyoutOfferSent
from src.models.events.finance import FundsTransferred

@ActionRegistry.register("SET_PRICE")
def handle_set_price(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    new_price = float(payload.get("amount", state.price))

    if new_price < 0:
        return []

    return [PriceSetEvent(
        week=week,
        agent_id=state.id,
        new_price=new_price,
        old_price=state.price
    )]

@ActionRegistry.register("BUY_SUPPLIES")
def handle_buy_inventory(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    item = payload.get("item")
    qty = int(payload.get("quantity", 0))
    vendor_id = payload.get("vendor_id", "bulkwash")
    vendor_manager = context.get("vendor_manager")
    
    # Calculate Dynamic Cost
    calculated_cost = 0.0
    if vendor_manager:
        vendor = vendor_manager.get_vendor(vendor_id)
        if vendor:
             # Use vendor price logic (negotiated or base)
             unit_price = vendor.get_price(item, agent_id=state.id)
             calculated_cost = unit_price * qty
    
    # Fallback to payload cost if calculation failed (or for testing)
    # But prefer calculated cost to avoid "free supplies" exploit
    cost = calculated_cost if calculated_cost > 0 else float(payload.get("cost", 0))
    arrival_week = int(payload.get("arrival_week", week + 1))

    events = []

    # Financial Event
    events.append(FundsTransferred(
        week=week,
        agent_id=state.id,
        transaction_id=str(uuid.uuid4()),
        amount=-cost,
        category="expense",
        description=f"Ordered {qty} {item} from {vendor_id}"
    ))

    # Supply Order Event (Triggers logistics reaction)
    events.append(SupplyOrdered(
        week=week,
        agent_id=state.id,
        order_id=str(uuid.uuid4()),
        vendor_id=vendor_id,
        item=item,
        quantity=qty,
        cost=cost,
        arrival_week=arrival_week
    ))

    return events

@ActionRegistry.register("NEGOTIATE")
@ActionRegistry.register("NEGOTIATE_CONTRACT")
def handle_negotiate(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    item = payload.get("item", "soap")
    vendor_id = payload.get("vendor_id", "bulkwash")

    # 1. Validation (Pure)
    # We define that you can always REQUEST a negotiation.
    # Logic for "can you actually do it?" could be here if it depends only on State (e.g. cooldown).
    # For now, we assume requests are valid if they have minimum args.

    # Snapshot social score for the process
    social_score = state.social_score.total_score if hasattr(state.social_score, "total_score") else state.reputation

    return [
        NegotiationRequested(
            week=week,
            agent_id=state.id,
            negotiation_id=str(uuid.uuid4()),
            vendor_id=vendor_id,
            item_type=item,
            social_score_snapshot=social_score
        )
    ]

@ActionRegistry.register("INITIATE_BUYOUT")
def handle_initiate_buyout(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    target_id = payload.get("target")
    offer = float(payload.get("offer", 0))

    # Check bounds
    if offer <= 0: return []
    if state.balance < offer:
        # Optional: Emit "BuyoutFailedInsufficientFunds"
        return []

    return [
        BuyoutOfferSent(
            week=week,
            agent_id=state.id,
            proposal_id=str(uuid.uuid4()),
            target_agent_id=target_id,
            offer_amount=offer
        )
    ]
