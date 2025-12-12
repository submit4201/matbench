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
        current = state.inventory.get(item, 0)
        state.inventory[item] = current + qty


@EventRegistry.register("DELIVERY_PROCESSED")
def apply_delivery_processed(state: LaundromatState, event: GameEvent):
    """Remove processed delivery from pending list."""
    payload = event.payload if hasattr(event, "payload") else {}
    delivery_id = getattr(event, "delivery_id", payload.get("delivery_id"))
    
    if hasattr(state, "pending_deliveries"):
        state.pending_deliveries = [
            d for d in state.pending_deliveries 
            if d.get("id") != delivery_id
        ]


@EventRegistry.register("DELIVERY_LIST_UPDATED")
def apply_delivery_list_updated(state: LaundromatState, event: GameEvent):
    """Update pending deliveries list after processing arrivals."""
    payload = event.payload if hasattr(event, "payload") else {}
    remaining = getattr(event, "remaining_deliveries", payload.get("remaining_deliveries", []))
    state.pending_deliveries = remaining


# --- Orphan Event Handlers (Future Feature Support) ---

@EventRegistry.register("ORDER_PLACED")
def apply_order_placed(state: LaundromatState, event: GameEvent):
    """Add order to pending deliveries."""
    payload = event.payload if hasattr(event, "payload") else {}
    if not hasattr(state, "pending_deliveries"):
        state.pending_deliveries = []
    state.pending_deliveries.append({
        "order_id": getattr(event, "order_id", payload.get("order_id")),
        "vendor_id": getattr(event, "vendor_id", payload.get("vendor_id")),
        "items": getattr(event, "items", payload.get("items", {})),
        "arrival_week": getattr(event, "expected_delivery_date", payload.get("expected_delivery_date"))
    })


@EventRegistry.register("SHIPMENT_SHIPPED")
def apply_shipment_shipped(state: LaundromatState, event: GameEvent):
    """Stub for shipment tracking."""
    pass


@EventRegistry.register("SUPPLY_CHAIN_DISRUPTION_STARTED")
def apply_supply_chain_disruption_started(state: LaundromatState, event: GameEvent):
    """Stub for disruption tracking."""
    pass


@EventRegistry.register("SUPPLY_CHAIN_DISRUPTION_ENDED")
def apply_supply_chain_disruption_ended(state: LaundromatState, event: GameEvent):
    """Stub for disruption end."""
    pass


@EventRegistry.register("VENDOR_NEGOTIATION_STARTED")
def apply_vendor_negotiation_started(state: LaundromatState, event: GameEvent):
    """Stub for negotiation tracking."""
    pass


@EventRegistry.register("VENDOR_NEGOTIATION_OUTCOME")
def apply_vendor_negotiation_outcome(state: LaundromatState, event: GameEvent):
    """Update vendor discount after negotiation."""
    payload = event.payload if hasattr(event, "payload") else {}
    vendor_id = getattr(event, "vendor_id", payload.get("vendor_id"))
    new_multiplier = getattr(event, "new_price_multiplier", payload.get("new_price_multiplier"))
    if hasattr(state, "vendor_discounts") and vendor_id and new_multiplier is not None:
        state.vendor_discounts[vendor_id] = new_multiplier


@EventRegistry.register("VENDOR_RELATIONSHIP_CHANGED")
def apply_vendor_relationship_changed(state: LaundromatState, event: GameEvent):
    """Update vendor relationship score."""
    payload = event.payload if hasattr(event, "payload") else {}
    vendor_id = getattr(event, "vendor_id", payload.get("vendor_id"))
    new_score = getattr(event, "new_score", payload.get("new_score"))
    if hasattr(state, "vendor_relationships") and vendor_id and new_score is not None:
        state.vendor_relationships[vendor_id] = new_score


@EventRegistry.register("NEGOTIATION_ATTEMPTED")
def apply_negotiation_attempted(state: LaundromatState, event: GameEvent):
    """Stub for negotiation tracking."""
    pass


@EventRegistry.register("VENDOR_DISCOUNT_GRANTED")
def apply_vendor_discount_granted(state: LaundromatState, event: GameEvent):
    """Stub for discount tracking."""
    pass


@EventRegistry.register("VENDOR_MARKET_UPDATED")
def apply_vendor_market_updated(state: LaundromatState, event: GameEvent):
    """Stub for market updates."""
    pass


@EventRegistry.register("BUYOUT_OFFER_SENT")
def apply_buyout_offer_sent(state: LaundromatState, event: GameEvent):
    """Stub for buyout tracking."""
    pass


@EventRegistry.register("BUYOUT_OFFER_ACCEPTED")
def apply_buyout_offer_accepted(state: LaundromatState, event: GameEvent):
    """Stub for buyout acceptance."""
    pass


@EventRegistry.register("BUYOUT_OFFER_REJECTED")
def apply_buyout_offer_rejected(state: LaundromatState, event: GameEvent):
    """Stub for buyout rejection."""
    pass


@EventRegistry.register("BUYOUT_FAILED_INSUFFICIENT_FUNDS")
def apply_buyout_failed(state: LaundromatState, event: GameEvent):
    """Stub for buyout failure."""
    pass
