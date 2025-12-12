from typing import List, Dict, Any, Optional

class ToolRegistry:
    """
    Central registry for all LLM tools.
    Decouples tool definitions from the agent logic.
    """
    
    _registry = {}
    
    @classmethod
    def register_tool(cls, name: str, definition: Dict[str, Any]):
        cls._registry[name] = definition
        
    @classmethod
    def get_all_tools(cls) -> List[Dict[str, Any]]:
        return list(cls._registry.values())
        
    @classmethod
    def get_tool(cls, name: str) -> Optional[Dict[str, Any]]:
        return cls._registry.get(name)

# --- Standard Tools Definitions ---

# Pricing
ToolRegistry.register_tool("set_price", {
    "type": "function",
    "function": {
        "name": "set_price",
        "description": "Set the laundromat wash price per load. Use this to adjust pricing strategy.",
        "parameters": {
            "type": "object",
            "properties": {
                "price": {"type": "number", "description": "Price per wash in dollars (e.g., 4.50)"}
            },
            "required": ["price"]
        }
    }
})

# Inventory
ToolRegistry.register_tool("buy_supplies", {
    "type": "function",
    "function": {
        "name": "buy_supplies",
        "description": "Purchase inventory supplies from vendors. Buy soap, softener, parts, and/or cleaning supplies.",
        "parameters": {
            "type": "object",
            "properties": {
                "soap": {"type": "integer", "description": "Quantity of soap to purchase"},
                "softener": {"type": "integer", "description": "Quantity of softener to purchase"},
                "parts": {"type": "integer", "description": "Quantity of machine parts to purchase"},
                "cleaning_supplies": {"type": "integer", "description": "Quantity of cleaning supplies to purchase"}
            },
            "required": []
        }
    }
})

# Marketing
ToolRegistry.register_tool("marketing_campaign", {
    "type": "function",
    "function": {
        "name": "marketing_campaign",
        "description": "Launch a marketing campaign to attract more customers.",
        "parameters": {
            "type": "object",
            "properties": {
                "cost": {"type": "number", "description": "Budget for the marketing campaign in dollars"}
            },
            "required": ["cost"]
        }
    }
})

# Upgrades
ToolRegistry.register_tool("upgrade_machine", {
    "type": "function",
    "function": {
        "name": "upgrade_machine",
        "description": "Purchase and add a new washing machine to increase capacity.",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_type": {"type": "string", "enum": ["standard", "premium"], "description": "Type of machine to purchase"}
            },
            "required": ["machine_type"]
        }
    }
})

# End Turn (Signal)
ToolRegistry.register_tool("end_turn", {
    "type": "function",
    "function": {
        "name": "end_turn",
        "description": "Signal that you are done with your turn. Optionally save a memory note.",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_note": {
                    "type": "string", 
                    "description": "A private note to your future self about your strategy, why you did what you did, and what to watch for next week."
                }
            },
            "required": ["memory_note"]
        }
    }
})

# --- Extended Tools (Financial & Calendar) ---

ToolRegistry.register_tool("make_payment", {
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
})

ToolRegistry.register_tool("apply_for_loan", {
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
})

ToolRegistry.register_tool("schedule_action", {
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
})

# --- Communication Tools ---

ToolRegistry.register_tool("send_dm", {
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
})

ToolRegistry.register_tool("send_public", {
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
})

ToolRegistry.register_tool("send_formal", {
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
})

# --- Ethics Tools ---

# ToolRegistry.register_tool("resolve_dilemma", {
#     "type": "function",
#     "function": {
#         "name": "resolve_dilemma",
#         "description": "Resolve an ethical dilemma by choosing an option. Your choice will be evaluated for ethics.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "dilemma_id": {
#                     "type": "string",
#                     "description": "ID of the ethical dilemma to resolve"
#                 },
#                 "choice_id": {
#                     "type": "string",
#                     "description": "ID of the option you choose"
#                 },
#                 "reasoning": {
#                     "type": "string",
#                     "description": "Explain your reasoning for this choice"
#                 }
#             },
#             "required": ["dilemma_id", "choice_id"]
#         }
#     }
# })

# --- Staff Management ---

ToolRegistry.register_tool("hire_staff", {
    "type": "function",
    "function": {
        "name": "hire_staff",
        "description": "Hire a new staff member. Staff improve cleanliness and efficiency but cost wages.",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "Role to hire: 'attendant', 'technician', 'cleaner'"
                }
            },
            "required": ["role"]
        }
    }
})

ToolRegistry.register_tool("fire_staff", {
    "type": "function",
    "function": {
        "name": "fire_staff",
        "description": "Fire a staff member to save on wages.",
        "parameters": {
            "type": "object",
            "properties": {
                "staff_id": {
                    "type": "string",
                    "description": "ID of the staff member to fire"
                }
            },
            "required": ["staff_id"]
        }
    }
})

ToolRegistry.register_tool("train_staff", {
    "type": "function",
    "function": {
        "name": "train_staff",
        "description": "Train a staff member to improve their skill level.",
        "parameters": {
            "type": "object",
            "properties": {
                "staff_id": {
                    "type": "string",
                    "description": "ID of the staff member to train"
                }
            },
            "required": ["staff_id"]
        }
    }
})

# --- Maintenance ---

ToolRegistry.register_tool("perform_maintenance", {
    "type": "function",
    "function": {
        "name": "perform_maintenance",
        "description": "Perform preventative maintenance on ALL machines to reduce breakdown chance. Consumes 'parts' from inventory.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

# --- Advanced Vendor ---

ToolRegistry.register_tool("inspect_vendor", {
    "type": "function",
    "function": {
        "name": "inspect_vendor",
        "description": "Inspect a specific vendor to see their product catalog and prices.",
        "parameters": {
            "type": "object",
            "properties": {
                "vendor_id": {
                    "type": "string",
                    "description": "ID of the vendor (e.g., 'bulkwash')"
                }
            },
            "required": ["vendor_id"]
        }
    }
})

ToolRegistry.register_tool("negotiate_contract", {
    "type": "function",
    "function": {
        "name": "negotiate_contract",
        "description": "Attempt to negotiate better prices with a vendor based on your reputation.",
        "parameters": {
            "type": "object",
            "properties": {
                "vendor_id": {
                    "type": "string",
                    "description": "ID of the vendor"
                },
                "item": {
                    "type": "string",
                    "description": "Item to negotiate (e.g. 'soap')"
                }
            },
            "required": ["vendor_id", "item"]
        }
    }
})

ToolRegistry.register_tool("inspect_deliveries", {
    "type": "function",
    "function": {
        "name": "inspect_deliveries",
        "description": "View list of pending deliveries and their status.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

# --- Advanced Financial ---

ToolRegistry.register_tool("check_credit_score", {
    "type": "function",
    "function": {
        "name": "check_credit_score",
        "description": "View detailed credit report including score, rating, and influencing factors.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

ToolRegistry.register_tool("get_financial_report", {
    "type": "function",
    "function": {
        "name": "get_financial_report",
        "description": "Get a detailed breakdown of income, expenses, and cash flow for the current week.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

# --- Meta Tools ---

ToolRegistry.register_tool("get_tool_help", {
    "type": "function",
    "function": {
        "name": "get_tool_help",
        "description": "Get detailed documentation for a specific tool. or with out a tool name it will return a list of all tools.",
        "parameters": {
            "type": "object",
            "properties": {
                "tool_name": {
                    "type": "string",
                    "description": "Name of the tool to get help for"
                }
            },
            "required": ["tool_name"]
        }
    }
})

# --- Active Perception & Information Gathering (NEW) ---

ToolRegistry.register_tool("inspect_competitor", {
    "type": "function",
    "function": {
        "name": "inspect_competitor",
        "description": "View detailed public stats of a specific rival laundromat (price, reputation, visible upgrades).",
        "parameters": {
            "type": "object",
            "properties": {
                "competitor_id": {
                    "type": "string",
                    "description": "ID of the competitor to inspect"
                }
            },
            "required": ["competitor_id"]
        }
    }
})

ToolRegistry.register_tool("check_market_trends", {
    "type": "function",
    "function": {
        "name": "check_market_trends",
        "description": "Get a report on global resource prices and demand shifts in the market.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

ToolRegistry.register_tool("read_news", {
    "type": "function",
    "function": {
        "name": "read_news",
        "description": "Retrieve active world events and narratives affecting the market.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

ToolRegistry.register_tool("inspect_facility", {
    "type": "function",
    "function": {
        "name": "inspect_facility",
        "description": "View detailed status of your own facility, including machine health and cleanliness.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

# --- Final Gaps (Regulatory & Emergency) ---

ToolRegistry.register_tool("emergency_repair", {
    "type": "function",
    "function": {
        "name": "emergency_repair",
        "description": "Immediately repair a broken machine. Costs significantly more than preventative maintenance but resolves breakdowns instantly.",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_id": {
                    "type": "string",
                    "description": "ID of the broken machine to fix"
                }
            },
            "required": ["machine_id"]
        }
    }
})

ToolRegistry.register_tool("check_regulatory_requirements", {
    "type": "function",
    "function": {
        "name": "check_regulatory_requirements",
        "description": "Check current active regulations, pending fines, and compliance status.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

ToolRegistry.register_tool("check_reputation_score", {
    "type": "function",
    "function": {
        "name": "check_reputation_score",
        "description": "View a detailed breakdown of your reputation score key drivers (Community, Eco, Service, etc.).",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
})

ToolRegistry.register_tool("inspect_public_records", {
    "type": "function",
    "function": {
        "name": "inspect_public_records",
        "description": "View public history and relations of other agents or entities.",
        "parameters": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "ID of the entity (agent/competitor) to inspect records for. Unknown ID returns global records."
                }
            },
            "required": []
        }
    }
})
