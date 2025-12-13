from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.projections.registry import EventRegistry

if TYPE_CHECKING:
    from src.models.world import LaundromatState
    from src.models.events.core import GameEvent

@EventRegistry.register("INVENTORY_STOCKED")
@EventRegistry.register("INVENTORY_UPDATED")
def apply_inventory_stock(state: LaundromatState, event: GameEvent):
    payload = event.payload
    item = getattr(event, "item_type", payload.get("item"))
    qty = getattr(event, "quantity", payload.get("quantity", 0))
    
    current = state.primary_location.inventory.get(item, 0)
    state.primary_location.inventory[item] = max(0, current + qty)

@EventRegistry.register("PRICE_SET")
def apply_price_set(state: LaundromatState, event: GameEvent):
    payload = event.payload
    val = getattr(event, "new_price", payload.get("price"))
    if val is not None:
        state.primary_location.price = val


@EventRegistry.register("SHIPMENT_RECEIVED")
def apply_shipment_received(state: LaundromatState, event: GameEvent):
    """Apply inventory additions from received shipments."""
    payload = event.payload if hasattr(event, "payload") else {}
    items_received = getattr(event, "items_received", payload.get("items_received", {}))
    
    for item, qty in items_received.items():
        current = state.primary_location.inventory.get(item, 0)
        state.primary_location.inventory[item] = current + qty


@EventRegistry.register("DELIVERY_PROCESSED")
def apply_delivery_processed(state: LaundromatState, event: GameEvent):
    """Remove processed delivery from pending list."""
    payload = event.payload if hasattr(event, "payload") else {}
    delivery_id = getattr(event, "delivery_id", payload.get("delivery_id"))
    
    state.primary_location.pending_deliveries = [
        d for d in state.primary_location.pending_deliveries 
        if d.get("id") != delivery_id
    ]


@EventRegistry.register("DELIVERY_LIST_UPDATED")
def apply_delivery_list_updated(state: LaundromatState, event: GameEvent):
    """Update pending deliveries list after processing arrivals."""
    payload = event.payload if hasattr(event, "payload") else {}
    remaining = getattr(event, "remaining_deliveries", payload.get("remaining_deliveries", []))
    state.primary_location.pending_deliveries = remaining


# --- Orphan Event Handlers (Future Feature Support) ---

@EventRegistry.register("ORDER_PLACED")
def apply_order_placed(state: LaundromatState, event: GameEvent):
    """Add order to pending deliveries."""
    payload = event.payload if hasattr(event, "payload") else {}
    state.primary_location.pending_deliveries.append({
        "order_id": getattr(event, "order_id", payload.get("order_id")),
        "vendor_id": getattr(event, "vendor_id", payload.get("vendor_id")),
        "items": getattr(event, "items", payload.get("items", {})),
        "arrival_week": getattr(event, "expected_delivery_date", payload.get("expected_delivery_date"))
    })


@EventRegistry.register("SHIPMENT_SHIPPED")
def apply_shipment_shipped(state: LaundromatState, event: GameEvent):
    """Stub for shipment tracking."""
    payload = event.payload if hasattr(event, "payload") else {}
    order_id = getattr(event, "order_id", payload.get("order_id"))
    
    for delivery in state.primary_location.pending_deliveries:
        if delivery.get("order_id") == order_id:
            delivery["status"] = "shipped"
            break


@EventRegistry.register("SUPPLY_CHAIN_DISRUPTION_STARTED")
def apply_supply_chain_disruption_started(state: LaundromatState, event: GameEvent):
    """Stub for disruption tracking."""
    payload = event.payload if hasattr(event, "payload") else {}
    item_type = getattr(event, "item_type", payload.get("item_type"))
    severity = getattr(event, "severity", payload.get("severity", "high"))
    
    if item_type:
        state.primary_location.supply_chain_status[item_type] = {
            "status": "disrupted",
            "severity": severity,
            "start_week": event.week
        }


@EventRegistry.register("SUPPLY_CHAIN_DISRUPTION_ENDED")
def apply_supply_chain_disruption_ended(state: LaundromatState, event: GameEvent):
    """Stub for disruption end."""
    payload = event.payload if hasattr(event, "payload") else {}
    item_type = getattr(event, "item_type", payload.get("item_type"))
    
    if item_type and item_type in state.primary_location.supply_chain_status:
        # Either remove or mark resolved
        del state.primary_location.supply_chain_status[item_type]


@EventRegistry.register("VENDOR_NEGOTIATION_STARTED")
def apply_vendor_negotiation_started(state: LaundromatState, event: GameEvent):
    """Stub for negotiation tracking."""
    payload = event.payload if hasattr(event, "payload") else {}
    negotiation_id = getattr(event, "negotiation_id", payload.get("negotiation_id"))
    vendor_id = getattr(event, "vendor_id", payload.get("vendor_id"))
    
    if negotiation_id:
        state.agent.active_negotiations[negotiation_id] = {
            "vendor_id": vendor_id,
            "status": "active",
            "attempts": 0,
            "start_week": event.week
        }


@EventRegistry.register("VENDOR_NEGOTIATION_OUTCOME")
def apply_vendor_negotiation_outcome(state: LaundromatState, event: GameEvent):
    """Update vendor discount after negotiation."""
    payload = event.payload if hasattr(event, "payload") else {}
    vendor_id = getattr(event, "vendor_id", payload.get("vendor_id"))
    new_multiplier = getattr(event, "new_price_multiplier", payload.get("new_price_multiplier"))
    
    if vendor_id and new_multiplier is not None:
        state.agent.vendor_discounts[vendor_id] = new_multiplier
        
    # Also log success/fail?
    success = getattr(event, "success", payload.get("success"))
    if success:
        # Improve relationship
        current_rel = state.agent.vendor_relationships.get(vendor_id, 0.5)
        state.agent.vendor_relationships[vendor_id] = min(1.0, current_rel + 0.1)


@EventRegistry.register("VENDOR_RELATIONSHIP_CHANGED")
def apply_vendor_relationship_changed(state: LaundromatState, event: GameEvent):
    """Update vendor relationship score."""
    payload = event.payload if hasattr(event, "payload") else {}
    vendor_id = getattr(event, "vendor_id", payload.get("vendor_id"))
    new_score = getattr(event, "new_score", payload.get("new_score"))
    if vendor_id and new_score is not None:
        state.agent.vendor_relationships[vendor_id] = new_score


@EventRegistry.register("NEGOTIATION_ATTEMPTED")
def apply_negotiation_attempted(state: LaundromatState, event: GameEvent):
    """Stub for negotiation tracking."""
    payload = event.payload if hasattr(event, "payload") else {}
    negotiation_id = getattr(event, "negotiation_id", payload.get("negotiation_id"))
    
    if negotiation_id and negotiation_id in state.agent.active_negotiations:
        state.agent.active_negotiations[negotiation_id]["attempts"] += 1
        state.agent.active_negotiations[negotiation_id]["last_attempt_week"] = event.week


@EventRegistry.register("VENDOR_DISCOUNT_GRANTED")
def apply_vendor_discount_granted(state: LaundromatState, event: GameEvent):
    """Update discount (alternate redundancy)."""
    payload = event.payload if hasattr(event, "payload") else {}
    vendor_id = getattr(event, "vendor_id", payload.get("vendor_id"))
    new_multiplier = getattr(event, "discount_multiplier", payload.get("discount_multiplier"))
    
    if vendor_id and new_multiplier is not None:
        state.agent.vendor_discounts[vendor_id] = new_multiplier


@EventRegistry.register("VENDOR_MARKET_UPDATED")
def apply_vendor_market_updated(state: LaundromatState, event: GameEvent):
    """Update vendor specific market data (prices, effects)."""
    payload = event.payload if hasattr(event, "payload") else {}
    vendor_id = getattr(event, "vendor_id", payload.get("vendor_id"))
    updates = getattr(event, "updates", payload.get("updates", {}))
    
    # Store in a cache or update known prices
    if not hasattr(state.agent, "vendor_market_data"):
        state.agent.vendor_market_data = {}
        
    state.agent.vendor_market_data[vendor_id] = updates


@EventRegistry.register("BUYOUT_OFFER_SENT")
def apply_buyout_offer_sent(state: LaundromatState, event: GameEvent):
    """Track sent buyout offers."""
    payload = event.payload if hasattr(event, "payload") else {}
    offer = {
        "id": getattr(event, "proposal_id", payload.get("proposal_id")),
        "target": getattr(event, "target_agent_id", payload.get("target_agent_id")),
        "amount": getattr(event, "offer_amount", payload.get("offer_amount")),
        "status": "pending",
        "week": event.week
    }
    state.agent.proposals.append(offer)


@EventRegistry.register("BUYOUT_OFFER_ACCEPTED")
def apply_buyout_offer_accepted(state: LaundromatState, event: GameEvent):
    """Handle accepted buyout."""
    payload = event.payload if hasattr(event, "payload") else {}
    proposal_id = getattr(event, "proposal_id", payload.get("proposal_id"))
    
    # Update proposal status
    for prop in state.agent.proposals:
        if prop.get("id") == proposal_id:
            prop["status"] = "accepted"
    
    # Actual merger logic (transferring assets) usually handled by `MERGER_COMPLETED` 
    # or specific asset transfer events. This just updates the proposal tracking.


@EventRegistry.register("BUYOUT_OFFER_REJECTED")
def apply_buyout_offer_rejected(state: LaundromatState, event: GameEvent):
    """Update buyout proposal status."""
    payload = event.payload if hasattr(event, "payload") else {}
    proposal_id = getattr(event, "proposal_id", payload.get("proposal_id"))
    
    for prop in state.agent.proposals:
        if prop.get("id") == proposal_id:
            prop["status"] = "rejected"
            break


@EventRegistry.register("BUYOUT_FAILED_INSUFFICIENT_FUNDS")
def apply_buyout_failed(state: LaundromatState, event: GameEvent):
    """Update buyout proposal status."""
    payload = event.payload if hasattr(event, "payload") else {}
    proposal_id = getattr(event, "proposal_id", payload.get("proposal_id"))
    
    for prop in state.agent.proposals:
        if prop.get("id") == proposal_id:
            prop["status"] = "failed_funds"
            break
