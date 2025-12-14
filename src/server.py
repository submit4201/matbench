"""
FastAPI Server for Laundromat Tycoon

Features:
- Game state management
- AI agent integration with structured XML thinking
- History tracking for all participants
- Scenario selection
"""

# Load environment variables FIRST
import os

from src.config import settings


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import uvicorn
import json

from src.engine.core.time import TimeSystem, WeekPhase, Day
from src.engine.core.events import EventManager
from src.engine.population.customer import Customer
from src.engine.history import GameHistory, TurnRecord
from src.world.laundromat import LaundromatState
from src.world.ticket import TicketStatus
from src.engine.commerce.vendor import VendorManager, VendorTier
from src.engine.game_engine import GameEngine # Base Engine
from src.engine.enhanced_engine import EnhancedGameEngine  # Enhanced with new systems
from src.agents.human_agent import HumanAgent
from src.agents.llm_agent import LLMAgent
from src.agents.base_agent import Action, ActionType, Observation
from src.engine.social.communication import MessageIntent
from src.benchmark.scenarios import get_scenario, list_scenarios, Scenario


from src.utils.logger import get_logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Logger Setup
logger = get_logger("src.server", category="server")

app = FastAPI(title="Laundromat Tycoon", version="1.0.0")

# Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        logger.info(f"REQUEST: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            process_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"RESPONSE: {response.status_code} (took {process_time:.3f}s)")
            return response
        except Exception as e:
            logger.error(f"REQUEST FAILED: {str(e)}", exc_info=True)
            raise e

app.add_middleware(LoggingMiddleware)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Game State ---
# --- Game State Wrapper ---
class GameWrapper:
    def __init__(self, scenario_name: str = None):
        self.scenario_name = scenario_name
        self.scenario: Optional[Scenario] = None
        
        # Initialize Game Engine (Enhanced with Credit, Calendar, Neighborhood, Game Master)
        self.engine = EnhancedGameEngine(["p1", "p2", "p3"])
        
        # Initialize from scenario or defaults
        if scenario_name:
            try:
                self.scenario = get_scenario(scenario_name)
                # Override engine defaults with scenario data
                self._apply_scenario(self.scenario)
            except ValueError:
                print(f"Unknown scenario: {scenario_name}, using defaults")
        
        # Initialize agents
        self.agents = [
            HumanAgent("p1", "Human Player"),
            LLMAgent("p2", "Cheap AI", llm_provider="GEMINI"),
            LLMAgent("p3", "Luxury AI", llm_provider="PHI")  # PHI with tool-enabled format
        ]
        
        self.customers = [Customer(f"c{i}") for i in range(50)]
        self.history = GameHistory(scenario_name)
        self.ai_thoughts = {}
        self.vendor_manager = VendorManager() # Use VendorManager
        
        # Game session ID for log organization
        self.game_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _apply_scenario(self, scenario: Scenario):
        # Helper to map scenario data to engine states
        for pid, initial in [("p1", scenario.p1_initial), ("p2", scenario.p2_initial), ("p3", scenario.p3_initial)]:
            state = self.engine.states[pid]
            state.price = initial.price
            state.social_score = initial.social_score
            state.reputation = initial.social_score # Sync
            
            # Only overwrite balance if NOT using EnhancedGameEngine (which sets SBA loan)
            if not isinstance(self.engine, EnhancedGameEngine):
                state.balance = initial.balance
                
            # state.machines = initial.machines # Need to convert int to list of Machine objects if needed
            state.inventory = initial.inventory.copy()

game = GameWrapper()


from src.api_types import (
    ActionRequest, 
    ScenarioRequest, 
    NegotiateRequest, 
    ProposalRequest, 
    CreditPaymentRequest, 
    DiplomacyProposalRequest
)


# --- Helper Functions ---
# Helper function _serialize_state removed in favor of Pydantic .model_dump()



def _log_ai_response(agent_id: str, week: int, thinking: List[str], actions: List[Action], raw_response: str):
    """
    Log AI response to file for analysis and debugging
    
    Args:
        agent_id (str): ID of the agent
        week (int): Current week
        thinking (List[str]): List of AI thoughts
        actions (List[Action]): List of actions taken
        raw_response (str): Raw LLM response
     #! TODO: this accually needs to be a nother format json/yaml/xml something md great for formatting but not for analysis
    #! TODO: should have think, action, thought,     
    """
    # Create game-specific log directory with timestamp
    game_id = getattr(game, 'game_id', datetime.now().strftime("%Y%m%d_%H%M%S"))
    log_dir = f"logs/games/{game_id}/ai_responses"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{log_dir}/{agent_id}_week{week}_{timestamp}.md"
    
    content = f"""# AI Response Log
**Agent**: {agent_id}
**Week**: {week}
**Timestamp**: {datetime.now().isoformat()}

## Thinking
{chr(10).join([f'- {t}' for t in thinking]) if thinking else 'No thinking captured'}

## Actions
{chr(10).join([f'- {a.type.value}: {a.parameters}' for a in actions]) if actions else 'No actions'}

## Raw LLM Response
```xml
{raw_response if raw_response else 'No raw response available'}
```
"""
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[LOG] Saved AI response to {filename}")
    except Exception as e:
        print(f"[AI Log] Failed to write log: {e}")





def _record_turn(agent_id: str, agent_name: str, thinking: List[str], 
                 actions: List[Action], raw_response: str, 
                 state_before: Dict, state_after: Dict,
                 competitors: List[Dict], events: List[str],
                 is_human: bool = False, llm_provider: str = ""):
    """Record a turn in the game history"""
    record = TurnRecord(
        week=game.engine.time_system.current_week,
        agent_id=agent_id,
        agent_name=agent_name,
        timestamp=datetime.now().isoformat(),
        balance_before=state_before.get("balance", 0),
        social_score_before=state_before.get("social_score", 0),
        inventory_before=state_before.get("inventory", {}),
        thinking=thinking,
        actions=[{"type": a.type.value, "params": a.parameters} for a in actions],
        raw_response=raw_response,
        balance_after=state_after.get("balance", 0),
        social_score_after=state_after.get("social_score", 0),
        inventory_after=state_after.get("inventory", {}),
        competitors_snapshot=competitors,
        events_active=events,
        is_human=is_human,
        llm_provider=llm_provider
    )
    game.history.record_turn(record)



# --- Main Endpoints ---
@app.get("/scenarios")
def list_scenarios():
    """List all available scenarios"""
    from src.benchmark.scenarios import SCENARIOS
    return {
        "scenarios": [
            {
                "name": s.name,
                "description": s.description,
                "difficulty": s.difficulty.value,
                "weeks": s.weeks
            }
            for s in SCENARIOS.values()
        ]
    }


@app.post("/start_scenario")
def start_scenario(req: ScenarioRequest):
    """Start a new game with selected scenario"""
    global game
    scenario_name = req.scenario_name or "stable_market"
    game = GameWrapper(scenario_name=scenario_name)
    return {"status": "started", "scenario": scenario_name}


@app.get("/state")
def get_state(agent_id: str = "p1"):
    """Get current game state"""
    laundromats_data = {}
    for pid, l in game.engine.states.items():
        # Using Pydantic Dump
        state_dump = l.model_dump(mode='json', exclude={'ledger'})
        # Inject properties not covered by default dump if not ComputedField
        state_dump['balance'] = l.balance
        state_dump['broken_machines'] = l.broken_machines
        state_dump['reputation'] = l.reputation  # Add reputation from property
        # Convert machines list to count for frontend compatibility
        # if isinstance(state_dump.get('machines'), list):
        #    state_dump['machines'] = len(state_dump['machines'])
        # Add metrics
        if hasattr(l, 'get_inventory_metrics'):
            state_dump['inventory_metrics'] = l.get_inventory_metrics()
        
        # Inject Loans from Credit System
        if hasattr(game.engine, 'credit_system'):
            # Get accounts for this agent
            accounts = game.engine.credit_system.get_agent_accounts(pid)
            # The frontend expects 'loans' list in Laundromat object with specific fields
            state_dump['loans'] = []
            for acc in accounts:
                # Calculate weeks remaining
                weeks_passed = game.engine.time_system.current_week - acc.opened_week
                weeks_remaining = max(0, acc.term_weeks - weeks_passed)
                
                state_dump['loans'].append({
                    "name": acc.account_type.replace('_', ' ').capitalize(),
                    "principal": acc.original_amount,
                    "balance": acc.current_balance,
                    "interest_rate_monthly": acc.interest_rate, # This is usually weekly in our engine but named monthly in type?
                    "term_weeks": acc.term_weeks,
                    "weeks_remaining": weeks_remaining,
                    "weekly_payment": acc.weekly_payment,
                    "is_defaulted": acc.is_defaulted,
                    "missed_payments": len([p for p in acc.payments if p.status == 'missed'])
                })
        
        laundromats_data[pid] = state_dump



    # Serialize vendors
    vendors_data = []
    for v in game.vendor_manager.get_all_vendors():
        vendors_data.append({
            "id": v.profile.id,
            "name": v.profile.name,
            "slogan": v.profile.slogan,
            "tier": v.tier.name,
            "prices": {item: v.get_price(item, agent_id=agent_id) for item in v.profile.base_prices},
            "special_offer": v.special_offer.__dict__ if v.special_offer else None,
            "reliability": v.profile.reliability,
            "delivery_days": v.profile.delivery_days
        })

    return {
        "week": game.engine.time_system.current_week,
        "day": game.engine.time_system.current_day.value,
        "phase": game.engine.time_system.current_phase.value,
        "season": game.engine.time_system.current_season.value,
        "laundromats": laundromats_data,
        "events": [e.description for e in game.engine.event_manager.active_events],
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "recipient_id": m.recipient_id,
                "channel": m.channel.value if hasattr(m.channel, "value") else str(m.channel),
                "content": m.content,
                "week": m.week,
                "day": m.day,
                "intent": m.intent.value if hasattr(m.intent, "value") else str(m.intent),
                "is_read": "p1" in m.read_by,
                "attachments": m.attachments or []
            }
            for m in game.engine.communication.get_messages("p1")
        ],
        "market": {
            "vendors": vendors_data,
            "supply_chain_events": game.vendor_manager.get_active_supply_chain_events()
        },
        "customer_thoughts": [
            {
                "text": c.current_thought,
                "laundromat_id": c.current_thought_laundromat_id or "unknown"
            }
            for c in game.customers if c.current_thought
        ],
        "scenario": game.scenario_name,
        "ai_thoughts": game.ai_thoughts,
        "ai_thoughts_history": getattr(game, 'ai_thoughts_history', [])[-5:],  # Last 5 turns
        "alliances": [str(a) for a in game.engine.trust_system.active_alliances]
    }


@app.post("/action")
def take_action(req: ActionRequest):
    """Human player takes an action"""
    if req.agent_id != "p1":
        raise HTTPException(status_code=403, detail="Only p1 can take actions via API")
    
    try:
        action_type = ActionType(req.action_type)
        action = Action(type=action_type, parameters=req.parameters)
        
        state_before = game.engine.states["p1"].model_dump(mode="json", exclude={'ledger'})

        
        # Apply action IMMEDIATELY for human player (no queuing - fair play with AI)
        my_state = game.engine.states["p1"]
        # Use Engine's Action Processing
        game.engine.apply_action(my_state, action.model_dump())
        
        state_after = game.engine.states["p1"].model_dump(mode='json', exclude={'ledger'})
        state_after['balance'] = game.engine.states["p1"].balance

        
        # Record human turn (no thinking for human actions via this endpoint)
        competitors = [game.engine.states[k].model_dump(mode='json', exclude={'ledger'}) for k in game.engine.states if k != "p1"]
        events = [e.description for e in game.engine.event_manager.active_events]
        _record_turn(
            "p1", "Human Player", 
            [],  # No thinking captured for quick actions
            [action], "",
            state_before, state_after,
            competitors, events,
            is_human=True
        )
        
        return {"status": "accepted", "action": str(action), "new_state": state_after}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid action type: {str(e)}")


@app.post("/negotiate")
def negotiate_price(req: NegotiateRequest):
    """Negotiate a price with a vendor"""
    if req.agent_id != "p1":
        raise HTTPException(status_code=403, detail="Only p1 can negotiate")
        
    vendor = game.vendor_manager.get_vendor(req.vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    agent_state = game.engine.states["p1"]
    
    # Get social score total
    social_score = agent_state.social_score.total_score if hasattr(agent_state.social_score, "total_score") else agent_state.reputation
    
    # Negotiate - returns a Dict with success, message, vendor_id
    result = vendor.negotiate_price(req.item, agent_state.name, social_score, agent_id=req.agent_id)
    
    # Get the new price after negotiation
    final_price = vendor.get_price(req.item, agent_id=req.agent_id)
    
    return {
        "item": req.item,
        "original_price": vendor.profile.base_prices.get(req.item, 0),
        "offered_price": final_price,
        "success": result.get("success", False),
        "message": result.get("message", ""),
        "vendor_id": req.vendor_id
    }


# --- GM-Powered Vendor Negotiation Chat ---
class NegotiateChatRequest(BaseModel):
    agent_id: str
    vendor_id: str
    item: str
    message: str  # Player's negotiation message

@app.post("/negotiate/chat")
def negotiate_chat(req: NegotiateChatRequest):
    """
    Chat-based negotiation with vendor, powered by Game Master LLM.
    The GM roleplays as the vendor and responds to the player's message.
    Conversation history is persisted per vendor/player pair.
    """
    import datetime
    
    if req.agent_id != "p1":
        raise HTTPException(status_code=403, detail="Only p1 can negotiate")
    
    vendor = game.vendor_manager.get_vendor(req.vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    agent_state = game.engine.states["p1"]
    
    # Build vendor profile for roleplay
    vendor_profile = {
        "name": vendor.profile.name if hasattr(vendor, 'profile') else vendor.name,
        "slogan": vendor.profile.slogan if hasattr(vendor, 'profile') else "",
        "description": vendor.profile.description if hasattr(vendor, 'profile') else "",
        "reliability": vendor.profile.reliability if hasattr(vendor, 'profile') else 0.8
    }
    
    # Build negotiation context
    base_price = vendor.profile.base_prices.get(req.item, 10.0) if hasattr(vendor, 'profile') else 10.0
    current_price = vendor.get_price(req.item, agent_id=req.agent_id) if hasattr(vendor, 'get_price') else base_price
    
    social_score = agent_state.social_score.total_score if hasattr(agent_state.social_score, "total_score") else agent_state.reputation
    
    # Get conversation history for this player-vendor pair
    history_key = req.agent_id
    conversation_history = vendor.negotiation_history.get(history_key, [])
    
    # Filter history for this item (optional: you can remove this to share history across items)
    item_history = [h for h in conversation_history if h.get("item") == req.item]
    
    negotiation_context = {
        "item": req.item,
        "base_price": base_price,
        "current_price": current_price,
        "player_reputation": social_score,
        "player_name": agent_state.name,
        "order_history": getattr(vendor, 'order_history', {}).get(req.agent_id, 0),
        "conversation_history": item_history[-10:]  # Last 10 messages for context
    }
    
    # Store player message in history
    player_entry = {
        "role": "player",
        "message": req.message,
        "item": req.item,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    if history_key not in vendor.negotiation_history:
        vendor.negotiation_history[history_key] = []
    vendor.negotiation_history[history_key].append(player_entry)
    
    # Use Game Master to roleplay as vendor
    if hasattr(game.engine, 'game_master'):
        result = game.engine.game_master.roleplay_as_vendor(
            vendor_profile, req.message, negotiation_context
        )
    else:
        # Fallback basic response
        result = {
            "vendor_response": f"Thank you for your interest. The price for {req.item} is ${base_price:.2f}.",
            "accepted": False,
            "offered_price": base_price,
            "discount_percent": 0
        }
    
    # Store vendor response in history
    vendor_entry = {
        "role": "vendor",
        "message": result.get("vendor_response", ""),
        "item": req.item,
        "offered_price": result.get("offered_price"),
        "accepted": result.get("accepted", False),
        "timestamp": datetime.datetime.now().isoformat()
    }
    vendor.negotiation_history[history_key].append(vendor_entry)
    
    # If accepted, update the vendor's negotiated price for this player
    if result.get("accepted") and result.get("offered_price"):
        if hasattr(vendor, 'negotiated_discounts'):
            if req.agent_id not in vendor.negotiated_discounts:
                vendor.negotiated_discounts[req.agent_id] = {}
            # Store as multiplier: offered_price / base_price
            vendor.negotiated_discounts[req.agent_id][req.item] = result["offered_price"] / base_price
    
    return {
        "vendor_id": req.vendor_id,
        "vendor_name": vendor_profile["name"],
        "item": req.item,
        "player_message": req.message,
        "vendor_response": result.get("vendor_response", ""),
        "accepted": result.get("accepted", False),
        "offered_price": result.get("offered_price"),
        "discount_percent": result.get("discount_percent", 0),
        "base_price": base_price
    }


@app.get("/negotiate/history/{vendor_id}/{agent_id}")
def get_negotiation_history(vendor_id: str, agent_id: str, item: Optional[str] = None):
    """
    Get negotiation history between a player and vendor.
    Optionally filter by item.
    """
    if agent_id != "p1":
        raise HTTPException(status_code=403, detail="Only p1 history accessible")
    
    vendor = game.vendor_manager.get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    history = vendor.negotiation_history.get(agent_id, [])
    
    if item:
        history = [h for h in history if h.get("item") == item]
    
    return {
        "vendor_id": vendor_id,
        "agent_id": agent_id,
        "item_filter": item,
        "history": history[-50:]  # Last 50 messages
    }


@app.post("/proposals")
def submit_proposal(req: ProposalRequest):
    """Submit a new revenue stream proposal"""
    if req.agent_id != "p1":
        raise HTTPException(status_code=403, detail="Only p1 can submit proposals")
        
    proposal = game.engine.proposal_manager.submit_proposal(
        req.agent_id, 
        req.dict(), 
        game.engine.time_system.current_week
    )
    
    return {
        "status": "submitted", 
        "proposal": proposal.__dict__
    }

@app.get("/proposals")
def get_proposals(agent_id: str = "p1"):
    """Get proposals for an agent"""
    proposals = game.engine.proposal_manager.get_proposals(agent_id)
    return {"proposals": [p.__dict__ for p in proposals]}

@app.post("/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: str):
    """Approve a proposal (Admin/Debug or Auto-approve for prototype)"""
    success = game.engine.proposal_manager.approve_proposal(proposal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"status": "approved"}

@app.post("/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: str):
    """Reject a proposal"""
    success = game.engine.proposal_manager.reject_proposal(proposal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"status": "rejected"}


# --- Enhanced System Endpoints ---



@app.get("/credit/{agent_id}")
def get_credit_report(agent_id: str):
    """Get detailed credit report including score and loans"""
    if hasattr(game.engine, 'get_credit_report'):
        return {"credit": game.engine.get_credit_report(agent_id)}
    raise HTTPException(status_code=501, detail="Credit system not initialized")

@app.post("/credit/{agent_id}/payment")
def make_credit_payment(agent_id: str, req: CreditPaymentRequest):
    """Process a loan payment"""
    if req.amount <= 0:
         raise HTTPException(status_code=400, detail="Payment amount must be positive")
    
    # We use the generic action pipeline to ensure fair play and logging
    try:
        action = Action(type=ActionType.MAKE_PAYMENT, parameters={
            "payment_id": req.payment_id,
            "amount": req.amount
        })
        
        # Apply specifically to p1 if it's p1, otherwise would need logic
        # For now, this endpoint acts as a direct interface for the UI
        # But to keep state consistent, we should verify balance
        
        state = game.engine.states.get(agent_id)
        if not state:
            raise HTTPException(status_code=404, detail="Agent not found")
            
        if state.balance < req.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
            
        # Delegate to engine's credit system directly for the API call
        # In a strict turn-based system, this might be queued, but for "Real-time" UI:
        result = game.engine.credit_system.make_payment(
            agent_id, req.payment_id, req.amount, game.engine.time_system.current_week
        )
        
        # Apply action IMMEDIATELY via Engine
        # We model_dump() because _apply_action expects a dict
        game.engine.apply_action(state, action.model_dump())
        
        return {"status": "success", "new_balance": state.balance, "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/{agent_id}")
def get_calendar(agent_id: str, week: Optional[int] = None):
    """Get agent's calendar and schedule"""
    if hasattr(game.engine, 'get_calendar'):
        cal = game.engine.get_calendar(agent_id)
        current_week = week or game.engine.time_system.current_week
        stats = cal.get_statistics()
        schedule = cal.get_week_schedule(current_week)
        
        # Convert schedule objects to dicts
        schedule_dict = {}
        for day, actions in schedule.items():
            schedule_dict[day] = [a.__dict__ for a in actions]
            
        return {
            "statistics": stats,
            "schedule": schedule_dict,
            "week": current_week
        }
    raise HTTPException(status_code=501, detail="Calendar system not initialized")

@app.get("/zone/{agent_id}")
def get_zone_info(agent_id: str):
    """Get neighborhood zone information"""
    if hasattr(game.engine, 'get_zone_info'):
        return {"zone": game.engine.get_zone_info(agent_id)}
    raise HTTPException(status_code=501, detail="Neighborhood system not initialized")


# --- Event Ledger Endpoints ---
@app.get("/events")
def get_events(
    agent_id: str = "p1",
    category: Optional[str] = None,
    week_start: Optional[int] = None,
    week_end: Optional[int] = None,
    limit: int = 50
):
    """
    Query game events from the event ledger.
    
    Categories: ticket, dilemma, message, trade, regulator, game_master, alliance, market, achievement, system
    """
    state = game.engine.states.get(agent_id)
    if not state:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    events = state.event_ledger.query(
        category=category,
        agent_id=agent_id,
        week_start=week_start,
        week_end=week_end,
        limit=limit
    )
    
    return {
        "agent_id": agent_id,
        "total": len(events),
        "events": [e.to_dict() for e in events],
        "counts_by_category": state.event_ledger.count_by_category()
    }



@app.post("/diplomacy/propose")
def propose_diplomacy(req: DiplomacyProposalRequest):
    """Propose a diplomatic action (Alliance, etc.)"""
    # Simply log for now, as full mechanics are pending
    print(f"[DIPLOMACY] {req.agent_id} proposed {req.type} to {req.target_id}")
    
    # Store in event manager or simply return success signal
    # In future: game.engine.trust_system.propose_alliance(req.agent_id, req.target_id)
    
    return {
        "status": "proposed",
        "message": f"Proposal sent to {req.target_id}. They will consider it."
    }


@app.post("/next_turn")
def next_turn():
    """Advance to next week - AI agents take actions"""
    # 1. AI Agents Decide and Act
    ai_actions = {}
    
    # Initialize AI thoughts history if not exists
    if not hasattr(game, 'ai_thoughts_history'):
        game.ai_thoughts_history = []
    
    game.ai_thoughts = {}  # Current turn only
    
    # Update market prices
    game.vendor_manager.update_all_markets(game.engine.time_system.current_week)
    
    print(f"\n[TURN] Week {game.engine.time_system.current_week} Day {game.engine.time_system.current_day.value} - Processing AI agents...")
    
    for agent in game.agents:
        if agent.id == "p1":
            continue
        
        print(f"[AGENT] Processing {agent.id} ({agent.name})...")
        
        my_state = game.engine.states[agent.id]
        competitors = [game.engine.states[k] for k in game.engine.states if k != agent.id]
        
        state_before = my_state.model_dump(mode='json', exclude={'ledger'})
        state_before['balance'] = my_state.balance

        
        obs = Observation(
            week=game.engine.time_system.current_week,
            day=game.engine.time_system.current_day.value,
            phase=game.engine.time_system.current_phase.value,
            season=game.engine.time_system.current_season.value,
            my_stats=state_before,
            competitor_stats=[c.model_dump(mode='json', exclude={'ledger'}) for c in competitors],
            messages=game.engine.communication.get_messages(agent.id),
            events=[e.description for e in game.engine.event_manager.active_events],
            alliances=[str(a) for a in game.engine.trust_system.active_alliances if agent.id in a.members],
            trust_scores=game.engine.trust_system.trust_matrix.get(agent.id, {}),
            market_data={v.profile.id: v.get_market_status() for v in game.vendor_manager.get_all_vendors()},
            # New enhanced data
            credit_info=game.engine.credit_system.get_credit_report(agent.id) if hasattr(game.engine, 'credit_system') else None,
            zone_info=game.engine.get_zone_info(agent.id) if hasattr(game.engine, 'get_zone_info') else None,
            calendar_info=game.engine.calendar_manager.get_calendar(agent.id).get_statistics() if hasattr(game.engine, 'calendar_manager') else None,
            ethical_dilemma=game.engine.ethical_events.get_active_dilemma(agent.id).__dict__ if hasattr(game.engine, 'ethical_events') and game.engine.ethical_events.get_active_dilemma(agent.id) else None
        )
        
        # Get action
        # Get actions
        actions = agent.decide_action(obs)
        
        # Metadata access safe for both LLM and Human agents
        thinking = getattr(agent, "last_thinking", [])
        raw_response = getattr(agent, "last_raw_response", "")
        llm_provider = getattr(agent, "llm_provider", "Unknown")
        
        all_actions = actions
        
        ai_actions[agent.id] = all_actions
        
        print(f"[AGENT] {agent.id} generated {len(all_actions)} actions: {[a.type.name for a in all_actions]}")
        
        # Submit actions to Engine
        for a in all_actions:
            engine_action = {"type": "WAIT"}
            if a.type == ActionType.SET_PRICE:
                engine_action = {"type": "SET_PRICE", "amount": a.parameters.get("price")}
            elif a.type == ActionType.BUY_SUPPLIES:
                engine_action = {"type": "BUY_INVENTORY", "item": a.parameters.get("item"), "quantity": a.parameters.get("quantity")}
            elif a.type == ActionType.MARKETING_CAMPAIGN:
                engine_action = {"type": "MARKETING", "amount": a.parameters.get("cost")}
            elif a.type == ActionType.SEND_MESSAGE:
                engine_action = {"type": "SEND_MESSAGE", "recipient": a.parameters.get("recipient"), "content": a.parameters.get("content")}
            elif a.type == ActionType.NEGOTIATE:
                engine_action = {"type": "NEGOTIATE", "item": a.parameters.get("item"), "vendor_id": a.parameters.get("vendor_id", "bulkwash")}
            elif a.type == ActionType.RESOLVE_TICKET:
                engine_action = {"type": "RESOLVE_TICKET", "ticket_id": a.parameters.get("ticket_id")}
            elif a.type == ActionType.UPGRADE_MACHINE:
                engine_action = {"type": "UPGRADE_MACHINE"}
            
            game.engine.submit_action(agent.id, engine_action)
        
        state_after = my_state.model_dump(mode='json', exclude={'ledger'}) # Snapshot before processing
        state_after['balance'] = my_state.balance

        
        # Store AI thinking (including raw response for debugging)
        game.ai_thoughts[agent.id] = {
            "name": my_state.name,
            "thinking": thinking,
            "actions": [a.type.value for a in all_actions],
            "raw_response": raw_response  # Full LLM output for debugging
        }
        
        # Log AI response to file for analysis
        _log_ai_response(agent.id, game.engine.time_system.current_week, thinking, all_actions, raw_response)
        
        # Record turn
        _record_turn(
            agent.id, my_state.name,
            thinking, all_actions, raw_response,
            state_before, state_after,
            [c.model_dump(mode='json', exclude={'ledger'}) for c in competitors],
            [e.description for e in game.engine.event_manager.active_events],
            is_human=False, llm_provider=llm_provider
        )
    
    # Archive this turn's AI thoughts to history
    game.ai_thoughts_history.append({
        'week': game.engine.time_system.current_week,
        'thoughts': game.ai_thoughts.copy()
    })
    
    # Keep only last 10 turns in history to avoid memory bloat
    if len(game.ai_thoughts_history) > 10:
        game.ai_thoughts_history = game.ai_thoughts_history[-10:]
    
    print(f"[TURN] Completed AI processing. Archived thoughts for week {game.engine.time_system.current_week}")

    # 2. Process Turn via Engine (Daily)
    turn_results = game.engine.process_daily_turn()
    
    # If mid-week, the results are just status. If week-rolled, results has financials.
    if turn_results.get("status") == "day_advanced":
        pass # Just a day click
    else:
        # Week Rolled Over - Results contain financials
        pass
    
    # 3. Customer Simulation (Optional: Engine does basic revenue, but we can keep detailed customer logic if we want)
    # For now, we'll trust the Engine's revenue calculation which includes seasonal mods
    # But we can still run the customer "visits" to generate thoughts/tickets
    
    laundromat_list = list(game.engine.states.values())
    for customer in game.customers:
        choice = customer.decide_laundromat(laundromat_list)
        if choice:
            customer.visit_laundromat(choice, game.engine.time_system.current_week)
            # We don't add revenue here because Engine already did it
    
    # 4. Advance Week Counter (Manually now)
    
    # [FIX] Record P1 (Human) History for Dashboard
    # This ensures "end of week" state including sales/inventory changes is captured
    p1_state = game.engine.states.get("p1")
    if p1_state:
        # Capture state after daily processing
        state_dump = p1_state.model_dump(mode='json', exclude={'ledger'})
        state_dump['balance'] = p1_state.balance
        
        # We don't have human actions here (they were API calls), but we need the state point
        # We pass empty lists for actions/thinking
        competitors = [game.engine.states[k].model_dump(mode='json', exclude={'ledger'}) for k in game.engine.states if k != "p1"]
        events = [e.description for e in game.engine.event_manager.active_events]
        
        _record_turn(
            "p1", "Human Player",
            [], [], "", # No thinking/actions/response in this summary record
            state_dump, state_dump, # Before/After are same here (snapshot)
            competitors, events,
            is_human=True
        )

    game.engine.time_system.advance_week()
    print(f"[TURN] Advanced to Week {game.engine.time_system.current_week}")

    return get_state()

@app.post("/next_day")
def next_day():
    """Advance to next day. If week ends, trigger next_turn."""
    
    # Check if we are at the end of the week (Sunday)
    is_sunday = game.engine.time_system.current_day == Day.SUNDAY
    
    if is_sunday:
        return next_turn()
    else:
        # Advance day
        game.engine.time_system.advance_day()
        
        # Simulate Daily Activity (Customers)
        # We assume customers visit daily, but financial processing (bills) is weekly
        laundromat_list = list(game.engine.states.values())
        daily_revenue = 0
        for customer in game.customers:
            # Simple daily decision
            choice = customer.decide_laundromat(laundromat_list)
            if choice:
                # Visit generates revenue in the state immediately
                customer.visit_laundromat(choice, game.engine.time_system.current_week)
        
        print(f"[DAY] Advanced to {game.engine.time_system.current_day.value} (Simulated Daily Traffic)")
        return get_state()


# --- Scenario Endpoints ---
@app.get("/scenarios")
def get_scenarios():
    """Get list of available scenarios"""
    scenarios = []
    for name in list_scenarios():
        scenario = get_scenario(name)
        scenarios.append({
            "name": name,
            "description": scenario.description,
            "difficulty": scenario.difficulty.value,
            "weeks": scenario.weeks
        })
    return {"scenarios": scenarios}


@app.post("/start_scenario")
def start_scenario(req: ScenarioRequest):
    """Start a new game with specified scenario"""
    global game
    game = GameWrapper(scenario_name=req.scenario_name)
    return {
        "status": "started",
        "scenario": req.scenario_name,
        "message": f"Game started with scenario: {req.scenario_name or 'Free Play'}"
    }
# --- Revenue Stream Endpoints ---

# --- Market Trends Endpoint ---
@app.get("/market")
def get_market_trends():
    """Get current market trends and resource prices"""
    report = game.engine.market_system.get_market_report() if hasattr(game.engine, 'market_system') else {}
    
    # Also include vendor pricing for comparison
    vendor_prices = {}
    for vendor in game.vendor_manager.vendors.values():
        vendor_prices[vendor.id] = {
            "name": vendor.name,
            "prices": vendor.profile.base_prices if hasattr(vendor, 'profile') else {}
        }
    
    return {
        "current_week": game.engine.time_system.current_week,
        "trend": report,
        "vendor_prices": vendor_prices,
        "supply_chain_events": game.vendor_manager.get_active_supply_chain_events()
    }


class PriceUpdateRequest(BaseModel):
    agent_id: str
    price: float

@app.put("/revenue_streams/{stream_name}")
def update_revenue_stream_price(stream_name: str, request: PriceUpdateRequest):
    """Update the price of a revenue stream"""
    state = game.engine.get_state(request.agent_id)
    if not state:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if stream_name not in state.revenue_streams:
        raise HTTPException(status_code=404, detail=f"Revenue stream '{stream_name}' not found")
    
    if request.price < 0.01:
        raise HTTPException(status_code=400, detail="Price must be positive")
    
    stream = state.revenue_streams[stream_name]
    old_price = stream.price
    stream.price = request.price
    stream.cost_per_unit = request.price * 0.3  # Update cost proportionally
    
    return {
        "status": "updated",
        "stream": stream_name,
        "old_price": old_price,
        "new_price": request.price
    }


class ActivateRequest(BaseModel):
    agent_id: str


@app.post("/revenue_streams/{stream_name}/activate")
def activate_revenue_stream(stream_name: str, request: ActivateRequest):
    """Activate an inactive revenue stream"""
    state = game.engine.get_state(request.agent_id)
    if not state:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if stream_name not in state.revenue_streams:
        raise HTTPException(status_code=404, detail=f"Revenue stream '{stream_name}' not found")
    
    stream = state.revenue_streams[stream_name]
    
    # RevenueStream uses 'unlocked' not 'active'
    if stream.unlocked:
        return {"status": "already_active", "stream": stream_name}
    
    # Check if there's a setup cost and if balance covers it
    setup_cost = getattr(stream, 'setup_cost', 0) or 0
    if setup_cost > 0 and state.balance < setup_cost:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Need ${setup_cost:.2f}")
    
    # Deduct setup cost if applicable
    if setup_cost > 0:
        state.balance -= setup_cost
    
    # Activate the stream
    stream.unlocked = True
    
    return {
        "status": "activated",
        "stream": stream_name,
        "setup_cost_paid": setup_cost,
        "new_balance": state.balance
    }


# --- Proposal Endpoints ---
from src.engine.commerce.proposals import ProposalManager, ProposalStatus

# Initialize proposal manager (if not exists) 
proposal_manager = ProposalManager(game.engine) if hasattr(game, 'engine') else None

class ProposalRequest(BaseModel):
    agent_id: str
    name: str
    category: str
    description: str
    pricing_model: str = ""
    resource_requirements: str = ""
    setup_cost: float = 0.0

@app.get("/proposals")
def get_proposals(agent_id: str):
    """Get all proposals for an agent"""
    global proposal_manager
    if proposal_manager is None:
        proposal_manager = ProposalManager(game.engine)
    
    proposals = proposal_manager.get_proposals(agent_id)
    return {
        "proposals": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "status": p.status.value,
                "evaluation": p.evaluation
            } for p in proposals
        ]
    }

@app.post("/proposals")
def submit_proposal(request: ProposalRequest):
    """Submit a new proposal"""
    global proposal_manager
    if proposal_manager is None:
        proposal_manager = ProposalManager(game.engine)
    
    proposal = proposal_manager.submit_proposal(
        request.agent_id,
        {
            "name": request.name,
            "category": request.category,
            "description": request.description,
            "pricing_model": request.pricing_model,
            "resource_requirements": request.resource_requirements
        },
        game.engine.time_system.current_week
    )
    
    # Deduct setup cost from balance if specified
    if request.setup_cost > 0:
        state = game.engine.get_state(request.agent_id)
        if state and state.balance >= request.setup_cost:
            state.balance -= request.setup_cost
    
    return {
        "status": "submitted",
        "proposal_id": proposal.id,
        "evaluation": proposal.evaluation
    }

@app.post("/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: str):
    """Approve a proposal and add it as revenue stream"""
    global proposal_manager
    if proposal_manager is None:
        proposal_manager = ProposalManager(game.engine)
    
    success = proposal_manager.approve_proposal(proposal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    return {"status": "approved", "proposal_id": proposal_id}

@app.post("/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: str):
    """Reject a proposal"""
    global proposal_manager
    if proposal_manager is None:
        proposal_manager = ProposalManager(game.engine)
    
    success = proposal_manager.reject_proposal(proposal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    return {"status": "rejected", "proposal_id": proposal_id}


# --- History Endpoints ---
@app.get("/history")
def get_history():
    """Get full game history"""
    return game.history.to_dict()


@app.get("/history/comparison")
def get_comparison():
    """Get side-by-side participant comparison"""
    return game.history.generate_comparison_report()


@app.get("/history/thinking")
def get_thinking_timeline(agent_id: Optional[str] = None):
    """Get thinking timeline for all or specific agent"""
    return {"timeline": game.history.get_thinking_timeline(agent_id)}


@app.post("/history/export")
def export_history(filename: str = "game_history.json"):
    """Export history to JSON file"""
    os.makedirs("results", exist_ok=True)
    filepath = f"results/{filename}"
    game.history.export_to_json(filepath)
    return {"status": "exported", "path": filepath}


@app.get("/ai_thoughts")
def get_ai_thoughts():
    """Get latest AI thinking from this turn"""
    return {"thoughts": game.ai_thoughts}


@app.get("/ai_thoughts_history")
def get_ai_thoughts_history():
    """Get full history of AI thoughts across recent turns"""
    return {
        "current_turn": game.ai_thoughts,
        "history": getattr(game, 'ai_thoughts_history', []),
        "total_turns": len(getattr(game, 'ai_thoughts_history', []))
    }


@app.get("/history/{agent_id}")
def get_history(agent_id: str):
    """Get historical data for an agent"""
    if not game.history:
        return []
    
    records = game.history.get_agent_history(agent_id)
    # Convert dataclasses to dicts
    from dataclasses import asdict
    return [asdict(r) for r in records]


@app.get("/inventory")
def get_inventory(agent_id: str = "p1"):
    """Get current inventory and pending deliveries for an agent"""
    state = game.engine.get_state(agent_id)
    if not state:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "agent_id": agent_id,
        "inventory": state.inventory,
        "pending_deliveries": state.pending_deliveries,
        "inventory_metrics": state.get_inventory_metrics() if hasattr(state, 'get_inventory_metrics') else {}
    }


# --- Reset Endpoint ---
@app.post("/reset")
def reset_game():
    """Reset the game to initial state"""
    global game, proposal_manager
    scenario = game.scenario_name  # Preserve scenario choice
    game = GameWrapper(scenario_name=scenario)
    proposal_manager = None  # Reset proposal manager
    return {"status": "reset", "message": "Game has been reset", "scenario": scenario}

# ═══════════════════════════════════════════════════════════════════════
# NEW ENDPOINTS: Credit, Calendar, Neighborhood Systems
# ═══════════════════════════════════════════════════════════════════════

@app.get("/credit/{agent_id}")
def get_credit_report(agent_id: str):
    """Get full credit report for an agent"""
    try:
        # Use FinancialSystem -> CreditSystem
        report = game.engine.financial_system.credit_system.get_credit_report(agent_id)
        
        # Merge Pending Bills from State (Source of Truth)
        state = game.engine.states.get(agent_id)
        if state and hasattr(state, 'bills'):
            pending_bills = []
            for bill in state.bills:
                if not bill.is_paid:
                    pending_bills.append({
                        "payment_id": bill.id,
                        "amount": bill.amount,
                        "due_week": bill.due_week,
                        "status": "pending",
                        "date": f"Week {bill.due_week} (Due)",
                        "description": bill.name
                    })
            
            # Inject into payment_history (prepend pending)
            if "payment_history" in report:
                 # Ensure we are adding to a list
                 if isinstance(report["payment_history"], list):
                     report["payment_history"] = pending_bills + report["payment_history"]
                 elif isinstance(report["payment_history"], dict) and "rows" in report["payment_history"]:
                     # If it's the dict format from CreditSystem, we need to adapt
                     # But for now assume it might be a list or we just add it to the 'rows'
                     pass 
            else:
                 report["payment_history"] = pending_bills
                 
        return {"agent_id": agent_id, "credit": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PaymentRequest(BaseModel):
    payment_id: str
    amount: float


@app.post("/credit/{agent_id}/payment")
def make_credit_payment(agent_id: str, request: PaymentRequest):
    """Make a payment on a loan or bill"""
    try:
        state = game.engine.get_state(agent_id)
        if not state:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Delegate to FinancialSystem
        result = game.engine.financial_system.pay_bill(
            state, 
            request.payment_id, 
            game.engine.time_system.current_week
        )
        
        if not result["success"]:
             # If error, try to return useful message
             raise HTTPException(status_code=400, detail=result.get("error", "Payment failed"))

        return {
            "status": "paid",
            "payment_id": request.payment_id,
            "amount": result["amount"],
            "new_balance": result["new_balance"],
            "new_credit_score": game.engine.financial_system.credit_system.agent_credit[agent_id].total_score
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/calendar/{agent_id}")
def get_calendar(agent_id: str, week: int = None):
    """Get calendar for an agent"""
    try:
        calendar = game.engine.get_calendar(agent_id)
        current_week = week or game.engine.time_system.current_week
        
        cal_data = calendar.to_dict(current_week)
        return {
            "agent_id": agent_id,
            "week": current_week,
            "schedule": cal_data["week_schedule"],
            "statistics": calendar.get_statistics()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ScheduleRequest(BaseModel):
    category: str
    title: str
    description: str = ""
    week: int
    day: int = 1
    priority: str = "medium"
    is_recurring: bool = False
    recurrence_weeks: int = 0


@app.post("/calendar/{agent_id}/schedule")
def schedule_action(agent_id: str, request: ScheduleRequest):
    """Schedule an action on the calendar"""
    from src.engine.core.calendar import ActionCategory, ActionPriority
    
    try:
        calendar = game.engine.get_calendar(agent_id)
        
        # Map string to enum
        try:
            category = ActionCategory(request.category)
        except ValueError:
            category = ActionCategory.CUSTOM
        
        try:
            priority = ActionPriority(request.priority)
        except ValueError:
            priority = ActionPriority.MEDIUM
        
        action = calendar.schedule_action(
            category=category,
            title=request.title,
            description=request.description or request.title,
            week=request.week,
            day=request.day,
            priority=priority,
            is_recurring=request.is_recurring,
            recurrence_weeks=request.recurrence_weeks,
            current_week=game.engine.time_system.current_week
        )
        
        return {
            "status": "scheduled",
            "action_id": action.id,
            "week": request.week,
            "day": request.day
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/calendar/{agent_id}/action/{action_id}")
def delete_calendar_action(agent_id: str, action_id: str):
    """Delete/cancel a calendar action"""
    try:
        calendar = game.engine.get_calendar(agent_id)
        result = calendar.cancel_action(action_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return {"status": "deleted", "action_id": action_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateActionRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    week: Optional[int] = None
    day: Optional[int] = None
    priority: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_weeks: Optional[int] = None


@app.put("/calendar/{agent_id}/action/{action_id}")
def update_calendar_action(agent_id: str, action_id: str, request: UpdateActionRequest):
    """Update a calendar action"""
    from src.engine.core.calendar import ActionPriority
    
    try:
        calendar = game.engine.get_calendar(agent_id)
        action = calendar.scheduled_actions.get(action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Action not found")
        
        # Update fields if provided
        if request.title is not None:
            action.title = request.title
        if request.description is not None:
            action.description = request.description
        if request.week is not None:
            action.scheduled_week = request.week
        if request.day is not None:
            action.scheduled_day = request.day
        if request.priority is not None:
            try:
                action.priority = ActionPriority(request.priority)
            except ValueError:
                pass
        if request.is_recurring is not None:
            action.is_recurring = request.is_recurring
        if request.recurrence_weeks is not None:
            action.recurrence_weeks = request.recurrence_weeks
        
        return {
            "status": "updated",
            "action_id": action_id,
            "action": {
                "id": action.id,
                "title": action.title,
                "description": action.description,
                "week": action.scheduled_week,
                "day": action.scheduled_day,
                "priority": action.priority.value,
                "is_recurring": action.is_recurring,
                "recurrence_weeks": action.recurrence_weeks
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/zone/{agent_id}")
def get_zone_info(agent_id: str):
    """Get neighborhood zone info for an agent"""
    try:
        zone_info = game.engine.get_zone_info(agent_id)
        return {"agent_id": agent_id, "zone": zone_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/zones")
def get_all_zones():
    """Get all neighborhood zones"""
    try:
        return {"zones": game.engine.neighborhood.get_zone_summary()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/enhanced_state")
def get_enhanced_state(agent_id: str = "p1"):
    """Get enhanced game state including credit, calendar, and zone data"""
    try:
        base_state = get_state(agent_id)
        
        # Add enhanced data
        enhanced = {
            **base_state,
            "credit": game.engine.financial_system.credit_system.get_credit_report(agent_id),
            "zone": game.engine.get_zone_info(agent_id),
            "calendar_stats": game.engine.get_calendar(agent_id).get_statistics()
        }
        
        return enhanced
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

