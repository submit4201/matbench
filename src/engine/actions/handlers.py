from typing import List, Dict, Any
from src.engine.actions.registry import ActionRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent, ActionFailed
from src.models.events.commerce import PriceSetEvent, InventoryStocked
from src.models.events.finance import FundsTransferred, BillPaid
from src.models.events.operations import MachinePurchased, MarketingCampaignStarted, TicketResolved, StaffHired, StaffFired, StaffTrained
from src.models.events.social import ReputationChanged
import uuid

@ActionRegistry.register("SET_PRICE")
def handle_set_price(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    new_price = float(payload.get("amount", state.price))
    
    if new_price < 0:
        return []
        
    return [PriceSetEvent(
        week=week,
        agent_id=state.id,
        new_price=new_price,
        old_price=state.price
    )]

@ActionRegistry.register("BUY_SUPPLIES")
def handle_buy_inventory(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    item = payload.get("item")
    qty = int(payload.get("quantity", 0))
    cost = float(payload.get("cost", 0))
    
    events = []
    
    # Financial Event
    events.append(FundsTransferred(
        week=week,
        agent_id=state.id,
        transaction_id=str(uuid.uuid4()),
        amount=-cost,
        category="expense",
        description=f"Bought {qty} {item}"
    ))
    
    # Inventory Event
    events.append(InventoryStocked(
        week=week,
        agent_id=state.id,
        item_type=item,
        quantity=qty,
        cost=cost
    ))
    
    return events

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
            location_id=state.primary_location.id # Assumption: Adding to primary location
        )
    ]

@ActionRegistry.register("MARKETING_CAMPAIGN")
def handle_marketing_campaign(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    # Support 'cost' or 'amount' keys for legacy compat
    cost = float(payload.get("cost", payload.get("amount", 0.0)))
    
    if cost <= 0 or state.balance < cost:
        return []
        
    boost = cost / 100.0
    
    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-cost,
            category="expense",
            description=f"Marketing Campaign (${cost})"
        ),
        MarketingCampaignStarted(
            week=week,
            agent_id=state.id,
            campaign_type="general", # Could be parametrized
            cost=cost,
            boost_amount=boost,
            duration_weeks=4
        ),
        ReputationChanged(
            week=week,
            agent_id=state.id,
            delta=boost,
            reason="Marketing Campaign"
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
            delta=2.0,
            reason="Customer Ticket Resolved"
        )
    ]

@ActionRegistry.register("PAY_BILL")
def handle_pay_bill(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    bill_id = payload.get("bill_id")
    
    # 1. Validation: Use State Source of Truth
    bill = next((b for b in state.bills if b.id == bill_id), None)
    
    if not bill:
        return [] # Or ActionFailed? For now silent fail if bill gone.
        
    if bill.is_paid:
        return []
        
    amount = bill.amount
    
    if state.balance < amount:
        return [] # Fail silently or ActionFailed (Legacy returned False)

    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-amount,
            category="liability",
            description=f"Paid Bill {bill.name}"
        ),
        BillPaid(
            week=week,
            agent_id=state.id,
            bill_id=bill_id,
            amount_paid=amount,
            payment_week=week,
            was_late=week > bill.due_week
        )
    ]

@ActionRegistry.register("BUY_BUILDING")
def handle_buy_building(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    # Similar to bills, we need price.
    price = float(payload.get("price", 0))
    listing_id = payload.get("listing_id")
    
    if price <= 0 or state.balance < price:
        return []
        
    from src.models.events.finance import BuildingPurchased
    
    return [
        FundsTransferred(
            week=week,
            agent_id=state.id,
            transaction_id=str(uuid.uuid4()),
            amount=-price,
            category="real_estate",
            description=f"Purchased Building {listing_id}"
        ),
        BuildingPurchased(
            week=week,
            agent_id=state.id,
            building_id=listing_id, # Simplified: ID matches listing
            price=price,
            location_multiplier=1.0
        )
    ]

@ActionRegistry.register("RESOLVE_DILEMMA")
def handle_resolve_dilemma(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    dilemma_id = payload.get("dilemma_id")
    choice_id = payload.get("choice_id")
    
    # Extract calculated effects from payload (Migration Hack: FE/Manager passes expected outcome)
    # Ideally, this should be calculated here using a Service in context, but explicit instruction
    # is to move side effects out or ensure Event carries the data.
    # We assume 'effects' dict contains { 'reputation': 5.0, 'money': -100.0, 'flags': [...] }
    effects = payload.get("effects", {})
    outcome_text = payload.get("outcome_text", "Resolved")
    
    from src.models.events.social import DilemmaResolved
    
    return [
        DilemmaResolved(
            week=week,
            agent_id=state.id,
            dilemma_id=dilemma_id,
            choice_id=choice_id,
            outcome_text=outcome_text,
            effects=effects
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

    severance = staff.wage * 20 # 1 week pay
    
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

@ActionRegistry.register("NEGOTIATE")
@ActionRegistry.register("NEGOTIATE_CONTRACT")
def handle_negotiate(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    item = payload.get("item", "soap")
    vendor_id = payload.get("vendor_id", "bulkwash")
    
    # 1. Validation (Pure)
    # We define that you can always REQUEST a negotiation. 
    # Logic for "can you actually do it?" could be here if it depends only on State (e.g. cooldown).
    # For now, we assume requests are valid if they have minimum args.
    
    # Snapshot social score for the process
    social_score = state.social_score.total_score if hasattr(state.social_score, "total_score") else state.reputation
    
    from src.models.events.commerce import NegotiationRequested
    
    return [
        NegotiationRequested(
            week=week,
            agent_id=state.id,
            negotiation_id=str(uuid.uuid4()),
            vendor_id=vendor_id,
            item_type=item,
            social_score_snapshot=social_score
        )
    ]


@ActionRegistry.register("PERFORM_MAINTENANCE")
def handle_maintenance(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    parts_needed = len(state.machines) // 5
    parts_in_stock = state.inventory.get("parts", 0)
    
    from src.models.events.operations import MaintenancePerformed
    
    if parts_in_stock >= parts_needed:
        return [
            MaintenancePerformed(
                week=week,
                agent_id=state.id,
                location_id=state.primary_location.id if hasattr(state, "primary_location") else "main",
                cost=0.0, # Parts used, no cash
                parts_used={"parts": parts_needed},
                machines_fixed=[m.id for m in state.machines] # All machines logic
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

@ActionRegistry.register("SEND_MESSAGE")
def handle_send_message(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    recipient = payload.get("recipient")
    content = payload.get("content")
    
    if not recipient or not content:
        return []
        
    from src.models.events.social import MessageSent
    
    # In legacy, this sent a message immediately via communication channel.
    # In event sourcing, we emit MessageSent, and the Projection/Saga might actually deliver it 
    # (i.e. put it in the recipient's inbox).
    # For now, we emit the event.
    
    return [
        MessageSent(
            week=week,
            agent_id=state.id, # Sender
            msg_id=str(uuid.uuid4()),
            recipients=[recipient],
            channel="direct",
            content=content
        )
    ]

@ActionRegistry.register("PROPOSE_ALLIANCE")
def handle_propose_alliance(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    target = payload.get("target")
    duration = int(payload.get("duration", 4))
    
    from src.models.events.social import AllianceProposed
    
    # We emit proposed. Auto-accept logic (TrustSystem) should be a Reaction to this event, 
    # OR we check it here? Legacy checked `trust_system.propose_alliance` directly.
    # That method likely does the logic and returns success/fail.
    # If we want to kill legacy, we should replicate that logic or delegate.
    # For this migration step, let's keep it simple: Emit Proposed.
    # AND if we can, emit Formed if we know it succeeds?
    # No, that duplicates logic.
    # Let's emit AllianceProposed.
    # Context: If trust system is available, we might use it to check feasibility?
    # But `handlers` should be pure.
    # Creating a "Proposal" event is safe.
    
    return [
        AllianceProposed(
            week=week,
            agent_id=state.id,
            proposal_id=str(uuid.uuid4()),
            target_agent_id=target,
            alliance_type="non_aggression",
            terms={"duration": duration}
        )
    ]

@ActionRegistry.register("INITIATE_BUYOUT")
def handle_initiate_buyout(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    target_id = payload.get("target")
    offer = float(payload.get("offer", 0))
    
    from src.models.events.commerce import BuyoutOfferSent
    
    # Check bounds
    if offer <= 0: return []
    if state.balance < offer:
        # Optional: Emit "BuyoutFailedInsufficientFunds"
        return []
        
    return [
        BuyoutOfferSent(
            week=week,
            agent_id=state.id,
            proposal_id=str(uuid.uuid4()),
            target_agent_id=target_id,
            offer_amount=offer
        )
    ]
