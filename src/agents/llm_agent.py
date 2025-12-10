"""
LLM Agent for Laundromat Simulation

Uses OpenAI function calling for reliable structured action output.
Supports multiple AI providers via helper packages.
"""

import json
import os
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent, Observation, Action, ActionType
from src.config import settings
from src.config import LLMDICT
from dotenv import load_dotenv

# Import Registry
from src.agents.tools.registry import ToolRegistry
from src.agents.prompts.registry import PromptRegistry

# Import Provider Factory
from src.agents.providers.factory import LLMProviderFactory

# Load environment variables
load_dotenv()

# --- Initialize Tools from Registry ---
TOOLS = ToolRegistry.get_all_tools()

# Mapping from function names to ActionType
FUNCTION_TO_ACTION = {
    "set_price": ActionType.SET_PRICE,
    "buy_supplies": ActionType.BUY_SUPPLIES,
    "marketing_campaign": ActionType.MARKETING_CAMPAIGN,
    "upgrade_machine": ActionType.UPGRADE_MACHINE,
    "resolve_ticket": ActionType.RESOLVE_TICKET,
    "send_message": ActionType.SEND_MESSAGE,
    "propose_alliance": ActionType.PROPOSE_ALLIANCE,
    "initiate_buyout": ActionType.INITIATE_BUYOUT,
    "negotiate": ActionType.NEGOTIATE,
    "wait": ActionType.WAIT,
    
    # Extended Tools
    "make_payment": ActionType.MAKE_PAYMENT,
    "apply_for_loan": ActionType.APPLY_FOR_LOAN,
    "schedule_action": ActionType.SCHEDULE_ACTION,
    "send_dm": ActionType.SEND_DM,
    "send_public": ActionType.SEND_PUBLIC,
    "send_formal": ActionType.SEND_FORMAL,
    "resolve_dilemma": ActionType.RESOLVE_DILEMMA,

    # Active Perception
    "inspect_competitor": ActionType.INSPECT_COMPETITOR,
    "check_market_trends": ActionType.CHECK_MARKET_TRENDS,
    "read_news": ActionType.READ_NEWS,
    "inspect_facility": ActionType.INSPECT_FACILITY,
}

from src.utils.logger import get_logger

# Existing imports...

class LLMAgent(BaseAgent):
    """AI Agent that uses LLMs with function calling for structured output"""
    
    def __init__(self, agent_id: str, name: str, model: str = None, llm_provider: str = "AZURE"):
        super().__init__(agent_id, name)
        self.model = model or settings.simulation.agent_default_model
        self.llm_provider = llm_provider
        self.history = []  # Conversation history
        self.memory = "No past memory yet."  # Evolving memory note
        
        # Last turn data for history tracking
        self.last_thinking: List[str] = []
        self.last_actions: List[Action] = []
        self.last_raw_response: str = ""
        self.last_parse_errors: List[str] = []
        
        # These will be set by helper functions, not from LLMDICT directly
        self.api_key = None
        self.endpoint = None
        self.version = None
        self.deployment = None
        self.llm = None
        
        # Setup loggers
        self.logger = get_logger(f"agent.{agent_id}", category="agents")
        self.trace_logger = get_logger(f"trace.{agent_id}", category="traces")
        
        # Setup LLM client using helper packages
        self.logger.info(f"[{self.name}] Starting LLM initialization...")
        self._setup_llm(llm_provider)

    def _setup_llm(self, llm_name: str):
        """Initialize LLM client based on provider"""
        self.llm = LLMProviderFactory.create(llm_name, agent_name=self.name)

    def decide_action(self, observation: Observation) -> List[Action]:
        """
        Main decision loop for the agent.
        Implements Think-Act-React cycle.
        """
        print(f"[{self.name}] Starting Thinking Loop for Week {observation.week}")
        
        # 1. Initialize Loop State
        self.last_thinking = []
        self.last_actions = []
        actions_to_return = []
        
        # 2. Build Initial System & Turn Prompts
        system_prompt = PromptRegistry.get_system_prompt(
            agent_name=self.name, 
            past_self_note=self.memory # Inject persistent memory
        )
        
        # Initial turn context
        turn_context = PromptRegistry.get_turn_prompt(
            state_summary=self._build_prompt(observation), # Use existing prompt builder for summary
            memory_context=self.memory # Inject persistent memory
        )
        
        # Start conversation with System + Turn Context
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": turn_context}
        ]
        
        max_steps = 5 # Safety limit to prevent infinite loops
        step_count = 0
        turn_done = False
        
        while step_count < max_steps:
            step_count += 1
            print(f"[{self.name}] Loop Step {step_count}/{max_steps}")
            
            # 3. Call LLM
            response = self._call_llm_messages(messages)
            message = response.choices[0].message
            
            # Store reasoning if present
            if message.content:
                self.last_thinking.append(message.content)
            
            # Append to history if content or tool calls exist
            if message.content or (hasattr(message, 'tool_calls') and message.tool_calls):
                # Convert Message object to dict for history
                msg_dict = {"role": "assistant", "content": message.content}
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    # Convert tool calls to dict format if needed, or pass as is if helper handles it? 
                    # Helper expects OpenAI format dicts usually. 
                    # gemini_helper.ToolCall -> needs conversion
                     msg_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                     ]
                messages.append(msg_dict) # Add assistant thought to history
                
            # 4. Parse Actions
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') and message.tool_calls else []
            
            if not tool_calls:
                 # If LLM just talks and calls no tools, remind it to act or end
                messages.append({
                    "role": "user", 
                    "content": "You must verify your state with tools or call 'end_turn()' to finish."
                })
                continue

            # 5. Execute Tools & React
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    print(f"[{self.name}] Failed to parse args for {func_name}")
                    func_args = {}
                
                print(f"[{self.name}] Tool Call: {func_name}")
                
                # Handle End Turn Signal
                if func_name == "end_turn":
                    memory_note = func_args.get("memory_note", "")
                    print(f"[{self.name}] Ending Turn. Memory: {memory_note}")
                    if memory_note:
                        self.memory = memory_note # Update persistent memory
                        print(f"[{self.name}] 🧠 Memory Updated: {self.memory}")
                    turn_done = True
                    # Break the tool loop, then will break the main loop
                    break
                    
                # Handle Meta Tools (Immediate Feedback)
                if func_name == "get_tool_help":
                    tool_name = func_args.get("tool_name")
                    tool_def = ToolRegistry.get_tool(tool_name)
                    feedback = f"Documentation for {tool_name}: {json.dumps(tool_def, indent=2)}" if tool_def else f"Tool {tool_name} not found."
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name, 
                        "content": feedback
                    })
                    continue

                # Handle Immediate Perception Tools (Mocking data from Observation if possible or generic response)
                # Ideally, we should parse the Observation to answer these, or the Engine should process them.
                # Since LLMAgent is decoupled, we'll queue them as Actions if they need Engine data not in Observation,
                # BUT 'inspect_competitor' needs data NOW.
                # Hack: We look at 'observation.competitor_stats' for inspect_competitor.
                if func_name == "inspect_competitor":
                    comp_id = func_args.get("competitor_id")
                    # Find in observation
                    comp_data = next((c for c in observation.competitor_stats if c.get('id') == comp_id or c.get('name') == comp_id), None)
                    feedback = f"Competitor Data: {json.dumps(comp_data, indent=2)}" if comp_data else "Competitor not found in recent observation."
                    messages.append({
                        "role": "tool", 
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": feedback
                    })
                    continue

                if func_name == "read_news":
                    # Mock response for now as parsing Observation events is complex
                    feedback = f"Recent Events: {json.dumps(observation.events, indent=2)}"
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": feedback
                    })
                    continue
                    
                # Handle Game Actions (Deferred)
                action = self._parse_single_tool(func_name, func_args)
                if action:
                    actions_to_return.append(action)
                    # Simulate feedback for the agent
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,  # Required by Gemini helper
                        "content": f"Action {func_name} queued completely."
                    })
            
            if turn_done:
                break
                
        self.last_actions = actions_to_return
        # If no actions were gathered effectively but we ended turn, wait.
        return actions_to_return if actions_to_return else [Action(ActionType.WAIT)]

    def _call_llm_messages(self, messages: List[Dict]):
        """Helper to call LLM with full message history"""
        
        # Get model params - prefer client's configured model over self.model default
        model_name = self.model  # Fallback
        if hasattr(self.llm, 'model') and self.llm.model:
            model_name = self.llm.model  # Use model from client (set by factory from config)
        elif hasattr(self.llm, 'deployment_name') and self.llm.deployment_name:
            model_name = self.llm.deployment_name  # Azure uses deployment_name
        
        # O-series models (o1, o3) don't support temperature or tools in the same way
        is_o_series = model_name and (
            model_name.startswith('o1') or model_name.startswith('o3')
        )

        request_params = {
            "model": model_name,
            "messages": messages,
            "max_completion_tokens": settings.simulation.agent_max_tokens
        }
        
        if not is_o_series:
            request_params["tools"] = TOOLS
            request_params["temperature"] = settings.simulation.agent_temperature
        
        # TRACE LOG PROMPT
        self.trace_logger.debug(f"\n[{self.name}] >>> SENT TO LLM ({model_name}):\n{json.dumps(messages, indent=2, default=str)}")
        
        try:
            response = self.llm.chat.completions.create(**request_params)
            
            # TRACE LOG RESPONSE
            try:
                # Safe inspection for logging
                content = response.choices[0].message.content
                tool_calls = response.choices[0].message.tool_calls
                log_msg = f"\n[{self.name}] <<< RECEIVED FROM LLM:\nContent: {content}"
                if tool_calls:
                    log_msg += f"\nTools: {tool_calls}"
                self.trace_logger.debug(log_msg)
            except Exception as e:
                self.trace_logger.debug(f"[{self.name}] <<< RECEIVED (Parse Error in Logging): {response}")

            return response
        except Exception as e:
            self.logger.error(f"[{self.name}] LLM Loop Call Failed: {e}", exc_info=True)
            print(f"[{self.name}] LLM Loop Call Failed: {e}")
            raise e

    def _parse_single_tool(self, func_name: str, args: Dict) -> Optional[Action]:
        """Convert a single tool call to an Action object"""

        if func_name == "set_price":
            return Action(type=ActionType.SET_PRICE, parameters={"price": args.get("price", settings.economy.default_price)})
        
        elif func_name == "buy_supplies":
            # Handle multiple supplies by picking the first valid one found in args 
            # (since we return single Action, loop wrapper should ideally handle multiple actions but tool calls are list already)
            # If the LLM sends one tool call with {"soap": 5, "softener": 2}, we can only return one ActionType.BUY_SUPPLIES here?
            # Actually, `decide_action` iterates `tool_calls`. If LLM sends one tool call with multiple params, we might lose data if we only return one.
            # But `BUY_SUPPLIES` generic action usually expects `item` and `quantity`.
            # Let's fix this properly: ActionType.BUY_SUPPLIES could support a dict of items?
            # Engine `_apply_action` (lines 280-335) expects single "item" and "quantity".
            # So we MUST return single item. 
            # If LLM combines them, we just pick one. Ideally LLM should make disparate tool calls for each item.
            for k in ["soap", "softener", "parts", "cleaning_supplies"]:
                if k in args and args[k] > 0:
                    return Action(type=ActionType.BUY_SUPPLIES, parameters={"item": k, "quantity": args[k]})
            # Fallback
            return Action(type=ActionType.BUY_SUPPLIES, parameters={"item": "soap", "quantity": 10})
            
        elif func_name == "marketing_campaign":
            return Action(type=ActionType.MARKETING_CAMPAIGN, parameters={"cost": args.get("cost", 100)})
            
        elif func_name == "upgrade_machine":
            return Action(type=ActionType.UPGRADE_MACHINE, parameters={
                "count": args.get("count", 1), 
                "type": args.get("machine_type", "standard")
            })
        
        elif func_name == "wait":
             return Action(type=ActionType.WAIT)
             
        # Extended Tools
        elif func_name == "make_payment":
            return Action(type=ActionType.MAKE_PAYMENT, parameters={
                "payment_id": args.get("payment_id", ""),
                "amount": float(args.get("amount", 0))
            })
        
        elif func_name == "apply_for_loan":
            return Action(type=ActionType.APPLY_FOR_LOAN, parameters={
                "loan_type": args.get("loan_type", "equipment_loan"),
                "amount": float(args.get("amount", 1000))
            })

        elif func_name == "schedule_action":
            return Action(type=ActionType.SCHEDULE_ACTION, parameters={
                "category": args.get("category", "custom"),
                "title": args.get("title", "Scheduled Task"),
                "week": int(args.get("week", 1)),
                "day": int(args.get("day", 1)),
                "priority": args.get("priority", "medium"),
                "is_recurring": args.get("is_recurring", False)
            })

        elif func_name == "send_dm":
             return Action(type=ActionType.SEND_DM, parameters={
                "recipient_id": args.get("recipient_id", ""),
                "content": args.get("content", ""),
                "intent": args.get("intent", "chat")
             })

        elif func_name == "send_public":
             return Action(type=ActionType.SEND_PUBLIC, parameters={
                 "content": args.get("content", ""),
                 "intent": args.get("intent", "announcement")
             })

        elif func_name == "send_formal":
             return Action(type=ActionType.SEND_FORMAL, parameters={
                 "recipient_id": args.get("recipient_id", ""),
                 "content": args.get("content", ""),
                 "intent": args.get("intent", "proposal")
             })

        elif func_name == "resolve_dilemma":
             return Action(type=ActionType.RESOLVE_DILEMMA, parameters={
                 "dilemma_id": args.get("dilemma_id", ""),
                 "choice_id": args.get("choice_id", ""),
                 "reasoning": args.get("reasoning", "")
             })

        # Active Perception
        elif func_name == "inspect_competitor":
             return Action(type=ActionType.INSPECT_COMPETITOR, parameters={
                 "competitor_id": args.get("competitor_id", "")
             })

        elif func_name == "check_market_trends":
             return Action(type=ActionType.CHECK_MARKET_TRENDS, parameters={})

        elif func_name == "read_news":
             return Action(type=ActionType.READ_NEWS, parameters={})

        elif func_name == "inspect_facility":
             return Action(type=ActionType.INSPECT_FACILITY, parameters={})

        # Staff
        elif func_name == "hire_staff":
            return Action(type=ActionType.HIRE_STAFF, parameters={
                "role": args.get("role", "attendant")
            })

        elif func_name == "fire_staff":
            return Action(type=ActionType.FIRE_STAFF, parameters={
                "staff_id": args.get("staff_id", "")
            })

        elif func_name == "train_staff":
            return Action(type=ActionType.TRAIN_STAFF, parameters={
                "staff_id": args.get("staff_id", "")
            })

        # Maintenance
        elif func_name == "perform_maintenance":
            return Action(type=ActionType.PERFORM_MAINTENANCE, parameters={})

        # Vendor/Logistics
        elif func_name == "inspect_vendor":
            return Action(type=ActionType.INSPECT_VENDOR, parameters={
                "vendor_id": args.get("vendor_id", "")
            })

        elif func_name == "negotiate_contract":
            return Action(type=ActionType.NEGOTIATE_CONTRACT, parameters={
                "vendor_id": args.get("vendor_id", ""),
                "item": args.get("item", "soap")
            })

        elif func_name == "inspect_deliveries":
            return Action(type=ActionType.INSPECT_DELIVERIES, parameters={})

        elif func_name == "get_financial_report":
            return Action(type=ActionType.GET_FINANCIAL_REPORT, parameters={})

        elif func_name == "check_credit_score":
            return Action(type=ActionType.CHECK_CREDIT_SCORE, parameters={})

        elif func_name == "check_market_trends":
            return Action(type=ActionType.CHECK_MARKET_TRENDS, parameters={})

        # Final Gaps
        elif func_name == "emergency_repair":
            return Action(type=ActionType.EMERGENCY_REPAIR, parameters={
                "machine_id": args.get("machine_id", "")
            })

        elif func_name == "check_regulatory_requirements":
            return Action(type=ActionType.CHECK_REGULATIONS, parameters={})

        elif func_name == "check_reputation_score":
            return Action(type=ActionType.CHECK_REPUTATION, parameters={})
            
        elif func_name == "inspect_public_records":
            return Action(type=ActionType.INSPECT_PUBLIC_RECORDS, parameters={
                "entity_id": args.get("entity_id", "")
            })

        elif func_name in FUNCTION_TO_ACTION:
             return Action(type=FUNCTION_TO_ACTION[func_name], parameters=args)
             
        return None

    def _build_prompt(self, obs: Observation) -> str:
        """Build observation prompt for the LLM"""
        
        # Format tickets with full details
        tickets_section = ""
        if obs.my_stats.get("tickets"):
            open_tickets = [t for t in obs.my_stats["tickets"] if t.get("status") == "open"]
            if open_tickets:
                tickets_section = "\n📋 OPEN TICKETS (need resolution):\n"
                for t in open_tickets:
                    tickets_section += f"  - ID: {t.get('id')} | Type: {t.get('type')} | Severity: {t.get('severity', 'medium')}\n"
                    tickets_section += f"    Description: {t.get('description', 'No description')}\n"
        
        # Format incoming messages
        messages_section = ""
        if obs.messages:
            messages_section = "\n💬 INCOMING MESSAGES:\n"
            for msg in obs.messages[-5:]:
                messages_section += f"  - {msg}\n"
        
        # Format competitor analysis
        competitors_section = ""
        for c in obs.competitor_stats:
            c_name = c.get('name', 'Unknown')
            c_price = c.get('price', 0)
            c_social_raw = c.get('social_score', 0)
            c_social = c_social_raw.get('total_score', 50) if isinstance(c_social_raw, dict) else c_social_raw
            c_machines = c.get('machines', 0)
            c_balance = c.get('balance', 'Unknown')
            c_inventory = c.get('inventory', {})
            
            competitors_section += f"""
  {c_name}:
    Price: ${c_price:.2f} | Social Score: {c_social}/100 | Machines: {c_machines}
    Balance: ${c_balance if isinstance(c_balance, (int, float)) else 'Hidden'}
    Inventory: Soap={c_inventory.get('soap', 0)}, Softener={c_inventory.get('softener', 0)}, Parts={c_inventory.get('parts', 0)}"""
        
        # Format inventory with low-stock warnings
        inventory = obs.my_stats.get('inventory', {})
        inventory_section = ""
        for item, qty in inventory.items():
            warning = " ⚠️ LOW!" if qty < 20 else ""
            inventory_section += f"  - {item.capitalize()}: {qty}{warning}\n"
        
        # Format events
        events_section = "None active"
        if obs.events:
            events_section = "\n".join([f"  - {e}" for e in obs.events])

        # Format Alliances & Trust
        diplomacy_section = ""
        if obs.alliances:
            diplomacy_section += "\n🤝 ACTIVE ALLIANCES:\n" + "\n".join([f"  - {a}" for a in obs.alliances])
        
        if obs.trust_scores:
            diplomacy_section += "\n❤️ TRUST SCORES:\n" + "\n".join([f"  - {k}: {v:.1f}/100" for k, v in obs.trust_scores.items()])
        
        # Calculate market position
        my_price = obs.my_stats.get('price', 5.0)
        competitor_prices = [c.get('price', 5.0) for c in obs.competitor_stats]
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else 5.0
        price_position = "CHEAPEST" if competitor_prices and my_price < min(competitor_prices) else \
                         ("EXPENSIVE" if competitor_prices and my_price > max(competitor_prices) else "MIDDLE")
        
        # Helper to extract numeric social score
        def get_social_score(score):
            if isinstance(score, dict):
                return score.get('total_score', 50)
            return score if isinstance(score, (int, float)) else 50
        
        my_social = get_social_score(obs.my_stats.get('social_score', 50))
        competitor_socials = [get_social_score(c.get('social_score', 50)) for c in obs.competitor_stats]
        reputation_rank = sum(1 for s in competitor_socials if s > my_social) + 1
        
        # Format Market Data
        market_section = ""
        if obs.market_data:
            market_section = "\n🛒 MARKET VENDORS:\n"
            for vid, data in obs.market_data.items():
                prices = data.get('prices', {})
                market_section += f"  - {vid}: Soap=${prices.get('soap',0):.2f}, Softener=${prices.get('softener',0):.2f}\n"
        
        return f"""╔══════════════════════════════════════════════════════════════╗
║  LAUNDROMAT TYCOON - WEEK {obs.week} | {obs.day} | {obs.phase}
╚══════════════════════════════════════════════════════════════╝

📊 YOUR BUSINESS STATUS:
  Balance: ${obs.my_stats.get('balance', 0):.2f}
  Active Customers: {obs.my_stats.get('active_customers', 0)}
  Social Score: {my_social}/100 (Rank #{reputation_rank} of {len(obs.competitor_stats) + 1})
  Machines: {obs.my_stats.get('machines', 4)} (broken: {obs.my_stats.get('broken_machines', 0)})
  Current Price: ${my_price:.2f} ({price_position} vs competitors, avg: ${avg_competitor_price:.2f})

📦 INVENTORY:
{inventory_section if inventory_section else "  No inventory data"}
{market_section}
{tickets_section}
{messages_section}
👥 COMPETITOR ANALYSIS:
{competitors_section}

🌍 ACTIVE EVENTS:
  {events_section}

🕊️ DIPLOMACY:
{diplomacy_section if diplomacy_section else "  No active alliances or trust data"}

💳 CREDIT & FINANCIALS:
  Credit Score: {obs.credit_info.get('credit_score', 'N/A') if obs.credit_info else 'N/A'} (Rating: {obs.credit_info.get('rating', 'N/A') if obs.credit_info else 'N/A'})
  SBA Loan: {f"${obs.credit_info.get('sba_loan_amount', 0):.2f}" if obs.credit_info else 'N/A'}
  Active Loans: {len(obs.credit_info.get('active_loans', [])) if obs.credit_info else 0}
  Payments Due: {len(obs.credit_info.get('payments_due', [])) if obs.credit_info else 0}

🏙️ NEIGHBORHOOD ZONE:
  Zone: {obs.zone_info.get('zone_name', 'Unknown') if obs.zone_info else 'Unknown'}
  Tier: {obs.zone_info.get('zone_tier', 'Unknown') if obs.zone_info else 'Unknown'}
  Traffic: {obs.zone_info.get('base_foot_traffic', 0) if obs.zone_info else 0}/day (Modifier: {obs.zone_info.get('traffic_modifier', 1.0) if obs.zone_info else 1.0}x)
  Rent: ${obs.zone_info.get('rent_cost', 0) if obs.zone_info else 0}/week

📅 CALENDAR & SCHEDULE:
  Upcoming: {obs.calendar_info.get('upcoming_count', 0) if obs.calendar_info else 0} actions
  Overdue: {obs.calendar_info.get('overdue_count', 0) if obs.calendar_info else 0} actions
  Active Events: {', '.join([e['title'] for e in obs.calendar_info.get('today_events', [])]) if obs.calendar_info and obs.calendar_info.get('today_events') else 'None'}

⚖️ ETHICAL DILEMMA:
{f"  ⚠️ ACTION REQUIRED: {obs.ethical_dilemma.get('title')}\n  {obs.ethical_dilemma.get('description')}\n  Options: {', '.join(obs.ethical_dilemma.get('options', []))}" if obs.ethical_dilemma else "  No active dilemmas"}

💡 STRATEGIC CONSIDERATIONS:
  - Price competitiveness: You are {price_position} in the market
  - Customer preference trends toward {"quality" if my_social > 60 else "value" if my_price < avg_competitor_price else "balanced options"}
  - {"⚠️ Low inventory warning! Consider restocking" if any(qty < 20 for qty in inventory.values()) else "Inventory levels healthy"}
  - {"⚠️ Unresolved tickets may hurt reputation!" if tickets_section else "No pending tickets"}

Analyze the situation and use the tools to take your actions for this turn."""

    def _heuristic_action(self, obs: Observation) -> Action:
        """Fallback heuristic when LLM unavailable"""
        import random
        
        balance = obs.my_stats.get('balance', 0)
        inventory = obs.my_stats.get('inventory', {})
        
        # Low inventory? Buy supplies
        if inventory.get('soap', 0) < 20 and balance > 50:
            self.last_thinking = ["Low on soap, need to restock"]
            action = Action(type=ActionType.BUY_SUPPLIES, parameters={"item": "soap", "quantity": 30})
            self.last_actions = [action]
            return action
        
        # Good balance? Maybe marketing
        if balance > 300 and random.random() < 0.3:
            self.last_thinking = ["Have surplus funds, investing in marketing"]
            action = Action(type=ActionType.MARKETING_CAMPAIGN, parameters={"cost": 100})
            self.last_actions = [action]
            return action
        
        # Random price adjustment
        if random.random() < 0.2:
            new_price = round(random.uniform(4.0, 7.0), 2)
            self.last_thinking = [f"Adjusting price to ${new_price} to stay competitive"]
            action = Action(type=ActionType.SET_PRICE, parameters={"price": new_price})
            self.last_actions = [action]
            return action
        
        # Default: wait
        self.last_thinking = ["Market conditions stable, waiting"]
        action = Action(type=ActionType.WAIT)
        self.last_actions = [action]
        return action
