"""
Shared LLM utility for NPC systems.
Provides centralized LLM setup and calling logic to avoid code duplication.
"""
import json
from typing import Dict, Any, Optional


class LLMHelper:
    """Shared utility for LLM operations across NPCs."""
    
    @staticmethod
    def setup_llm(provider: str):
        """
        Setup LLM client based on provider name.
        Returns tuple of (llm_client, deployment_name)
        """
        # Import our new helpers
        from src.agents.azure_helper import get_azure_client
        from src.agents.meta_helper import get_meta_client
        from src.agents.mistral_helper import get_mistral_client
        from src.agents.phi_helper import get_phi_client
        from src.agents.gemini_helper import get_gemini_client
        from src.agents.opsus_helper import get_claude_client
        
        llm = None
        deployment = None
        
        provider_lower = provider.lower()
        
        if provider_lower in ["openai", "azure"]:
            llm = get_azure_client()
            deployment = llm.deployment_name
            
        elif provider_lower == "meta":
            llm = get_meta_client()
            deployment = llm.deployment_name

        elif provider_lower == "mistral":
            llm = get_mistral_client()
            deployment = llm.deployment_name
            
        elif provider_lower == "phi":
            llm = get_phi_client()
            deployment = llm.deployment_name
            
        elif provider_lower in ["google", "gemini"]:
            llm = get_gemini_client()
            deployment = llm.model
            
        elif provider_lower in ["opsus", "claude"]:
            llm = get_claude_client()
            deployment = llm.deployment_name
            
        else:
            # Default to Azure
            print(f"[LLMHelper] Unknown provider '{provider}', defaulting to Azure")
            llm = get_azure_client()
            deployment = llm.deployment_name
        
        return llm, deployment
    
    @staticmethod
    def call_llm(
        llm,
        deployment: str,
        prompt: str,
        max_tokens: int = 300,
        temperature: float = 0.7,
        provider: str = "openai"
    ) -> str:
        """
        Call LLM with unified interface across providers.
        Returns the response text or raises an exception.
        """
        try:
            provider_lower = provider.lower()
            
            if provider_lower in ["google", "gemini"]:
                # Gemini uses our helper which has OpenAI-compatible interface
                response = llm.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant in a business simulation game."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            else:
                # All other providers use OpenAI-compatible interface
                # O-series models (o1, o3) don't support temperature
                is_o_series = deployment and (deployment.startswith('o1') or deployment.startswith('o3'))
                
                # Build request params
                request_params = {
                    "model": deployment,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant in a business simulation game."},
                        {"role": "user", "content": prompt}
                    ],
                }
                
                # Add parameters based on model type
                if is_o_series:
                    # O-series: use max_completion_tokens, no temperature
                    request_params["max_completion_tokens"] = max_tokens
                else:
                    # Standard models
                    request_params["max_completion_tokens"] = max_tokens
                    request_params["temperature"] = temperature
                
                try:
                    response = llm.chat.completions.create(**request_params)
                    return response.choices[0].message.content
                except Exception as e:
                    # If temperature fails, retry without it
                    if "temperature" in str(e).lower():
                        del request_params["temperature"]
                        response = llm.chat.completions.create(**request_params)
                        return response.choices[0].message.content
                    raise
                
        except Exception as e:
            raise Exception(f"LLM call failed: {str(e)}")
    
    @staticmethod
    def parse_json_response(response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response with robust handling.
        Strips markdown code blocks if present.
        """
        try:
            # Clean up markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Parse JSON
            data = json.loads(response_text.strip())
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {e}\nResponse: {response_text}")
    
    @staticmethod
    def safe_call_llm(
        llm,
        deployment: str,
        prompt: str,
        max_tokens: int = 300,
        temperature: float = 0.7,
        provider: str = "openai",
        fallback_value: Optional[str] = None
    ) -> Optional[str]:
        """
        Call LLM with error handling and optional fallback.
        Returns response text on success, fallback_value on failure.
        """
        try:
            return LLMHelper.call_llm(llm, deployment, prompt, max_tokens, temperature, provider)
        except Exception as e:
            print(f"[LLMHelper] LLM call failed: {e}")
            return fallback_value
