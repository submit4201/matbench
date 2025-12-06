"""
NPC Helper for Laundromat Tycoon Benchmark

Lightweight LLM wrapper for generating dynamic NPC content:
- Customer complaints and comments
- Vendor offers and negotiations  
- World events and neighborhood changes

Uses fast/cheap models (PHI or MISTRAL) to minimize costs while maintaining realism.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Import all helpers - use relative imports
from phi_helper import get_phi_client
from mistral_helper import get_mistral_client
from meta_helper import get_meta_client
from gemini_helper import get_gemini_client

load_dotenv()


class NPCHelper:
    """
    Lightweight helper for NPC text generation.
    
    Uses fast/cheap models by default (PHI > MISTRAL > META > GEMINI).
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize NPC helper.
        
        Args:
            provider: Specific provider to use (PHI, MISTRAL, META, GEMINI)
                     If None, uses NPC_PROVIDER from env or defaults to PHI
        """
        self.provider = provider or os.environ.get("NPC_PROVIDER", "PHI")
        self.client = self._get_client()
        
    def _get_client(self):
        """Get LLM client based on provider"""
        try:
            if self.provider == "PHI":
                return get_phi_client()
            elif self.provider == "MISTRAL":
                return get_mistral_client()
            elif self.provider == "META":
                return get_meta_client()
            elif self.provider == "GEMINI":
                return get_gemini_client()
            else:
                # Default to PHI
                print(f"[NPC] Unknown provider '{self.provider}', using PHI")
                return get_phi_client()
        except Exception as e:
            print(f"[NPC] Failed to initialize {self.provider}: {e}")
            # Fallback to PHI
            return get_phi_client()
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.8
    ) -> str:
        """
        Generate NPC text from a prompt.
        
        Args:
            prompt: The generation prompt
            max_tokens: Maximum tokens to generate
            temperature: Creativity (0.0-1.0, higher = more creative)
            
        Returns:
            Generated text string
        """
        try:
            # Get model name
            if hasattr(self.client, 'deployment_name'):
                model = self.client.deployment_name
            elif hasattr(self.client, 'model'):
                model = self.client.model
            else:
                model = "unknown"
            
            # Generate
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a creative writer generating realistic NPC dialogue and events for a laundromat business simulation game."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            print(f"[NPC] Generation failed: {e}")
            return f"[Error generating NPC content: {e}]"


# Global instance for convenience
_npc_helper = None


def get_npc_helper(provider: Optional[str] = None) -> NPCHelper:
    """Get or create the global NPC helper instance"""
    global _npc_helper
    if _npc_helper is None or provider is not None:
        _npc_helper = NPCHelper(provider)
    return _npc_helper


def generate_npc_text(prompt: str, max_tokens: int = 150, temperature: float = 0.8) -> str:
    """
    Convenience function for quick NPC text generation.
    
    Args:
        prompt: The generation prompt
        max_tokens: Maximum tokens to generate
        temperature: Creativity (0.0-1.0)
        
    Returns:
        Generated text string
    """
    helper = get_npc_helper()
    return helper.generate_text(prompt, max_tokens, temperature)


# Specific NPC generation functions
def generate_customer_complaint(issue: str = "general dissatisfaction") -> str:
    """Generate a realistic customer complaint"""
    prompt = f"Generate a brief, realistic customer complaint about {issue} at a laundromat. Keep it under 100 words and make it sound natural."
    return generate_npc_text(prompt, max_tokens=120, temperature=0.7)


def generate_vendor_offer(item: str = "soap", discount: int = 10) -> str:
    """Generate a vendor special offer message"""
    prompt = f"Generate a brief vendor message offering a {discount}% discount on {item}. Keep it professional and under 80 words."
    return generate_npc_text(prompt, max_tokens=100, temperature=0.6)


def generate_world_event() -> str:
    """Generate a random neighborhood event"""
    prompt = "Generate a brief random event affecting a neighborhood with laundromats (weather, local news, construction, etc.). Keep it under 100 words."
    return generate_npc_text(prompt, max_tokens=120, temperature=0.9)


def generate_customer_comment(satisfaction: str = "neutral") -> str:
    """Generate a customer comment based on satisfaction level"""
    prompt = f"Generate a brief customer comment with {satisfaction} satisfaction about their laundromat experience. Keep it under 60 words."
    return generate_npc_text(prompt, max_tokens=80, temperature=0.7)


if __name__ == "__main__":
    # Test NPC generation
    print("="*60)
    print("NPC Helper Test")
    print("="*60)
    
    print("\n1. Customer Complaint:")
    print(generate_customer_complaint("broken washing machines"))
    
    print("\n2. Vendor Offer:")
    print(generate_vendor_offer("bulk soap", 15))
    
    print("\n3. World Event:")
    print(generate_world_event())
    
    print("\n4. Customer Comment (positive):")
    print(generate_customer_comment("high"))
    
    print("\n" + "="*60)
