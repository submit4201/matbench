from typing import Dict, Any, List
import uuid
import logging

from src.engine.core.event_bus import EventBus
from src.engine.commerce.vendor import VendorManager
from src.models.events.core import GameEvent
from src.models.events.commerce import (
    NegotiationRequested, 
    NegotiationAttempted, 
    VendorNegotiationOutcome,
    VendorRelationshipChanged
)
from src.models.events.social import MessageSent
from src.models.events.finance import BillPaid, BillIgnored

logger = logging.getLogger(__name__)

class CommerceReactions:
    """
    Handles side-effects for commerce interactions, specifically:
    1. Async Negotiation Logic (triggered by NegotiationRequested)
    2. Dynamic Vendor Relationships (triggered by financial behavior)
    """

    def __init__(self, vendor_manager: VendorManager):
        self.vendor_manager = vendor_manager
    
    def register(self, bus: EventBus):
        """Register listeners for commerce workflows."""
        self.bus = bus
        bus.subscribe("NEGOTIATION_REQUESTED", self.on_negotiation_requested)
        bus.subscribe("BILL_PAID", self.on_bill_paid)
        bus.subscribe("BILL_IGNORED", self.on_bill_ignored)
        logger.info("Registered CommerceReactions")

    def on_negotiation_requested(self, event: GameEvent):
        """
        Process a negotiation request.
        Calculates success/fail using VendorManager (pure logic wrapper) and emits results.
        """
        if not isinstance(event, NegotiationRequested): return

        vendor_id = event.vendor_id
        vendor = self.vendor_manager.get_vendor(vendor_id)
        
        if not vendor:
            logger.warning(f"Negotiation requested for unknown vendor: {vendor_id}")
            return # Or emit Failure event?

        # Execute Logic (Side Effect: RNG + potential internal vendor state drift if legacy)
        #Ideally Vendor.negotiate_price should be pure, but for now we wrap it.
        result = vendor.negotiate_price(
            item=event.item_type, 
            agent_name="Player", # Todo: Fetch real name if available?
            social_score=event.social_score_snapshot,
            agent_id=event.agent_id
        )
        
        # 1. Emit Attempt Record
        attempt_evt = NegotiationAttempted(
            week=event.week,
            agent_id=event.agent_id,
            negotiation_id=event.negotiation_id,
            vendor_id=vendor_id,
            item_type=event.item_type,
            success=result["success"],
            negotiation_power=event.social_score_snapshot
        )
        
        # 2. Emit Outcome (State Change)
        outcome_evt = VendorNegotiationOutcome(
            week=event.week,
            agent_id=event.agent_id,
            vendor_id=vendor_id,
            success=result["success"],
            new_price_multiplier=result.get("discount_multiplier", 1.0) if result["success"] else 1.0,
            message=result["message"]
        )
        
        # 3. Emit Message (Feedback to User)
        msg_evt = MessageSent(
            week=event.week,
            agent_id=event.agent_id,
            msg_id=str(uuid.uuid4()),
            recipients=[event.agent_id],
            channel="email",
            content=f"From: {vendor.profile.name}\n\n{result['message']}",
            intent="negotiation_outcome"
        )
        
        # Dispatch all
        # Note: In a real EventBus, we'd need a way to publish. 
        # Assuming the bus object passed to `register` is reference held by Engine,
        # OR we need a reference to the BUS to publish.
        # BUT: The `bus` arg in `register` is a local var. 
        # Standard pattern: Component should have `self.bus = bus`?
        # Or Engine handles return values? 
        # If this is a Synchronous Event Bus, publishing inside a handler might recurse.
        # We need to verify how `EventBus` works. If it just calls callbacks, we need access to it.
        # I will check `src/engine/core/event_bus.py`.
        # For now, I'll assume we need to store the bus reference.
        self._publish_if_safe(attempt_evt)
        self._publish_if_safe(outcome_evt)
        self._publish_if_safe(msg_evt)

    def on_bill_paid(self, event: GameEvent):
        """Improve trust when bills are paid."""
        # Simple Logic: If bill category matches a vendor, boost them.
        # But bills often generic. 
        pass 

    def on_bill_ignored(self, event: GameEvent):
        """Decrease trust."""
        pass

    def _publish_if_safe(self, event: GameEvent):
        if hasattr(self, "bus") and self.bus:
            self.bus.publish(event)
        else:
            logger.error("EventBus not connected to CommerceReactions")

