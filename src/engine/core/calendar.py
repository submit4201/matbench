# [ ]↔T: Calendar & Scheduling System
#   - [x] ScheduledAction dataclass
#   - [x] Calendar class with daily slots
#   - [x] Payment scheduling and reminders
#   - [x] Action planning interface
#   - [x] Week overview and progress tracking
# PRIORITY: P1 - Critical for planning dimension
# STATUS: Complete

"""
Calendar & Scheduling System

Provides a calendar interface for agents to:
- Schedule actions in advance
- Set payment reminders
- Plan their week
- Track deadlines

This tests strategic planning and time management
without restricting when actions can be taken.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class ActionCategory(Enum):
    """Categories of schedulable actions."""
    PAYMENT = "payment"
    SUPPLY_ORDER = "supply_order"
    MAINTENANCE = "maintenance"
    MARKETING = "marketing"
    STAFFING = "staffing"
    NEGOTIATION = "negotiation"
    ALLIANCE = "alliance"
    MEETING = "meeting"
    REMINDER = "reminder"
    CUSTOM = "custom"


class ActionPriority(Enum):
    """Priority levels for scheduled actions."""
    CRITICAL = "critical"  # Must do (e.g., loan payment)
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class ActionStatus(Enum):
    """Status of a scheduled action."""
    SCHEDULED = "scheduled"
    PENDING = "pending"   # Day arrived, not yet executed
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledAction:
    """A single scheduled action on the calendar."""
    id: str
    agent_id: str
    category: ActionCategory
    title: str
    description: str
    scheduled_week: int
    scheduled_day: int  # 1-7 (Mon-Sun)
    priority: ActionPriority
    status: ActionStatus = ActionStatus.SCHEDULED
    
    # Action data (parameters for execution)
    action_data: Dict[str, Any] = field(default_factory=dict)
    
    # Linked items
    linked_payment_id: Optional[str] = None
    linked_loan_id: Optional[str] = None
    
    # Recurring
    is_recurring: bool = False
    recurrence_weeks: int = 0  # How often to repeat
    
    # Metadata
    created_week: int = 1
    created_day: int = 1
    completed_week: Optional[int] = None
    completed_day: Optional[int] = None
    
    @property
    def day_name(self) -> str:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return days[self.scheduled_day - 1] if 1 <= self.scheduled_day <= 7 else "???"


@dataclass
class CalendarReminder:
    """A reminder notification."""
    id: str
    action_id: str
    reminder_week: int
    reminder_day: int
    message: str
    is_sent: bool = False


class AgentCalendar:
    """
    Calendar for a single agent.
    
    Provides:
    - Week-at-a-glance view
    - Action scheduling
    - Payment reminders
    - Progress tracking
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.scheduled_actions: Dict[str, ScheduledAction] = {}
        self.reminders: List[CalendarReminder] = []
        
    def schedule_action(
        self,
        category: ActionCategory,
        title: str,
        description: str,
        week: int,
        day: int,
        priority: ActionPriority = ActionPriority.MEDIUM,
        action_data: Dict[str, Any] = None,
        is_recurring: bool = False,
        recurrence_weeks: int = 0,
        current_week: int = 1,
        current_day: int = 1
    ) -> ScheduledAction:
        """Schedule a new action on the calendar."""
        action = ScheduledAction(
            id=str(uuid.uuid4())[:8],
            agent_id=self.agent_id,
            category=category,
            title=title,
            description=description,
            scheduled_week=week,
            scheduled_day=day,
            priority=priority,
            action_data=action_data or {},
            is_recurring=is_recurring,
            recurrence_weeks=recurrence_weeks,
            created_week=current_week,
            created_day=current_day
        )
        
        self.scheduled_actions[action.id] = action
        logger.info(f"Agent {self.agent_id} scheduled: {title} for Week {week} Day {day}")
        
        return action
    
    def schedule_payment_reminder(
        self,
        payment_id: str,
        loan_id: str,
        amount: float,
        due_week: int,
        current_week: int = 1
    ) -> ScheduledAction:
        """Schedule a payment with automatic reminder."""
        action = self.schedule_action(
            category=ActionCategory.PAYMENT,
            title=f"Loan Payment Due: ${amount:.2f}",
            description=f"Payment for loan {loan_id}",
            week=due_week,
            day=7,  # Sunday - end of week
            priority=ActionPriority.CRITICAL,
            action_data={"payment_id": payment_id, "loan_id": loan_id, "amount": amount},
            current_week=current_week
        )
        action.linked_payment_id = payment_id
        action.linked_loan_id = loan_id
        
        # Create reminder for 2 days before
        reminder = CalendarReminder(
            id=str(uuid.uuid4())[:8],
            action_id=action.id,
            reminder_week=due_week,
            reminder_day=5,  # Friday
            message=f"⚠️ Payment of ${amount:.2f} due in 2 days!"
        )
        self.reminders.append(reminder)
        
        return action
    
    def get_week_schedule(self, week: int) -> Dict[int, List[ScheduledAction]]:
        """Get all scheduled actions for a week, organized by day."""
        week_schedule = {day: [] for day in range(1, 8)}
        
        for action in self.scheduled_actions.values():
            if action.scheduled_week == week and action.status in [ActionStatus.SCHEDULED, ActionStatus.PENDING]:
                week_schedule[action.scheduled_day].append(action)
        
        # Sort each day by priority
        priority_order = {
            ActionPriority.CRITICAL: 0,
            ActionPriority.HIGH: 1,
            ActionPriority.MEDIUM: 2,
            ActionPriority.LOW: 3,
            ActionPriority.OPTIONAL: 4
        }
        for day in week_schedule:
            week_schedule[day].sort(key=lambda a: priority_order.get(a.priority, 5))
        
        return week_schedule
    
    def get_day_schedule(self, week: int, day: int) -> List[ScheduledAction]:
        """Get all scheduled actions for a specific day."""
        return [
            action for action in self.scheduled_actions.values()
            if action.scheduled_week == week and action.scheduled_day == day
            and action.status in [ActionStatus.SCHEDULED, ActionStatus.PENDING]
        ]
    
    def get_pending_reminders(self, week: int, day: int) -> List[CalendarReminder]:
        """Get reminders that should be sent now."""
        pending = []
        for reminder in self.reminders:
            if not reminder.is_sent and reminder.reminder_week == week and reminder.reminder_day == day:
                pending.append(reminder)
        return pending
    
    def send_reminders(self, week: int, day: int) -> List[str]:
        """Mark reminders as sent and return messages."""
        messages = []
        for reminder in self.get_pending_reminders(week, day):
            reminder.is_sent = True
            messages.append(reminder.message)
        return messages
    
    def mark_action_complete(
        self,
        action_id: str,
        week: int,
        day: int
    ) -> Dict[str, Any]:
        """Mark a scheduled action as completed."""
        action = self.scheduled_actions.get(action_id)
        if not action:
            return {"error": "Action not found"}
        
        action.status = ActionStatus.COMPLETED
        action.completed_week = week
        action.completed_day = day
        
        # Handle recurring actions
        if action.is_recurring and action.recurrence_weeks > 0:
            next_action = self.schedule_action(
                category=action.category,
                title=action.title,
                description=action.description,
                week=action.scheduled_week + action.recurrence_weeks,
                day=action.scheduled_day,
                priority=action.priority,
                action_data=action.action_data.copy(),
                is_recurring=True,
                recurrence_weeks=action.recurrence_weeks,
                current_week=week,
                current_day=day
            )
            return {
                "status": "completed",
                "recurring": True,
                "next_occurrence": {
                    "id": next_action.id,
                    "week": next_action.scheduled_week,
                    "day": next_action.scheduled_day
                }
            }
        
        return {"status": "completed", "recurring": False}
    
    def mark_action_missed(self, action_id: str) -> Dict[str, Any]:
        """Mark a scheduled action as missed."""
        action = self.scheduled_actions.get(action_id)
        if not action:
            return {"error": "Action not found"}
        
        action.status = ActionStatus.MISSED
        
        return {
            "status": "missed",
            "category": action.category.value,
            "title": action.title
        }
    
    def cancel_action(self, action_id: str) -> Dict[str, Any]:
        """Cancel a scheduled action."""
        action = self.scheduled_actions.get(action_id)
        if not action:
            return {"error": "Action not found"}
        
        if action.status == ActionStatus.COMPLETED:
            return {"error": "Cannot cancel completed action"}
        
        action.status = ActionStatus.CANCELLED
        return {"status": "cancelled"}
    
    def reschedule_action(
        self,
        action_id: str,
        new_week: int,
        new_day: int
    ) -> Dict[str, Any]:
        """Reschedule an action to a new time."""
        action = self.scheduled_actions.get(action_id)
        if not action:
            return {"error": "Action not found"}
        
        if action.status not in [ActionStatus.SCHEDULED, ActionStatus.PENDING]:
            return {"error": "Cannot reschedule non-pending action"}
        
        old_week, old_day = action.scheduled_week, action.scheduled_day
        action.scheduled_week = new_week
        action.scheduled_day = new_day
        
        return {
            "status": "rescheduled",
            "from": {"week": old_week, "day": old_day},
            "to": {"week": new_week, "day": new_day}
        }
    
    def advance_day(self, week: int, day: int):
        """Update statuses as day advances."""
        for action in self.scheduled_actions.values():
            if action.scheduled_week == week and action.scheduled_day == day:
                if action.status == ActionStatus.SCHEDULED:
                    action.status = ActionStatus.PENDING
    
    def check_overdue(self, current_week: int, current_day: int) -> List[ScheduledAction]:
        """Find overdue actions that weren't completed."""
        overdue = []
        for action in self.scheduled_actions.values():
            if action.status in [ActionStatus.SCHEDULED, ActionStatus.PENDING]:
                action_day_num = action.scheduled_week * 7 + action.scheduled_day
                current_day_num = current_week * 7 + current_day
                if action_day_num < current_day_num:
                    overdue.append(action)
        return overdue
    
    def get_upcoming_critical(self, current_week: int, lookahead_weeks: int = 2) -> List[ScheduledAction]:
        """Get upcoming critical actions."""
        upcoming = []
        for action in self.scheduled_actions.values():
            if (action.priority == ActionPriority.CRITICAL and
                action.status in [ActionStatus.SCHEDULED, ActionStatus.PENDING] and
                current_week <= action.scheduled_week <= current_week + lookahead_weeks):
                upcoming.append(action)
        
        upcoming.sort(key=lambda a: (a.scheduled_week, a.scheduled_day))
        return upcoming
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get calendar statistics."""
        total = len(self.scheduled_actions)
        completed = sum(1 for a in self.scheduled_actions.values() if a.status == ActionStatus.COMPLETED)
        missed = sum(1 for a in self.scheduled_actions.values() if a.status == ActionStatus.MISSED)
        pending = sum(1 for a in self.scheduled_actions.values() if a.status in [ActionStatus.SCHEDULED, ActionStatus.PENDING])
        
        # Category breakdown
        by_category = {}
        for action in self.scheduled_actions.values():
            cat = action.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total_actions": total,
            "completed": completed,
            "missed": missed,
            "pending": pending,
            "completion_rate": round(completed / max(completed + missed, 1) * 100, 1),
            "by_category": by_category
        }
    
    def to_dict(self, week: int) -> Dict[str, Any]:
        """Serialize for API responses."""
        week_schedule = self.get_week_schedule(week)
        
        return {
            "agent_id": self.agent_id,
            "current_week": week,
            "week_schedule": {
                day: [
                    {
                        "id": a.id,
                        "title": a.title,
                        "category": a.category.value,
                        "priority": a.priority.value,
                        "status": a.status.value,
                        "action_data": a.action_data
                    }
                    for a in actions
                ]
                for day, actions in week_schedule.items()
            },
            "statistics": self.get_statistics()
        }


class CalendarManager:
    """
    Manages calendars for all agents.
    """
    
    def __init__(self, agent_ids: List[str] = None):
        self.calendars: Dict[str, AgentCalendar] = {}
        # If agent_ids provided, pre-create calendars
        if agent_ids:
            for aid in agent_ids:
                self.get_calendar(aid)
    
    def get_calendar(self, agent_id: str) -> AgentCalendar:
        """Get or create calendar for an agent."""
        if agent_id not in self.calendars:
            self.calendars[agent_id] = AgentCalendar(agent_id)
        return self.calendars[agent_id]
    
    def process_day(self, week: int, day: int) -> Dict[str, List[str]]:
        """
        Process all calendars for the current day.
        
        Returns reminders to send to each agent.
        """
        notifications = {}
        
        for agent_id, calendar in self.calendars.items():
            # Advance day statuses
            calendar.advance_day(week, day)
            
            # Get and send reminders
            reminders = calendar.send_reminders(week, day)
            if reminders:
                notifications[agent_id] = reminders
            
            # Check for overdue (mark as missed if too old)
            overdue = calendar.check_overdue(week, day)
            for action in overdue:
                # If more than 1 day overdue, mark as missed
                action_day_num = action.scheduled_week * 7 + action.scheduled_day
                current_day_num = week * 7 + day
                if current_day_num - action_day_num > 1:
                    calendar.mark_action_missed(action.id)
        
        return notifications
    
    def sync_credit_payments(self, agent_id: str, credit_system, current_week: int):
        """
        Sync scheduled payments from credit system to calendar.
        
        Call this when credit system is initialized or updated.
        """
        from src.engine.finance.models import PaymentStatus
        
        calendar = self.get_calendar(agent_id)
        
        # Get all scheduled payments
        payments = credit_system.scheduled_payments.get(agent_id, [])
        
        for payment in payments:
            if payment.status == PaymentStatus.SCHEDULED:
                # Check if already on calendar
                existing = any(
                    a.linked_payment_id == payment.id 
                    for a in calendar.scheduled_actions.values()
                )
                
                if not existing:
                    calendar.schedule_payment_reminder(
                        payment_id=payment.id,
                        loan_id=payment.loan_id,
                        amount=payment.amount_due,
                        due_week=payment.due_week,
                        current_week=current_week
                    )
    
    def get_all_upcoming_payments(self, weeks_ahead: int = 4) -> Dict[str, List[Dict]]:
        """Get upcoming payments for all agents."""
        result = {}
        
        for agent_id, calendar in self.calendars.items():
            payments = []
            for action in calendar.scheduled_actions.values():
                if (action.category == ActionCategory.PAYMENT and
                    action.status in [ActionStatus.SCHEDULED, ActionStatus.PENDING]):
                    payments.append({
                        "id": action.id,
                        "title": action.title,
                        "week": action.scheduled_week,
                        "day": action.scheduled_day,
                        "amount": action.action_data.get("amount", 0)
                    })
            
            if payments:
                payments.sort(key=lambda p: (p["week"], p["day"]))
                result[agent_id] = payments[:10]  # Next 10 payments
        
        return result
    
    def to_dict(self, week: int) -> Dict[str, Any]:
        """Serialize all calendars for API response."""
        return {
            agent_id: calendar.to_dict(week)
            for agent_id, calendar in self.calendars.items()
        }
