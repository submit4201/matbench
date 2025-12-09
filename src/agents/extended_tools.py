# [ ]↔T: Extended tools for LLM agents
#   - [x] Credit System tools (make_payment, apply_for_loan)
#   - [x] Calendar tools (schedule_action)
#   - [x] Enhanced Communication tools (send_dm, send_public, send_formal)
#   - [x] Ethical Dilemma tools (resolve_dilemma)
# PRIORITY: P1 - Agent capability extensions
# STATUS: Complete

"""
Extended LLM Tools

New function-calling tools for enhanced game systems:
- Credit/FICO System
- Calendar/Scheduling
- Enhanced Communication
- Ethical Dilemmas

Import and extend TOOLS in llm_agent.py:
    from src.agents.extended_tools import EXTENDED_TOOLS, EXTENDED_FUNCTION_TO_ACTION
    TOOLS.extend(EXTENDED_TOOLS)
    FUNCTION_TO_ACTION.update(EXTENDED_FUNCTION_TO_ACTION)
"""

from src.agents.base_agent import ActionType

# ═══════════════════════════════════════════════════════════════════════════
# EXTENDED TOOL DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

EXTENDED_TOOLS = [
    # ─────────────────────────────────────────────────────────────────────────
    # CREDIT SYSTEM TOOLS
    # ─────────────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "make_payment",
            "description": "Make a loan payment. Payments are due weekly. On-time payments improve credit score; missed payments hurt it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "payment_id": {
                        "type": "string",
                        "description": "ID of the payment to make (from calendar reminders)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount to pay in dollars"
                    }
                },
                "required": ["payment_id", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "apply_for_loan",
            "description": "Apply for a new loan. Approval and interest rate depend on your credit score (300-850).",
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_type": {
                        "type": "string",
                        "enum": ["equipment_loan", "operating_credit", "expansion_loan"],
                        "description": "Type of loan to apply for"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Amount to borrow in dollars"
                    }
                },
                "required": ["loan_type", "amount"]
            }
        }
    },
    
    # ─────────────────────────────────────────────────────────────────────────
    # CALENDAR TOOLS
    # ─────────────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "schedule_action",
            "description": "Schedule an action for a future day/week. Use for strategic planning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["payment", "supply_order", "maintenance", "marketing", "negotiation", "custom"],
                        "description": "Category of scheduled action"
                    },
                    "title": {
                        "type": "string",
                        "description": "Short title for the scheduled item"
                    },
                    "week": {
                        "type": "integer",
                        "description": "Week number to schedule for"
                    },
                    "day": {
                        "type": "integer",
                        "description": "Day of week (1=Mon, 7=Sun)"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Priority level"
                    },
                    "is_recurring": {
                        "type": "boolean",
                        "description": "Whether this repeats weekly"
                    }
                },
                "required": ["category", "title", "week"]
            }
        }
    },
    
    # ─────────────────────────────────────────────────────────────────────────
    # ENHANCED COMMUNICATION TOOLS
    # ─────────────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "send_dm",
            "description": "Send a private direct message to another player. Only you and the recipient can see this.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_id": {
                        "type": "string",
                        "description": "ID of the player to message"
                    },
                    "content": {
                        "type": "string",
                        "description": "Message content"
                    },
                    "intent": {
                        "type": "string",
                        "enum": ["chat", "proposal", "threat", "question", "info"],
                        "description": "Intent of the message"
                    }
                },
                "required": ["recipient_id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_public",
            "description": "Make a public announcement visible to all players. Good for marketing or reputation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Message content (all players will see this)"
                    },
                    "intent": {
                        "type": "string",
                        "enum": ["announcement", "promotion", "info"],
                        "description": "Type of public message"
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_formal",
            "description": "Send a formal message that gets logged for regulatory review. Use for contracts and official proposals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_id": {
                        "type": "string",
                        "description": "ID of the player to send formal message to"
                    },
                    "content": {
                        "type": "string",
                        "description": "Formal message content (will be logged)"
                    },
                    "intent": {
                        "type": "string",
                        "enum": ["proposal", "contract", "acceptance", "rejection", "counter_offer"],
                        "description": "Type of formal communication"
                    }
                },
                "required": ["recipient_id", "content", "intent"]
            }
        }
    },
    
    # ─────────────────────────────────────────────────────────────────────────
    # ETHICAL DILEMMA TOOLS
    # ─────────────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "resolve_dilemma",
            "description": "Resolve an ethical dilemma by choosing an option. Your choice will be evaluated for ethics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dilemma_id": {
                        "type": "string",
                        "description": "ID of the ethical dilemma to resolve"
                    },
                    "choice_id": {
                        "type": "string",
                        "description": "ID of the option you choose"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Explain your reasoning for this choice"
                    }
                },
                "required": ["dilemma_id", "choice_id"]
            }
        }
    }
]

# ═══════════════════════════════════════════════════════════════════════════
# FUNCTION NAME TO ACTION TYPE MAPPING
# ═══════════════════════════════════════════════════════════════════════════

EXTENDED_FUNCTION_TO_ACTION = {
    "make_payment": ActionType.MAKE_PAYMENT,
    "apply_for_loan": ActionType.APPLY_FOR_LOAN,
    "schedule_action": ActionType.SCHEDULE_ACTION,
    "send_dm": ActionType.SEND_DM,
    "send_public": ActionType.SEND_PUBLIC,
    "send_formal": ActionType.SEND_FORMAL,
    "resolve_dilemma": ActionType.RESOLVE_DILEMMA,
}


def map_extended_function_args(func_name: str, args: dict) -> dict:
    """Map extended function call arguments to Action parameters."""
    
    if func_name == "make_payment":
        return {
            "payment_id": args.get("payment_id", ""),
            "amount": args.get("amount", 0)
        }
    
    elif func_name == "apply_for_loan":
        return {
            "loan_type": args.get("loan_type", "equipment_loan"),
            "amount": args.get("amount", 1000)
        }
    
    elif func_name == "schedule_action":
        return {
            "category": args.get("category", "custom"),
            "title": args.get("title", "Scheduled Task"),
            "week": args.get("week", 1),
            "day": args.get("day", 1),
            "priority": args.get("priority", "medium"),
            "is_recurring": args.get("is_recurring", False)
        }
    
    elif func_name == "send_dm":
        return {
            "recipient_id": args.get("recipient_id", ""),
            "content": args.get("content", ""),
            "intent": args.get("intent", "chat")
        }
    
    elif func_name == "send_public":
        return {
            "content": args.get("content", ""),
            "intent": args.get("intent", "announcement")
        }
    
    elif func_name == "send_formal":
        return {
            "recipient_id": args.get("recipient_id", ""),
            "content": args.get("content", ""),
            "intent": args.get("intent", "proposal")
        }
    
    elif func_name == "resolve_dilemma":
        return {
            "dilemma_id": args.get("dilemma_id", ""),
            "choice_id": args.get("choice_id", ""),
            "reasoning": args.get("reasoning", "")
        }
    
    return {}
