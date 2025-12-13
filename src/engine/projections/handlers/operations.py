from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.projections.registry import EventRegistry
from src.models.hierarchy import Machine, StaffMember, Building
from src.models.social import TicketStatus

if TYPE_CHECKING:
    from src.models.world import LaundromatState
    from src.models.events.core import GameEvent


# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def _evt(event, name: str, default=None):
    """Extract field from event, checking both attrs and payload dict."""
    payload = getattr(event, "payload", {}) or {}
    return getattr(event, name, payload.get(name, default))

def _remove_staff(state, staff_id: str) -> None:
    """Remove staff member by ID from primary location."""
    state.primary_location.staff = [
        s for s in state.primary_location.staff if s.id != staff_id
    ]

@EventRegistry.register("STAFF_HIRED")
def apply_staff_hired(state: LaundromatState, event: GameEvent):
    payload = event.payload
    new_staff = StaffMember(
        id=getattr(event, "staff_id", payload.get("id")),
        name=getattr(event, "name", payload.get("name", "Unknown")),
        role=getattr(event, "role", payload.get("role")),
        skill_level=getattr(event, "skill_level", payload.get("skill_level", 0.5)),
        wage=getattr(event, "wage", payload.get("wage", 0.0))
    )
    state.primary_location.staff.append(new_staff)

@EventRegistry.register("STAFF_FIRED")
def apply_staff_fired(state: LaundromatState, event: GameEvent):
    payload = event.payload
    staff_id = getattr(event, "staff_id", payload.get("staff_id"))
    state.primary_location.staff = [
        s for s in state.primary_location.staff if s.id != staff_id
    ]

@EventRegistry.register("STAFF_QUITS")
def apply_staff_quits(state: LaundromatState, event: GameEvent):
    """Remove staff member who quit."""
    payload = event.payload if hasattr(event, "payload") else {}
    staff_id = getattr(event, "staff_id", payload.get("staff_id"))
    state.primary_location.staff = [
        s for s in state.primary_location.staff if s.id != staff_id
    ]

@EventRegistry.register("STAFF_TRAINED")
def apply_staff_trained(state: LaundromatState, event: GameEvent):
    payload = event.payload
    staff_id = getattr(event, "staff_id", payload.get("staff_id"))
    gain = getattr(event, "skill_gained", payload.get("skill_gained", 0.0))
    
    for s in state.primary_location.staff:
        if s.id == staff_id:
            s.skill_level = min(1.0, s.skill_level + gain)
            if hasattr(s, "morale"):
                 s.morale = min(1.0, s.morale + 0.1)
            break

@EventRegistry.register("MACHINE_PURCHASED")
def apply_machine_purchased(state: LaundromatState, event: GameEvent):
     payload = event.payload
     new_machine = Machine(
         id=getattr(event, "machine_id", payload.get("id")),
         type=getattr(event, "model_type", payload.get("type", "standard_washer")),
         condition=getattr(event, "condition", payload.get("condition", 1.0))
     )
     state.primary_location.machines.append(new_machine)

@EventRegistry.register("MARKETING_CAMPAIGN_STARTED")
def apply_marketing_started(state: LaundromatState, event: GameEvent):
    payload = event.payload
    boost = getattr(event, "boost_amount", payload.get("boost_amount", 0.0))
    state.primary_location.marketing_boost += boost

@EventRegistry.register("BUILDING_PURCHASED")
def apply_building_purchased(state: LaundromatState, event: GameEvent):
    payload = event.payload
    b_id = getattr(event, "building_id", payload.get("building_id"))
    
    # Check if primary_location has buildings list
    if hasattr(state.primary_location, "buildings"):
        state.primary_location.buildings.append(Building(
            id=b_id,
            name=f"Building {b_id}",
            type="storefront",
            condition=1.0,
            capacity_machines=20, # Default
            location_multiplier=getattr(event, "location_multiplier", 1.0)
        ))

@EventRegistry.register("MAINTENANCE_PERFORMED")
def apply_maintenance(state: LaundromatState, event: GameEvent):
    payload = event.payload
    parts_used = getattr(event, "parts_used", payload.get("parts_used", {}))
    machines_fixed = getattr(event, "machines_fixed", payload.get("machines_fixed", []))
    
    # Update components/inventory
    for part, qty in parts_used.items():
        current = state.primary_location.inventory.get(part, 0)
        state.primary_location.inventory[part] = max(0, current - qty)
        
    # Update machines
    # Assuming full repair or +0.2 condition from legacy logic?
    # Legacy: m.condition = min(1.0, m.condition + 0.2)
    # The Event doesn't say "how much" condition improved, only that it was performed.
    # The PROJECTION defines the effect on state? Or the Action defines it?
    # In Event Sourcing, the Event should ideally carry the *delta* or *result*.
    # But `MaintenancePerformed` event model (from `src/models/events/operations.py`) defined by user
    # has `cost`, `parts_used`, `machines_fixed`. No `condition_delta`.
    # So the Rule is in the Projection: "Maintenance adds 0.2 condition".
    # Or strict ES: Action should have calculated the result and emitted `MachineConditionUpdated` for each machine.
    # But that's 10-20 events.
    # COMPROMISE: Projection interprets `MaintenancePerformed` as specific improvement logic.
    
    for m in state.primary_location.machines:
        # Check if machine ID is in the fixed list
        # Note: machines_fixed might be list of IDs
        if m.id in machines_fixed:
            m.condition = min(1.0, m.condition + 0.2)
            if m.condition > 0.5:
                # Is is_broken a field?
                # Machine model in hierarchy.py likely has it.
                # Assuming yes.
                if hasattr(m, 'is_broken'):
                     m.is_broken = False


@EventRegistry.register("MACHINE_WEAR_UPDATED")
def apply_machine_wear_updated(state: LaundromatState, event: GameEvent):
    """Apply machine wear degradation from weekly physics calculation."""
    payload = event.payload if hasattr(event, "payload") else {}
    machine_id = getattr(event, "machine_id", payload.get("machine_id"))
    new_condition = getattr(event, "current_condition", payload.get("current_condition"))
    
    for m in state.primary_location.machines:
        if m.id == machine_id:
            m.condition = new_condition
            # If condition drops below breakdown threshold, mark as broken
            if new_condition <= 0.2:
                if hasattr(m, 'is_broken'):
                    m.is_broken = True
            break


@EventRegistry.register("MARKETING_BOOST_DECAYED")
def apply_marketing_boost_decayed(state: LaundromatState, event: GameEvent):
    """Apply marketing boost decay from weekly calculation."""
    payload = event.payload if hasattr(event, "payload") else {}
    remaining = getattr(event, "remaining_boost", payload.get("remaining_boost", 0.0))
    state.primary_location.marketing_boost = remaining


@EventRegistry.register("CLEANLINESS_UPDATED")
def apply_cleanliness_updated(state: LaundromatState, event: GameEvent):
    """Apply cleanliness update from weekly calculation."""
    payload = event.payload if hasattr(event, "payload") else {}
    new_cleanliness = getattr(event, "new_cleanliness", payload.get("new_cleanliness"))
    if new_cleanliness is not None:
        state.primary_location.cleanliness = max(0.0, min(1.0, new_cleanliness))

# --- Orphan Event Handlers (Future Feature Support) ---

@EventRegistry.register("MACHINE_STATE_CHANGED")
def apply_machine_state_changed(state: LaundromatState, event: GameEvent):
    """Update machine operational state."""
    payload = event.payload if hasattr(event, "payload") else {}
    machine_id = getattr(event, "machine_id", payload.get("machine_id"))
    new_state = getattr(event, "new_state", payload.get("new_state"))
    condition = getattr(event, "condition", payload.get("condition"))
    
    for m in state.primary_location.machines:
        if m.id == machine_id:
            if hasattr(m, "state"):
                m.state = new_state
            if condition is not None:
                m.condition = condition
            if new_state == "broken":
                m.is_broken = True
            break



@EventRegistry.register("CUSTOMER_VISIT_STARTED")
def apply_customer_visit_started(state: LaundromatState, event: GameEvent):
    """Stub for customer visit tracking."""
    # High frequency - maybe only track aggregate if needed
    pass



@EventRegistry.register("CUSTOMER_VISIT_BOUNCED")
def apply_customer_visit_bounced(state: LaundromatState, event: GameEvent):
    """Stub for bounce tracking."""
    state.primary_location.traffic_stats["bounced_visits"] += 1


@EventRegistry.register("CUSTOMER_COMPLAINT_FILED")
def apply_customer_complaint_filed(state: LaundromatState, event: GameEvent):
    """Add ticket for customer complaint."""
    from src.models.social import Ticket, TicketType, TicketStatus
    
    payload = event.payload if hasattr(event, "payload") else {}
    ticket = Ticket(
        id=getattr(event, "ticket_id", payload.get("ticket_id", "")),
        type=TicketType.COMPLAINT,
        description=getattr(event, "description", payload.get("description", "")),
        status=TicketStatus.OPEN,
        created_week=event.week
    )
    state.tickets.append(ticket)


@EventRegistry.register("CUSTOMER_SERVICE_COMPLETED")
def apply_customer_service_completed(state: LaundromatState, event: GameEvent):
    """Update Ticket status on completion."""
    payload = event.payload if hasattr(event, "payload") else {}
    ticket_id = getattr(event, "ticket_id", payload.get("ticket_id"))
    
    # Find and close ticket
    for ticket in state.tickets:
        if ticket.id == ticket_id:
            ticket.status = TicketStatus.CLOSED
            break



@EventRegistry.register("CUSTOMER_SENTIMENT_RECORDED")
def apply_customer_sentiment_recorded(state: LaundromatState, event: GameEvent):
    """Stub for sentiment tracking."""
    payload = event.payload if hasattr(event, "payload") else {}
    sentiment = float(getattr(event, "sentiment_score", payload.get("sentiment_score", 0.0)))
    
    # Store history
    state.primary_location.sentiment_history.append({
        "week": event.week,
        "score": sentiment,
        "topic": getattr(event, "topic", payload.get("topic", "general"))
    })
    
    # Keep history bounded? (Optional)
    if len(state.primary_location.sentiment_history) > 100:
        state.primary_location.sentiment_history.pop(0)


@EventRegistry.register("TICKET_IGNORED")
def apply_ticket_ignored(state: LaundromatState, event: GameEvent):
    """Mark ticket as ignored."""
    ticket_id = _evt(event, "ticket_id")
    
    for ticket in state.tickets:
        if ticket.id == ticket_id:
            ticket.status = TicketStatus.IGNORED
            break


@EventRegistry.register("PROPOSAL_SUBMITTED")
def apply_proposal_submitted(state: LaundromatState, event: GameEvent):
    """Track submitted improvement/business proposals."""
    payload = event.payload if hasattr(event, "payload") else {}
    proposal = {
        "id": getattr(event, "proposal_id", payload.get("proposal_id")),
        "type": getattr(event, "proposal_type", payload.get("proposal_type", "business")),
        "description": getattr(event, "description", payload.get("description", "")),
        "status": "pending",
        "week": event.week
    }
    state.agent.proposals.append(proposal)



@EventRegistry.register("PROPOSAL_EVALUATED")
def apply_proposal_evaluated(state: LaundromatState, event: GameEvent):
    """Update proposal status."""
    payload = event.payload if hasattr(event, "payload") else {}
    proposal_id = getattr(event, "proposal_id", payload.get("proposal_id"))
    
    for prop in state.agent.proposals:
        if prop.get("id") == proposal_id:
            prop["status"] = "under_review"
            break


@EventRegistry.register("PROPOSAL_APPROVED")
def apply_proposal_approved(state: LaundromatState, event: GameEvent):
    """Unlock revenue stream from approved proposal."""
    payload = event.payload if hasattr(event, "payload") else {}
    stream_name = getattr(event, "revenue_stream_name", payload.get("revenue_stream_name"))
    
    if stream_name and stream_name in state.revenue_streams:
        state.revenue_streams[stream_name].unlocked = True



@EventRegistry.register("PROPOSAL_REJECTED")
def apply_proposal_rejected(state: LaundromatState, event: GameEvent):
    """Update proposal status."""
    payload = event.payload if hasattr(event, "payload") else {}
    proposal_id = getattr(event, "proposal_id", payload.get("proposal_id"))
    
    for prop in state.agent.proposals:
        if prop.get("id") == proposal_id:
            prop["status"] = "rejected"
            break



@EventRegistry.register("LOCATION_ASSIGNED")
def apply_location_assigned(state: LaundromatState, event: GameEvent):
    """Stub for zone assignment."""
    payload = event.payload if hasattr(event, "payload") else {}
    zone_id = getattr(event, "zone_id", payload.get("zone_id"))
    entity_id = getattr(event, "entity_id", payload.get("entity_id")) # e.g. machine or staff
    
    if zone_id and entity_id:
        if zone_id not in state.primary_location.zones:
            state.primary_location.zones[zone_id] = {"assigned_entities": []}
            
        if "assigned_entities" not in state.primary_location.zones[zone_id]:
             state.primary_location.zones[zone_id]["assigned_entities"] = []
             
        state.primary_location.zones[zone_id]["assigned_entities"].append(entity_id)


@EventRegistry.register("ZONE_TRAFFIC_SHIFTED")
def apply_zone_traffic_shifted(state: LaundromatState, event: GameEvent):
    """Stub for traffic changes."""
    payload = event.payload if hasattr(event, "payload") else {}
    zone_id = getattr(event, "zone_id", payload.get("zone_id"))
    multiplier = getattr(event, "traffic_multiplier", payload.get("traffic_multiplier"))
    
    if zone_id and multiplier is not None:
        if zone_id not in state.primary_location.zones:
            state.primary_location.zones[zone_id] = {}
        state.primary_location.zones[zone_id]["traffic_multiplier"] = multiplier


