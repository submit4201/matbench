import uuid
import logging

from src.engine.core.event_bus import EventBus
from src.engine.commerce.vendor import VendorManager
from src.models.events.core import GameEvent
from src.models.events.commerce import (
    NegotiationRequested, 
    NegotiationAttempted, 
    VendorNegotiationOutcome
)
from src.models.events.social import MessageSent

logger = logging.getLogger(__name__)

class CommerceReactions:
    """
    Handles side-effects for commerce interactions, specifically:
    1. Async Negotiation Logic (triggered by NegotiationRequested)
    2. Dynamic Vendor Relationships (triggered by financial behavior)
    """

    def __init__(self, vendor_manager: VendorManager):
        self.vendor_manager = vendor_manager
    
    def register(self, bus: EventBus, communication_system=None, calendar_system=None):
        """Register listeners for commerce workflows."""
        self.bus = bus
        self.communication = communication_system
        self.calendar = calendar_system
        
        bus.subscribe("NEGOTIATION_REQUESTED", self.on_negotiation_requested)
        bus.subscribe("SUPPLY_ORDERED", self.on_supply_ordered)
        bus.subscribe("BILL_PAID", self.on_bill_paid)
        bus.subscribe("BILL_IGNORED", self.on_bill_ignored)
        logger.info("Registered CommerceReactions")

    def on_supply_ordered(self, event: GameEvent):
        """Handle supply order confirmation and logistics."""
        # We assume event is SupplyOrdered type, though type hinting might be loose here
        if event.type != "SUPPLY_ORDERED": return

        # 1. Send Confirmation Message
        if self.communication:
            self.communication.send_message(
                sender_id="Supply Chain",
                recipient_id=event.agent_id,
                content=f"📦 **Order Confirmed**: {event.quantity} {event.item} from {event.vendor_id}. Expected delivery: Week {event.arrival_week}.",
                week=event.week,
                intent="notification"
            )

        # 2. Schedule Calendar Event
        # We need access to the calendar system. Assuming we can pass it or get it.
        # Ideally, CalendarSystem is passed in __init__ or register.
        if self.calendar:
            try:
                # We need to get the specific agent's calendar. 
                # Assuming calendar_system is a manager or we have a way.
                # If calendar_system IS the manager, maybe `get_calendar(agent_id)`?
                # Using reflection or assuming standard interface
                agent_calendar = self.calendar.get_calendar(event.agent_id) if hasattr(self.calendar, "get_calendar") else None
                
                if agent_calendar:
                    from src.engine.core.calendar import ActionCategory, ActionPriority
                    agent_calendar.schedule_action(
                        category=ActionCategory.SUPPLY_ORDER,
                        title=f"Delivery: {event.quantity} {event.item}",
                        description=f"Delivery from {event.vendor_id}",
                        week=event.arrival_week,
                        day=1,
                        priority=ActionPriority.MEDIUM,
                        current_week=event.week
                    )
            except Exception as e:
                logger.warning(f"Failed to schedule delivery on calendar: {e}")

    def on_negotiation_requested(self, event: GameEvent):
        """
        Process a negotiation request.
        Calculates success/fail using VendorManager (pure logic wrapper) and emits results.
        """
        if event.type != "NEGOTIATION_REQUESTED": return

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


