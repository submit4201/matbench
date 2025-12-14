from src.engine.core.event_bus import EventBus
from src.models.events.core import GameEvent
from src.engine.social.communication import CommunicationChannel, MessageIntent

class NotificationReactions:
    """
    Handles system notifications triggered by game events.
    Decoupled from Command Handlers.
    """
    def __init__(self, communication: CommunicationChannel):
        self.communication = communication

    def register(self, bus: EventBus):
        bus.subscribe("STAFF_HIRED", self.on_staff_hired)

    def on_staff_hired(self, event: GameEvent):
        """
        Notify the owner when a new staff member is hired.
        """
        payload = event.payload if hasattr(event, "payload") else {}
        
        # Extract data safely
        staff_name = getattr(event, "staff_name", payload.get("staff_name", "Unknown"))
        role = getattr(event, "role", payload.get("role", "staff"))
        wage = getattr(event, "wage", payload.get("wage", 0.0))
        agent_id = event.agent_id
        
        message = (
            f"✅ **Staff Hired**\n\n"
            f"You have hired **{staff_name}** as a {role}.\n"
            f"Wage: ${wage:.2f}/week."
        )
        
        self.communication.send_system_message(
            recipient_id=agent_id,
            content=message,
            week=event.week,
            intent=MessageIntent.NOTIFICATION
        )
