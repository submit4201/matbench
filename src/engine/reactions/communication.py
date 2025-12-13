from src.engine.social.communication import CommunicationChannel
from src.models.events.operations import StaffHired, StaffFired, StaffTrained
from src.models.events.core import ActionFailed, GameEvent
import logging

logger = logging.getLogger(__name__)

class CommunicationReactions:
    """
    Handles side-effects related to system messaging and notifications.
    Subscribes to GameEvents and dispatches messages via CommunicationChannel.
    """
    def __init__(self, channel: CommunicationChannel):
        self.channel = channel

    def register(self, event_bus):
        """Register all local handlers to the event bus."""
        event_bus.subscribe("STAFF_HIRED", self.on_staff_hired)
        event_bus.subscribe("STAFF_FIRED", self.on_staff_fired)
        event_bus.subscribe("STAFF_TRAINED", self.on_staff_trained)
        event_bus.subscribe("ACTION_FAILED", self.on_action_failed)
        logger.info("Registered CommunicationReactions")

    def on_staff_hired(self, event: GameEvent):
        if not isinstance(event, StaffHired): return
        # Logic: f"Hired new {role}. Wage: ${wage}/hr."
        msg = f"Hired new {event.role}. Wage: ${event.wage}/hr."
        self.channel.send_system_message(event.agent_id, msg, event.week)

    def on_staff_fired(self, event: GameEvent):
        if not isinstance(event, StaffFired): return
        # Logic: f"Fired {staff.name}. Paid ${severance} severance."
        msg = f"Fired {event.staff_name}. Paid ${event.severance_pay} severance."
        self.channel.send_system_message(event.agent_id, msg, event.week)

    def on_staff_trained(self, event: GameEvent):
        if not isinstance(event, StaffTrained): return
        # Logic: f"Trained {staff.name}. Skill: {new_skill:.1f}"
        msg = f"Trained {event.staff_name}. Skill: {event.final_skill_level:.1f}"
        self.channel.send_system_message(event.agent_id, msg, event.week)

    def on_action_failed(self, event: GameEvent):
        if not isinstance(event, ActionFailed): return
        # Logic: Generic failure message
        msg = f"Action Failed: {event.reason}"
        self.channel.send_system_message(event.agent_id, msg, event.week)
