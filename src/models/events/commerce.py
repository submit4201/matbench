from datetime import date
from typing import Dict, Optional, List, Any

from pydantic import Field

from .core import GameEvent


# --- Supply Chain Events ---

class OrderPlaced(GameEvent):
    """Event for when a supply order is placed."""
    type: str = "ORDER_PLACED"
    order_id: str
    vendor_id: str
    items: Dict[str, int]
    total_cost: float = Field(ge=0)
    expected_delivery_date: date


class ShipmentShipped(GameEvent):
    """Event for when a shipment is shipped."""
    type: str = "SHIPMENT_SHIPPED"
    order_id: str
    vendor_id: str
    shipped_items: Dict[str, int]
    actual_delivery_date: date


class ShipmentReceived(GameEvent):
    """Event for when a shipment is received."""
    type: str = "SHIPMENT_RECEIVED"
    order_id: str
    items_received: Dict[str, int]


class SupplyChainDisruptionStarted(GameEvent):
    """Event for when a supply chain disruption starts."""
    type: str = "SUPPLY_CHAIN_DISRUPTION_STARTED"
    disruption_event_id: str
    disruption_type: str  # Shortage/Spike
    vendor_id: Optional[str] = None
    severity: float
    effect_data: Dict[str, float]


class SupplyChainDisruptionEnded(GameEvent):
    """Event for when a supply chain disruption ends."""
    type: str = "SUPPLY_CHAIN_DISRUPTION_ENDED"
    disruption_event_id: str


# --- Vendor Events ---

class VendorNegotiationStarted(GameEvent):
    """Event for when a vendor negotiation starts."""
    type: str = "VENDOR_NEGOTIATION_STARTED"
    vendor_id: str
    item_type: str


class VendorNegotiationOutcome(GameEvent):
    """Event for the outcome of a vendor negotiation."""
    type: str = "VENDOR_NEGOTIATION_OUTCOME"
    vendor_id: str
    success: bool
    new_price_multiplier: float
    message: str


class VendorRelationshipChanged(GameEvent):
    """Event for when a vendor relationship score changes."""
    type: str = "VENDOR_RELATIONSHIP_CHANGED"
    vendor_id: str
    new_score: float
    change_reason: str



class NegotiationRequested(GameEvent):
    """Event for signaling intent to negotiate (Async/Reaction trigger)."""
    type: str = "NEGOTIATION_REQUESTED"
    negotiation_id: str
    vendor_id: str
    item_type: str
    offer_amount: Optional[float] = None
    social_score_snapshot: float = 0.0 # Snapshot for reaction logic


class NegotiationAttempted(GameEvent):
    """Event for logging a negotiation attempt details."""
    type: str = "NEGOTIATION_ATTEMPTED"
    vendor_id: str
    item_type: str
    success: bool
    negotiation_power: float


class VendorDiscountGranted(GameEvent):
    """Event for when a vendor grants a discount."""
    type: str = "VENDOR_DISCOUNT_GRANTED"
    vendor_id: str
    item_type: str
    discount_multiplier: float


class VendorMarketUpdated(GameEvent):
    """Event for when the vendor market updates prices/offers."""
    type: str = "VENDOR_MARKET_UPDATED"
    vendor_id: str
    price_multipliers: Dict[str, float]
    special_offer: Optional[str] = None


# --- Business / Buyout Events ---

class BuyoutOfferSent(GameEvent):
    """Event for sending a buyout offer."""
    type: str = "BUYOUT_OFFER_SENT"
    proposal_id: str
    target_agent_id: str
    offer_amount: float = Field(ge=0)


class BuyoutOfferAccepted(GameEvent):
    """Event for when a buyout offer is accepted."""
    type: str = "BUYOUT_OFFER_ACCEPTED"
    proposal_id: str
    final_transaction_amount: float = Field(ge=0)


class BuyoutOfferRejected(GameEvent):
    """Event for when a buyout offer is rejected."""
    type: str = "BUYOUT_OFFER_REJECTED"
    proposal_id: str
    rejection_reason: str


class BuyoutFailedInsufficientFunds(GameEvent):
    """Event for buyout failure due to funds."""
    type: str = "BUYOUT_FAILED_INSUFFICIENT_FUNDS"
    proposal_id: str
    required_amount: float
    available_amount: float


# --- Operations / Simple Commerce Events ---

class PriceSetEvent(GameEvent):
    """Event for changing the service price."""
    type: str = "PRICE_SET"
    new_price: float = Field(gt=0)
    old_price: float


class InventoryStocked(GameEvent):
    """Event for direct purchase of inventory (skipping complex order flow)."""
    type: str = "INVENTORY_STOCKED"
    item_type: str
    quantity: int = Field(gt=0)
    cost: float = Field(ge=0)


class DeliveryListUpdated(GameEvent):
    """Event for updating pending deliveries list after processing arrivals."""
    type: str = "DELIVERY_LIST_UPDATED"
    remaining_deliveries: List[Dict[str, Any]] = Field(default_factory=list)
