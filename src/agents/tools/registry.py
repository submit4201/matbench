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
            }
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
