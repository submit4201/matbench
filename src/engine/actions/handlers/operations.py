from typing import List, Dict, Any
import uuid
from src.engine.actions.registry import ActionRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent, ActionFailed
from src.models.events.operations import (
    MachinePurchased, TicketResolved, StaffHired, StaffFired, StaffTrained, MaintenancePerformed, EmergencyRepairPerformed
)
from src.models.events.finance import FundsTransferred
from src.models.events.social import ReputationChanged

@ActionRegistry.register("UPGRADE_MACHINE")
def handle_upgrade_machine(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    cost = 500.0
    if state.balance < cost:
        return []

    new_id = f"M-{uuid.uuid4()}"

    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-cost,
            category="expense",
            description="Machine Upgrade"
        ),
        MachinePurchased(
            week=week,
            agent_id=state.id,
            machine_id=new_id,
            model_type="standard_washer",
            price=cost,
            location_id=state.primary_location.id if hasattr(state, "primary_location") else "main"
        )
    ]

@ActionRegistry.register("RESOLVE_TICKET")
def handle_resolve_ticket(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    ticket_id = payload.get("ticket_id")
    # Verify ticket ownership/validity?
    # For now assume valid if ID exists.

    return [
        TicketResolved(
            week=week,
            agent_id=state.id,
            ticket_id=ticket_id,
            resolution_method="standard",
            cost_incurred=0.0
        ),
        ReputationChanged(
            week=week,
            agent_id=state.id,
            delta=2.0, # Parity with legacy
            reason="Customer Ticket Resolved"
        )
    ]

@ActionRegistry.register("HIRE_STAFF")
def handle_hire_staff(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    role = payload.get("role", "attendant")
    hiring_fee = 100.0

    if state.balance < hiring_fee:
        return [ActionFailed(
            week=week,
            agent_id=state.id,
            action_type="HIRE_STAFF",
            reason="Insufficient funds to hire staff.",
            details={"cost": hiring_fee, "balance": state.balance}
        )]

    # Generate ID - Logic copied from legacy but using UUID for cleaner generation or keeping format?
    current_count = len(state.staff)
    new_id = f"S{current_count + 1}_{week}"

    # Wage
    wage = 15.0 if role == "attendant" else 20.0

    # Name generation (simple)
    new_name = f"Employee {new_id}"

    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-hiring_fee,
            category="expense",
            description=f"Hiring Fee ({role})"
        ),
        StaffHired(
            week=week,
            agent_id=state.id,
            staff_id=new_id,
            role=role,
            wage=wage,
            skill_level=0.5,
            staff_name=new_name
        )
    ]

@ActionRegistry.register("FIRE_STAFF")
def handle_fire_staff(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    staff_id = payload.get("staff_id")
    # Find staff
    staff = next((s for s in state.staff if s.id == staff_id), None)

    if not staff:
        return [ActionFailed(
            week=week,
            agent_id=state.id,
            action_type="FIRE_STAFF",
            reason=f"Staff member {staff_id} not found."
        )]

    severance = staff.wage * 2 # 2 weeks pay (updated from 1 week)

    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-severance,
            category="expense",
            description=f"Severance ({staff.id})"
        ),
        StaffFired(
            week=week,
            agent_id=state.id,
            staff_id=staff.id,
            reason="Fired by manager",
            staff_name=staff.name,
            severance_pay=severance
        )
    ]

@ActionRegistry.register("TRAIN_STAFF")
def handle_train_staff(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    staff_id = payload.get("staff_id")
    staff = next((s for s in state.staff if s.id == staff_id), None)
    cost = 150.0

    if not staff:
        return [ActionFailed(week=week, agent_id=state.id, action_type="TRAIN_STAFF", reason=f"Staff {staff_id} not found")]

    if state.balance < cost:
        return [ActionFailed(week=week, agent_id=state.id, action_type="TRAIN_STAFF", reason="Insufficient funds for training")]

    skill_gain = 0.1
    new_skill = min(1.0, staff.skill_level + skill_gain)

    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-cost,
            category="expense",
            description=f"Training ({staff_id})"
        ),
        StaffTrained(
            week=week,
            agent_id=state.id,
            staff_id=staff_id,
            skill_gained=skill_gain,
            cost=cost,
            staff_name=staff.name,
            final_skill_level=new_skill
        )
    ]

@ActionRegistry.register("PERFORM_MAINTENANCE")
def handle_maintenance(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    machine_count = len(state.machines) if isinstance(state.machines, list) else state.machines
    # Legacy logic: 1 part per 5 machines
    parts_needed = max(1, int(machine_count / 5)) if machine_count > 0 else 0
    parts_in_stock = state.inventory.get("parts", 0)

    if parts_in_stock >= parts_needed:
        return [
            MaintenancePerformed(
                week=week,
                agent_id=state.id,
                location_id=state.primary_location.id if hasattr(state, "primary_location") else "main",
                cost=0.0, # Parts used, no cash
                parts_used={"parts": parts_needed},
                machines_fixed=[m.id for m in state.machines] if isinstance(state.machines, list) else []
            )
        ]
    else:
        return [ActionFailed(
            week=week,
            agent_id=state.id,
            action_type="PERFORM_MAINTENANCE",
            reason=f"Not enough parts. Need {parts_needed}, have {parts_in_stock}.",
            details={"needed": parts_needed, "available": parts_in_stock}
        )]

@ActionRegistry.register("EMERGENCY_REPAIR")
def handle_emergency_repair(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    broken_count = state.broken_machines
    if broken_count <= 0:
        return []

    cost = broken_count * 150.0  # Legacy cost

    if state.balance < cost:
         return [ActionFailed(
            week=week,
            agent_id=state.id,
            action_type="EMERGENCY_REPAIR",
            reason="Insufficient funds",
            details={"cost": cost, "balance": state.balance}
        )]

    return [
         FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-cost,
            category="expense",
            description=f"Emergency Repair ({broken_count} machines)"
        ),
        EmergencyRepairPerformed(
            week=week,
            agent_id=state.id,
            cost=cost,
            machines_fixed=broken_count
        )
    ]
