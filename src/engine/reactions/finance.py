from typing import List
from src.engine.core.event_bus import EventBus
from src.models.events.core import GameEvent
from src.models.events.finance import LoanApplied, LoanApproved, LoanDenied
from src.engine.social.communication import CommunicationSystem, MessageIntent
import uuid

class FinanceReactions:
    def __init__(self, bus: EventBus, credit_system, communication: CommunicationSystem):
        self.bus = bus
        self.credit_system = credit_system
        self.communication = communication
        
        # Subscribe
        self.bus.subscribe("LOAN_APPLIED", self.handle_loan_applied)
        self.bus.subscribe("LOAN_APPROVED", self.handle_loan_outcome)
        self.bus.subscribe("LOAN_DENIED", self.handle_loan_outcome)
        self.bus.subscribe("FUNDS_TRANSFERRED", self.handle_repayment)

    def handle_loan_applied(self, event: LoanApplied):
        """Process loan application against credit system."""
        # Use Credit System logic
        result = self.credit_system.apply_for_loan(
            agent_id=event.agent_id,
            loan_type=event.loan_type,
            amount=event.amount,
            current_week=event.week
        )
        
        if result.get("approved"):
            # Emit Approved Event
            self.bus.publish(LoanApproved(
                week=event.week,
                agent_id=event.agent_id,
                application_id=event.application_id,
                loan_id=result.get("loan_id", str(uuid.uuid4())),
                amount=event.amount,
                interest_rate=result.get("interest_rate", 0.0),
                weekly_payment=result.get("weekly_payment", 0.0)
            ))
        else:
            # Emit Denied Event
            self.bus.publish(LoanDenied(
                week=event.week,
                agent_id=event.agent_id,
                application_id=event.application_id,
                reason=result.get("reason", "Credit criteria not met")
            ))

    def handle_loan_outcome(self, event: GameEvent):
        """Notify user of loan outcome."""
        if isinstance(event, LoanApproved):
            self.communication.send_system_message(
                recipient_id=event.agent_id,
                content=f"🎉 Loan Approved!\n\nAmount: ${event.amount:,.2f}\nRate: {event.interest_rate*100:.1f}%\nWeekly Payment: ${event.weekly_payment:,.2f}",
                week=event.week,
                intent=MessageIntent.FORMAL_BUSINESS
            )
        elif isinstance(event, LoanDenied):
            self.communication.send_system_message(
                recipient_id=event.agent_id,
                content=f"❌ Loan Denied\n\nReason: {event.reason}",
                week=event.week,
                intent=MessageIntent.FORMAL_BUSINESS
            )

    def handle_repayment(self, event: GameEvent):
        """Sync repayment to credit system."""
        # Using generic event for FUNDS_TRANSFERRED or specific type check
        if event.category == "repayment" and event.amount < 0:
            # Amount is negative in FundsTransferred for expense
            payment_amount = abs(event.amount)
            payment_id = event.related_entity_id
            
            # Delegate to credit system
            self.credit_system.make_payment(
                agent_id=event.agent_id,
                payment_id=payment_id,
                amount=payment_amount,
                current_week=event.week
            )
