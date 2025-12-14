from typing import List, Dict, Any
import uuid
from src.engine.actions.registry import ActionRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent
from src.models.events.operations import MarketingCampaignStarted
from src.models.events.social import ReputationChanged, MessageSent, AllianceProposed, DilemmaResolved
from src.models.events.finance import FundsTransferred

@ActionRegistry.register("MARKETING_CAMPAIGN")
def handle_marketing_campaign(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    # Support 'cost' or 'amount' keys for legacy compat
    cost = float(payload.get("cost", payload.get("amount", 0.0)))

    if cost <= 0 or state.balance < cost:
        return []

    # Standard logic: Boost = cost / 20.0 (Updated from legacy reading)
    # Legacy code said: boost = cost / settings.economy.marketing_cost_divisor
    # We'll use a constant or passed param from context settings?
    # For now hardcode 20.0 as seen in legacy reading.
    divisor = 20.0
    boost = cost / divisor

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
            campaign_type=payload.get("campaign_type", "general"),
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

@ActionRegistry.register("RESOLVE_DILEMMA")
def handle_resolve_dilemma(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    dilemma_id = payload.get("dilemma_id")
    choice_id = payload.get("choice_id")

    # We still accept payload-injected effects for migration simplicity,
    # but Reactions can also calculate.
    effects = payload.get("effects", {})
    outcome_text = payload.get("outcome_text", "Resolved")

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

@ActionRegistry.register("SEND_MESSAGE")
def handle_send_message(state: LaundromatState, payload: Dict[str, Any], week: int, context: Dict[str, Any]) -> List[GameEvent]:
    recipient = payload.get("recipient")
    content = payload.get("content")

    if not recipient or not content:
        return []

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
