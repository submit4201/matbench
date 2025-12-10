"""
LLM Provider Factory

Centralizes the creation of LLM clients (Azure, Claude, Meta, etc.).
"""

from typing import Optional, Any
from src.config import LLMDICT

# Import all AI model helpers
# NOTE: Using lazy imports or standard imports. Assuming helper files are in src.agents
# We use relative imports since we are in src.agents.providers
from src.agents.opsus_helper import get_claude_client
from src.agents.meta_helper import get_meta_client
from src.agents.mistral_helper import get_mistral_client
from src.agents.phi_helper import get_phi_client
from src.agents.azure_helper import get_azure_client
from src.agents.gemini_helper import get_gemini_client

class LLMProviderFactory:
    """
    Factory class for creating LLM clients based on provider names.
    """

    @staticmethod
    def create(provider_name: str, agent_name: str = "Agent") -> Optional[Any]:
        """
        Create and return an initialized LLM client.
        
        Args:
            provider_name: The key name of the provider (e.g., "AZURE", "OPSUS").
            agent_name: Name of the agent for logging purposes.
            
        Returns:
            Initialized client object or None if failed/unknown.
        """
        if provider_name not in LLMDICT:
            print(f"[{agent_name}] ✗ Provider '{provider_name}' not found in LLMDICT - LLM will be disabled")
            return None

        print(f"[{agent_name}] Initializing {provider_name} provider...")

        try:
            if provider_name == "OPSUS":
                client = get_claude_client()
                print(f"[{agent_name}] ✓ Claude (Opus) client initialized")
                return client

            elif provider_name == "META":
                client = get_meta_client()
                print(f"[{agent_name}] ✓ Meta (Llama) client initialized")
                return client

            elif provider_name == "MISTRAL":
                client = get_mistral_client()
                print(f"[{agent_name}] ✓ Mistral client initialized")
                return client

            elif provider_name == "PHI":
                client = get_phi_client()
                print(f"[{agent_name}] ✓ Phi client initialized")
                return client
            
            elif provider_name == "GEMINI":
                gemini_config = LLMDICT.get("GEMINI", {})
                model = gemini_config.get("MODEL", "gemini-flash-lite-latest")
                client = get_gemini_client(model=model)
                print(f"[{agent_name}] ✓ Gemini client initialized (model: {model})")
                return client

            elif provider_name in ["AZURE", "OPENAI"]:
                print(f"[{agent_name}] Calling get_azure_client()...")
                client = get_azure_client()
                print(f"[{agent_name}] ✓ Azure OpenAI client initialized")
                if hasattr(client, 'deployment_name'):
                    print(f"[{agent_name}]   Deployment: {client.deployment_name}")
                return client

            else:
                # Fallback
                print(f"[{agent_name}] ⚠ Unknown provider '{provider_name}', using Azure OpenAI fallback")
                client = get_azure_client()
                return client

        except Exception as e:
            print(f"[{agent_name}] ✗ LLM setup FAILED with exception: {e}")
            print(f"[{agent_name}]   Provider was: {provider_name}")
            import traceback
            traceback.print_exc()
            return None
