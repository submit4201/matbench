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

from src.config import LLMDICT


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import uvicorn
import json

from src.engine.time import TimeSystem
from src.engine.events import EventManager
from src.engine.customer import Customer
from src.engine.history import GameHistory, TurnRecord
from src.world.laundromat import LaundromatState
from src.world.ticket import TicketStatus
from src.engine.vendor import VendorManager, VendorTier
from src.engine.game_engine import GameEngine # New Engine
from src.agents.human_agent import HumanAgent
from src.agents.llm_agent import LLMAgent
from src.agents.base_agent import Action, ActionType, Observation
from src.benchmark.scenarios import get_scenario, list_scenarios, Scenario

app = FastAPI(title="Laundromat Tycoon", version="1.0.0")

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
        
        # Initialize Game Engine
        self.engine = GameEngine(["p1", "p2", "p3"])
        
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
            state.balance = initial.balance
            # state.machines = initial.machines # Need to convert int to list of Machine objects if needed
            state.inventory = initial.inventory.copy()

game = GameWrapper()


# --- Pydantic Models ---
class ActionRequest(BaseModel):
    agent_id: str
    action_type: str
    parameters: Dict[str, Any]


class ScenarioRequest(BaseModel):
    scenario_name: Optional[str] = None


class NegotiateRequest(BaseModel):
    agent_id: str
    vendor_id: str
    item: str

class ProposalRequest(BaseModel):
    agent_id: str
    name: str
    category: str
    description: str
    pricing_model: str
    resource_requirements: str


# --- Helper Functions ---
def _serialize_state(laundromat_state):
    data = laundromat_state.__dict__.copy()
    
    if 'id' not in data:
        data['id'] = getattr(laundromat_state, 'id', 'unknown')
    
    # Serialize SocialScore object
    if 'social_score' in data and hasattr(data['social_score'], 'to_dict'):
        data['social_score'] = data['social_score'].to_dict()
        
    # Ensure both reputation and social_score are available
    if 'reputation' not in data and 'social_score' in data:
        # If social_score is a dict (serialized), use total_score
        if isinstance(data['social_score'], dict):
             data['reputation'] = data['social_score'].get('total_score', 50.0)
        else:
             data['reputation'] = 50.0
    elif 'social_score' not in data and 'reputation' in data:
        # If social_score is missing, use reputation as total
        data['social_score'] = {'total_score': data['reputation']}
        
    # Expose active customers metric
    data['active_customers'] = getattr(laundromat_state, 'active_customers', 0)
        
    # Convert machines list to count for frontend compatibility
    if isinstance(data.get('machines'), list):
        data['machines'] = len(data['machines'])
        
    # Ensure broken_machines is included (it's a property, not in __dict__)
    if 'broken_machines' not in data:
        data['broken_machines'] = getattr(laundromat_state, 'broken_machines', 0)
    
    # Serialize Tickets
    if data.get("tickets"):
        tickets_data = []
        for t in data["tickets"]:
            try:
                t_dict = t.__dict__.copy()
                if hasattr(t_dict.get("type"), "value"):
                    t_dict["type"] = t_dict["type"].value
                if hasattr(t_dict.get("status"), "value"):
                    t_dict["status"] = t_dict["status"].value
                tickets_data.append(t_dict)
            except Exception as e:
                print(f"Error serializing ticket {t}: {e}")
                tickets_data.append(str(t))
        data["tickets"] = tickets_data
    
    # Inventory Metrics
    if hasattr(laundromat_state, 'get_inventory_metrics'):
        data['inventory_metrics'] = laundromat_state.get_inventory_metrics()
    
    # Serialize Revenue Streams
    if data.get("revenue_streams"):
        streams_data = {}
        for k, v in data["revenue_streams"].items():
            if hasattr(v, "__dict__"):
                streams_data[k] = v.__dict__
            else:
                streams_data[k] = str(v)
        data["revenue_streams"] = streams_data

    return data


def _log_ai_response(agent_id: str, week: int, thinking: List[str], actions: List[Action], raw_response: str):
    """Log AI response to file for analysis and debugging"""
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


def _apply_action(state: LaundromatState, action: Action):
    """Apply an action to a laundromat state"""
    if action.type == ActionType.SET_PRICE:
        state.price = action.parameters.get("price", state.price)
    elif action.type == ActionType.BUY_SUPPLIES:
        item = action.parameters.get("item")
        qty = action.parameters.get("quantity", 0)
        vendor_id = action.parameters.get("vendor_id", "bulkwash") # Default to BulkWash
        
        # Map 'soap' to 'detergent' for inventory compatibility
        inventory_item = "detergent" if item == "soap" else item
        
        vendor = game.vendor_manager.get_vendor(vendor_id)
        if not vendor:
            vendor = game.vendor_manager.get_vendor("bulkwash")
            
        unit_price = vendor.get_price(item, agent_id=state.id)
        cost = qty * unit_price
        
        if state.balance >= cost:
            state.balance -= cost
            
            # Process order in vendor to update relationship
            result = vendor.process_order(
                {item: qty}, 
                game.engine.time_system.current_week,
                game.vendor_manager.supply_chain,
                agent_id=state.id
            )
            
            # Determine arrival time
            delivery_days = vendor.profile.delivery_days
            arrival_offset = 0
            if delivery_days > 2:
                arrival_offset = 1 + (delivery_days - 3) // 7
            
            arrival_week = game.engine.time_system.current_week + arrival_offset
            
            # Apply inventory update based on result (handling partial shipments)
            actual_qty = int(qty * result.get("quantity_multiplier", 1.0))
            
            if arrival_week <= game.engine.time_system.current_week:
                # Use the inventory_item key (detergent) instead of vendor item (soap)
                state.inventory[inventory_item] = state.inventory.get(inventory_item, 0) + actual_qty
            else:
                state.pending_deliveries.append({
                    "item": inventory_item,  # Store as inventory key
                    "quantity": actual_qty,
                    "arrival_week": arrival_week,
                    "vendor_name": vendor.profile.name
                })
                
            if result.get("events"):
                for event_desc in result["events"]:
                    game.engine.event_manager.active_events.append(
                        # Create a temporary event for notification (must include target_agent_id)
                        type("TempEvent", (), {"description": f"Supply Chain: {event_desc}", "target_agent_id": None, "type": None, "effect_data": {}, "duration": 1})()
                    )


            
    elif action.type == ActionType.RESOLVE_TICKET:
        ticket_id = action.parameters.get("ticket_id")
        for t in state.tickets:
            if t.id == ticket_id and t.status == TicketStatus.OPEN:
                t.status = TicketStatus.RESOLVED
                # Increased from 2.0 to 5.0 for more noticeable reputation impact
                state.update_social_score("customer_satisfaction", 5.0)
    elif action.type == ActionType.UPGRADE_MACHINE:
        if state.balance >= 500:
            state.balance -= 500
            # Handle both list and int types for machines
            if isinstance(state.machines, list):
                from src.world.laundromat import Machine
                state.machines.append(Machine(f"washer_{len(state.machines)+1}", "washer"))
            else:
                state.machines += 1
    elif action.type == ActionType.MARKETING_CAMPAIGN:
        cost = action.parameters.get("cost", 0)
        if state.balance >= cost:
            state.balance -= cost
            # Increased boost from cost/50 to cost/20 for better impact
            boost = cost / 20.0
            state.update_social_score("community_standing", boost)
            state.marketing_boost += boost


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
        laundromats_data[pid] = _serialize_state(l)

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
        "season": game.engine.time_system.current_season.value,
        "laundromats": laundromats_data,
        "events": [e.description for e in game.engine.event_manager.active_events],
        "messages": [str(m) for m in game.engine.communication.get_messages("p1")],
        "market": {
            "vendors": vendors_data,
            "supply_chain_events": game.vendor_manager.get_active_supply_chain_events()
        },
        "customer_thoughts": [c.current_thought for c in game.customers if c.current_thought],
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
        action = Action(action_type, req.parameters)
        
        state_before = _serialize_state(game.engine.states["p1"])
        
        # Apply action IMMEDIATELY for human player (no queuing - fair play with AI)
        my_state = game.engine.states["p1"]
        _apply_action(my_state, action)
        
        state_after = _serialize_state(game.engine.states["p1"])
        
        # Record human turn (no thinking for human actions via this endpoint)
        competitors = [_serialize_state(game.engine.states[k]) for k in game.engine.states if k != "p1"]
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
    
    print(f"\n[TURN] Week {game.engine.time_system.current_week} - Processing AI agents...")
    
    for agent in game.agents:
        if agent.id == "p1":
            continue
        
        print(f"[AGENT] Processing {agent.id} ({agent.name})...")
        
        my_state = game.engine.states[agent.id]
        competitors = [game.engine.states[k] for k in game.engine.states if k != agent.id]
        
        state_before = _serialize_state(my_state)
        
        obs = Observation(
            week=game.engine.time_system.current_week,
            season=game.engine.time_system.current_season.value,
            my_stats=state_before,
            competitor_stats=[_serialize_state(c) for c in competitors],
            messages=game.engine.communication.get_messages(agent.id),
            events=[e.description for e in game.engine.event_manager.active_events],
            alliances=[str(a) for a in game.engine.trust_system.active_alliances if agent.id in a.members],
            trust_scores=game.engine.trust_system.trust_matrix.get(agent.id, {}),
            market_data={v.profile.id: v.get_market_status() for v in game.vendor_manager.get_all_vendors()}
        )
        
        # Get action
        action = agent.decide_action(obs)
        ai_actions[agent.id] = action
        
        # Get all thinking and actions
        if hasattr(agent, 'get_last_thinking'):
            thinking = agent.get_last_thinking()
            all_actions = agent.get_all_actions() if hasattr(agent, 'get_all_actions') else [action]
            raw_response = getattr(agent, 'last_raw_response', '')
            llm_provider = getattr(agent, 'llm_provider', '')
            print(f"[AGENT] {agent.id} generated {len(all_actions)} actions: {[a.type.value for a in all_actions]}")
        else:
            thinking = []
            all_actions = [action]
            raw_response = ""
            llm_provider = ""
        
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
        
        state_after = _serialize_state(my_state) # Snapshot before processing
        
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
            [_serialize_state(c) for c in competitors],
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

    # 2. Process Turn via Engine
    turn_results = game.engine.process_turn()
    
    # 3. Customer Simulation (Optional: Engine does basic revenue, but we can keep detailed customer logic if we want)
    # For now, we'll trust the Engine's revenue calculation which includes seasonal mods
    # But we can still run the customer "visits" to generate thoughts/tickets
    
    laundromat_list = list(game.engine.states.values())
    for customer in game.customers:
        choice = customer.decide_laundromat(laundromat_list)
        if choice:
            customer.visit_laundromat(choice, game.engine.time_system.current_week)
            # We don't add revenue here because Engine already did it
    
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
from src.engine.proposals import ProposalManager, ProposalStatus

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

