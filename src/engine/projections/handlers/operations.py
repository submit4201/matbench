from src.engine.projections.registry import EventRegistry
from src.models.world import LaundromatState
from src.models.hierarchy import Machine, StaffMember, Building
from src.models.events.core import GameEvent

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

