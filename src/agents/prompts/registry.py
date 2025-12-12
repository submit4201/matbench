import os
from pathlib import Path
from src.agents.tools.registry import ToolRegistry

class PromptRegistry:
    """
    Manages prompt templates for agents.
    Loads from `src/agents/prompts/` directory.
    """
    
    PROMPT_DIR = Path(__file__).parent.parent / "prompts"
    
    @classmethod
    def get_system_prompt(cls, template_name: str = "evolving_system_draft.md", **kwargs) -> str:
        """
        Loads a system prompt template and formats it with kwargs.
        Default is the 'evolving' template.
        """
        try:
            template_path = cls.PROMPT_DIR / template_name
            if not template_path.exists():
                return f"Error: Template {template_name} not found."
                
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Basic Jinja2-style replacement (Double curly braces)
            for key, value in kwargs.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
                
            # Add tools
            tools = ToolRegistry.get_all_tools()
            tools_str = "\n".join([f"- {tool['function']['name']}" for tool in tools])
            content = content.replace("{{tools}}", tools_str)
            
            return content
            
        except Exception as e:
            return f"Error loading prompt: {str(e)}"

    @classmethod
    def get_turn_prompt(cls ,template_name: str = "turn_prompt_template.md", **kwargs) -> str:

        """
        Constructs the dynamic Turn Prompt.
        """
        try:
            template_path = cls.PROMPT_DIR / template_name
            if not template_path.exists():
                return f"Error: Template {template_name} not found."
                
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Basic Jinja2-style replacement (Double curly braces)
            for key, value in kwargs.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
            return content
            
        except Exception as e:
            return f"Error loading prompt: {str(e)}"
