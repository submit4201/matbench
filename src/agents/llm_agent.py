"""
LLM Agent for Laundromat Simulation

Uses OpenAI function calling for reliable structured action output.
Supports multiple AI providers via helper packages.
"""

import json
import os
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent, Observation, Action, ActionType
from src.config import LLMDICT
from dotenv import load_dotenv

# Import all AI model helpers
from src.agents.opsus_helper import get_claude_client, AzureClaudeClient
from src.agents.meta_helper import get_meta_client, AzureMetaClient
from src.agents.mistral_helper import get_mistral_client, AzureMistralClient
from src.agents.phi_helper import get_phi_client, AzurePhiClient
from src.agents.azure_helper import get_azure_client, AzureOpenAIClient
from src.agents.gemini_helper import get_gemini_client, GeminiClient

# Load environment variables
load_dotenv()
# Tool definitions for all action types
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_price",
            "description": "Set the laundromat wash price per load. Use this to adjust pricing strategy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "number",
                        "description": "Price per wash in dollars (e.g., 4.50)"
                    }
                },
                "required": ["price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buy_supplies",
            "description": "Purchase inventory supplies from vendors. Buy soap, softener, parts, and/or cleaning supplies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "soap": {
                        "type": "integer",
                        "description": "Quantity of soap to purchase"
                    },
                    "softener": {
                        "type": "integer",
                        "description": "Quantity of softener to purchase"
                    },
                    "parts": {
                        "type": "integer",
                        "description": "Quantity of machine parts to purchase"
                    },
                    "cleaning_supplies": {
                        "type": "integer",
                        "description": "Quantity of cleaning supplies to purchase"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "marketing_campaign",
            "description": "Launch a marketing campaign to attract more customers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cost": {
                        "type": "number",
                        "description": "Budget for the marketing campaign in dollars"
                    }
                },
                "required": ["cost"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "upgrade_machine",
            "description": "Purchase and add a new washing machine to increase capacity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Number of machines to add (default 1)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "resolve_ticket",
            "description": "Resolve a customer complaint ticket to improve satisfaction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "ID of the ticket to resolve"
                    }
                },
                "required": ["ticket_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send a message to another player, vendor, or customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_id": {
                        "type": "string",
                        "description": "ID of the message recipient"
                    },
                    "content": {
                        "type": "string",
                        "description": "Message content"
                    }
                },
                "required": ["recipient_id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "propose_alliance",
            "description": "Propose a business alliance with another laundromat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "ID of the laundromat to propose alliance with"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Duration of alliance in weeks"
                    }
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "initiate_buyout",
            "description": "Make an offer to buy out a competitor's laundromat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "ID of the laundromat to buy out"
                    },
                    "offer": {
                        "type": "number",
                        "description": "Offer amount in dollars"
                    }
                },
                "required": ["target", "offer"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "negotiate",
            "description": "Negotiate with a vendor for better prices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "Item to negotiate (soap, softener, parts)"
                    },
                    "vendor_id": {
                        "type": "string",
                        "description": "Vendor ID to negotiate with"
                    }
                },
                "required": ["item"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Skip this turn without taking action. Use when market conditions are stable.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

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
}


class LLMAgent(BaseAgent):
    """AI Agent that uses LLMs with function calling for structured output"""
    
    def __init__(self, agent_id: str, name: str, model: str = "gpt-4", llm_provider: str = "AZURE"):
        super().__init__(agent_id, name)
        self.model = model
        self.llm_provider = llm_provider
        self.history = []  # Conversation history
        
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
        
        # Setup LLM client using helper packages
        print(f"[{self.name}] Starting LLM initialization...")
        self._setup_llm(llm_provider)

    def _setup_llm(self, llm_name: str):
        """Initialize LLM client based on provider"""
        try:
            if llm_name not in LLMDICT:
                print(f"[{self.name}] ✗ Provider '{llm_name}' not found in LLMDICT - LLM will be disabled")
                self.llm = None
                return
            
            print(f"[{self.name}] Initializing {llm_name} provider...")
            
            # Initialize client based on provider
            if llm_name == "OPSUS":
                self.llm = get_claude_client()
                print(f"[{self.name}] ✓ Claude (Opus) client initialized")
            
            elif llm_name == "META":
                self.llm = get_meta_client()
                print(f"[{self.name}] ✓ Meta (Llama) client initialized")
            
            elif llm_name == "MISTRAL":
                self.llm = get_mistral_client()
                print(f"[{self.name}] ✓ Mistral client initialized")
            
            elif llm_name == "PHI":
                self.llm = get_phi_client()
                print(f"[{self.name}] ✓ Phi client initialized")
            
            elif llm_name == "GEMINI":
                self.llm = get_gemini_client()
                print(f"[{self.name}] ✓ Gemini client initialized")
            
            elif llm_name in ["AZURE", "OPENAI"]:
                print(f"[{self.name}] Calling get_azure_client()...")
                self.llm = get_azure_client()
                print(f"[{self.name}] ✓ Azure OpenAI client initialized")
                print(f"[{self.name}]   Deployment: {self.llm.deployment_name}")
            
            else:
                # Fallback to generic Azure OpenAI for unknown providers
                print(f"[{self.name}] ⚠ Unknown provider '{llm_name}', using Azure OpenAI fallback")
                self.llm = get_azure_client()
                
        except Exception as e:
            print(f"[{self.name}] ✗ LLM setup FAILED with exception: {e}")
            print(f"[{self.name}]   Provider was: {llm_name}")
            import traceback
            traceback.print_exc()
            self.llm = None

    def decide_action(self, observation: Observation) -> Action:
        """
        Decide next action based on observation using function calling.
        Returns the first action; call get_all_actions() for multi-action turns.
        """
        prompt = self._build_prompt(observation)
        
        # Reset last turn data
        self.last_thinking = []
        self.last_actions = []
        self.last_raw_response = ""
        self.last_parse_errors = []
        
        # Try to call LLM
        if self.llm:
            try:
                response = self._call_llm(prompt)
                
                # Debug: Log raw response structure
                print(f"[{self.name}] Raw response type: {type(response)}")
                print(f"[{self.name}] Response has choices: {hasattr(response, 'choices')}")
                if hasattr(response, 'choices') and response.choices:
                    print(f"[{self.name}] Number of choices: {len(response.choices)}")
                    message = response.choices[0].message
                    print(f"[{self.name}] Message type: {type(message)}")
                    print(f"[{self.name}] Message attributes: {dir(message)}")
                    if hasattr(message, 'tool_calls'):
                        print(f"[{self.name}] tool_calls attribute exists: {message.tool_calls}")
                
                # Extract thinking from message content
                message = response.choices[0].message
                if message.content:
                    self.last_thinking = [message.content]
                    self.last_raw_response = message.content
                
                # Parse tool calls into actions
                self.last_actions = self._parse_tool_calls(message)
                
                if self.last_actions:
                    final_action = self.last_actions[0]
                    self.log_strategy(observation.week, self.last_thinking, final_action)
                    return final_action
                    
            except Exception as e:
                print(f"[{self.name}] LLM call failed: {e}")
                import traceback
                traceback.print_exc()
                self.last_parse_errors.append(str(e))
        
        # Fallback to heuristic if LLM fails
        print(f"[{self.name}] Using heuristic fallback")
        action = self._heuristic_action(observation)
        self.log_strategy(observation.week, ["Heuristic fallback triggered"], action)
        return action
    
    def log_strategy(self, week: int, thinking: List[str], decision: Action):
        """Logs the agent's strategy to a markdown file."""
        log_dir = "logs/strategy"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        filename = f"{log_dir}/{self.id}_week_{week}.md"
        
        thinking_str = "\n".join([f"- {t}" for t in thinking])
        
        # Simple tag generation
        tags = []
        decision_str = str(decision)
        if "SET_PRICE" in decision_str: tags.append("#pricing")
        if "BUY_SUPPLIES" in decision_str: tags.append("#logistics")
        if "MARKETING" in decision_str: tags.append("#marketing")
        if "WAIT" in decision_str: tags.append("#passive")
        
        content = f"""# Strategy Log - Week {week}
**Agent**: {self.name} ({self.id})
**Mode**: Function Calling

**Reasoning**:
{thinking_str}

**Decision**: {decision}

**Tags**: {" ".join(tags)}
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def get_all_actions(self) -> List[Action]:
        """Get all actions from the last decide_action call (for multi-action turns)"""
        return self.last_actions if self.last_actions else [Action(ActionType.WAIT)]
    
    def get_last_thinking(self) -> List[str]:
        """Get thinking from the last decide_action call"""
        return self.last_thinking

    def _call_llm(self, prompt: str):
        """Call the LLM with function calling and return raw response"""
        
        # Get model name from the client
        if hasattr(self.llm, 'deployment_name'):
            model_name = self.llm.deployment_name
        elif hasattr(self.llm, 'model'):
            model_name = self.llm.model
        else:
            model_name = self.model  # Fallback to default
        
        # O-series models (o1, o3) don't support temperature or tools
        is_o_series = model_name and (
            model_name.startswith('o1') or model_name.startswith('o3')
        )
        
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        request_params = {
            "model": model_name,
            "messages": messages,
            "max_completion_tokens": 1500
        }
        
        # Only add tools and temperature for non-O-series models
        if not is_o_series:
            request_params["temperature"] = 0.7
            request_params["tools"] = TOOLS
            # Don't set tool_choice - many Azure models don't support it
        
        print(f"[{self.name}] Calling LLM with model: {model_name}")
        print(f"[{self.name}] Tools included: {not is_o_series}")
        print(f"[{self.name}] Number of tools: {len(TOOLS) if not is_o_series else 0}")
        
        try:
            response = self.llm.chat.completions.create(**request_params)
            print(f"[{self.name}] LLM call successful")
            return response
        except Exception as e:
            print(f"[{self.name}] LLM call failed: {e}")
            # Retry without tools/temperature if that was the issue
            if any(kw in str(e).lower() for kw in ["temperature", "tools"]):
                print(f"[{self.name}] Retrying without tools/temperature...")
                request_params.pop("temperature", None)
                request_params.pop("tools", None)
                request_params.pop("tool_choice", None)
                response = self.llm.chat.completions.create(**request_params)
                print(f"[{self.name}] Retry successful (without tools)")
                return response
            raise

    def _get_system_prompt(self) -> str:
        """System prompt for LLM - focused on strategic reasoning"""
        return """You are an AI competitor in Laundromat Tycoon, a strategic business simulation.

IMPORTANT: Before taking any action, ALWAYS explain your strategic reasoning in your message. Analyze:
1. Your current financial health and trends
2. Competitor prices and strategies  
3. Inventory levels and upcoming needs
4. Customer satisfaction and complaints
5. Why you're choosing specific actions

Use the provided tools to take actions each turn. You can call multiple tools to:
- Set prices to stay competitive
- Buy supplies before running out
- Launch marketing campaigns
- Resolve customer tickets
- Negotiate with vendors
- And more

If conditions are stable and no action is needed, call the wait() function.

Think strategically - your goal is to build the most successful laundromat!"""

    def _parse_tool_calls(self, message) -> List[Action]:
        """Parse tool calls from LLM response into Action objects"""
        actions = []
        
        print(f"[{self.name}] Parsing tool calls from message...")
        print(f"[{self.name}] Message has tool_calls attribute: {hasattr(message, 'tool_calls')}")
        
        if hasattr(message, 'tool_calls'):
            print(f"[{self.name}] tool_calls value: {message.tool_calls}")
            print(f"[{self.name}] tool_calls type: {type(message.tool_calls)}")
            if message.tool_calls:
                print(f"[{self.name}] tool_calls length: {len(message.tool_calls)}")
        
        if not message.tool_calls:
            # No tool calls - default to WAIT
            print(f"[{self.name}] No tool calls found (empty or None), defaulting to WAIT")
            actions.append(Action(ActionType.WAIT))
            return actions
        
        print(f"[{self.name}] Found {len(message.tool_calls)} tool calls")
        
        for idx, tool_call in enumerate(message.tool_calls):
            func_name = tool_call.function.name
            print(f"[{self.name}] Tool call {idx}: {func_name}")
            
            try:
                args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
                print(f"[{self.name}]   Arguments: {args}")
            except json.JSONDecodeError:
                args = {}
                self.last_parse_errors.append(f"Failed to parse args for {func_name}")
                print(f"[{self.name}]   Failed to parse arguments!")
            
            action_type = FUNCTION_TO_ACTION.get(func_name)
            if not action_type:
                self.last_parse_errors.append(f"Unknown function: {func_name}")
                print(f"[{self.name}]   Unknown function: {func_name}")
                continue
            
            # Map function args to action parameters
            params = self._map_function_args(func_name, args)
            actions.append(Action(action_type, params))
            
            print(f"[{self.name}] Action: {action_type.value} with {params}")
        
        return actions if actions else [Action(ActionType.WAIT)]

    def _map_function_args(self, func_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Map function call arguments to Action parameters"""
        print(f"[{self.name}] Mapping function '{func_name}' with args: {args}")
        
        if func_name == "set_price":
            return {"price": args.get("price", 5.0)}
        
        elif func_name == "buy_supplies":
            # Map various item names to inventory keys
            item_aliases = {
                "soap": "detergent",
                "detergent": "detergent",
                "softener": "softener",
                "parts": "parts",
                "machine_parts": "parts",
                "cleaning_supplies": "cleaning_supplies"
            }
            
            # Find first valid item in args
            params = {}
            for arg_key, arg_value in args.items():
                if arg_value and arg_value > 0:
                    # Map to inventory key
                    inventory_key = item_aliases.get(arg_key.lower())
                    if inventory_key:
                        params["item"] = inventory_key
                        params["quantity"] = arg_value
                        print(f"[{self.name}] Mapped {arg_key}={arg_value} to item={inventory_key}, quantity={arg_value}")
                        break
            
            if not params:
                # Check for standard keys
                for item in ["soap", "detergent", "softener", "parts"]:
                    if item in args and args[item] and args[item] > 0:
                        params["item"] = item_aliases.get(item, item)
                        params["quantity"] = args[item]
                        print(f"[{self.name}] Using {item}={args[item]}")
                        break
            
            if not params:
                params = {"item": "detergent", "quantity": 10}  # Default
                print(f"[{self.name}] No valid items found, using default: {params}")
            
            return params
        
        elif func_name == "marketing_campaign":
            return {"cost": args.get("cost", 100)}
        
        elif func_name == "upgrade_machine":
            return {"count": args.get("count", 1)}
        
        elif func_name == "resolve_ticket":
            return {"ticket_id": args.get("ticket_id", "")}
        
        elif func_name == "send_message":
            return {
                "recipient_id": args.get("recipient_id", ""),
                "content": args.get("content", "")
            }
        
        elif func_name == "propose_alliance":
            return {
                "target": args.get("target", ""),
                "duration": args.get("duration", 4)
            }
        
        elif func_name == "initiate_buyout":
            return {
                "target": args.get("target", ""),
                "offer": args.get("offer", 0)
            }
        
        elif func_name == "negotiate":
            return {
                "item": args.get("item", "soap"),
                "vendor_id": args.get("vendor_id", "bulkwash")
            }
        
        else:  # wait or unknown
            print(f"[{self.name}] Unknown function or wait: {func_name}")
            return {}

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
║  LAUNDROMAT TYCOON - WEEK {obs.week} ({obs.season})
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
            action = Action(ActionType.BUY_SUPPLIES, {"item": "soap", "quantity": 30})
            self.last_actions = [action]
            return action
        
        # Good balance? Maybe marketing
        if balance > 300 and random.random() < 0.3:
            self.last_thinking = ["Have surplus funds, investing in marketing"]
            action = Action(ActionType.MARKETING_CAMPAIGN, {"cost": 100})
            self.last_actions = [action]
            return action
        
        # Random price adjustment
        if random.random() < 0.2:
            new_price = round(random.uniform(4.0, 7.0), 2)
            self.last_thinking = [f"Adjusting price to ${new_price} to stay competitive"]
            action = Action(ActionType.SET_PRICE, {"price": new_price})
            self.last_actions = [action]
            return action
        
        # Default: wait
        self.last_thinking = ["Market conditions stable, waiting"]
        action = Action(ActionType.WAIT)
        self.last_actions = [action]
        return action
