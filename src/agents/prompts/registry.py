import os
from pathlib import Path

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
                
            return content
            
        except Exception as e:
            return f"Error loading prompt: {str(e)}"

    @classmethod
    def get_turn_prompt(cls, state_summary: str, memory_context: str = "None") -> str:
        """
        Constructs the dynamic Turn Prompt.
        """
        return f"""
# Current Status
{state_summary}

# Memory Context
Previous Thought: "{memory_context}"

# Your Task
1. Review the status and your memory.
2. THINK about your move.
3. Use TOOLS to act or gather data.
4. Call `end_turn(memory_note=...)` ONLY when done.
"""
