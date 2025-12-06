"""
Factory for creating LLM-enabled NPCs (customers, vendors, event managers).
Provides consistent configuration and easy toggling between LLM and rule-based NPCs.
"""
import os
from typing import List, Union
from src.engine.customer import Customer, LLMCustomer
from src.engine.vendor import VendorManager
from src.engine.events import EventManager


class NPCFactory:
    """Factory for creating LLM-enabled or rule-based NPCs."""
    
    @staticmethod
    def create_customers(
        count: int,
        use_llm: bool = True,
        llm_provider: str = "openai",
        llm_ratio: float = 1.0
    ) -> List[Customer]:
        """
        Create a mix of customers.
        
        Args:
            count: Total number of customers to create
            use_llm: Whether to use LLM customers
            llm_provider: LLM provider name (openai, azure, google, etc.)
            llm_ratio: Ratio of LLM customers (0.0-1.0). 1.0 = all LLM, 0.5 = half LLM
        
        Returns:
            List of Customer objects (mix of LLM and regular based on ratio)
        """
        customers = []
        llm_count = int(count * llm_ratio) if use_llm else 0
        
        # Create LLM customers
        for i in range(llm_count):
            try:
                customers.append(LLMCustomer(f"llm_c{i}", llm_provider=llm_provider))
            except Exception as e:
                print(f"[NPCFactory] Failed to create LLM customer {i}: {e}, using regular customer")
                customers.append(Customer(f"llm_c{i}"))
        
        # Create regular customers
        for i in range(count - llm_count):
            customers.append(Customer(f"c{i}"))
        
        print(f"[NPCFactory] Created {len(customers)} customers ({llm_count} LLM, {count - llm_count} regular)")
        return customers
    
    @staticmethod
    def create_vendor_manager(
        use_llm: bool = True,
        llm_provider: str = "openai"
    ) -> VendorManager:
        """
        Create a vendor manager (LLM or regular).
        
        Args:
            use_llm: Whether to use LLM vendor
            llm_provider: LLM provider name
        
        Returns:
            VendorManager object
        """
        try:
            manager = VendorManager(use_llm=use_llm, llm_provider=llm_provider)
            mode = "LLM-enhanced" if use_llm else "regular"
            print(f"[NPCFactory] Created {mode} vendor manager with {len(manager.vendors)} vendors")
            return manager
        except Exception as e:
            print(f"[NPCFactory] Failed to create vendor manager: {e}, using default")
            return VendorManager(use_llm=False)
    
    @staticmethod
    def create_event_manager(
        use_llm: bool = True,
        llm_provider: str = "openai"
    ) -> EventManager:
        """
        Create an event manager (LLM or regular).
        
        Args:
            use_llm: Whether to use LLM for event generation
            llm_provider: LLM provider name
        
        Returns:
            EventManager object
        """
        event_manager = EventManager(use_llm=use_llm, llm_provider=llm_provider)
        mode = "LLM-enhanced" if use_llm else "regular"
        print(f"[NPCFactory] Created {mode} event manager")
        return event_manager
    
    @staticmethod
    def from_env() -> dict:
        """
        Create NPCs based on environment variables.
        
        Env vars:
            USE_LLM_NPCS: "true" to enable LLM NPCs
            LLM_NPC_PROVIDER: provider name (default: "openai")
            LLM_CUSTOMER_RATIO: ratio of LLM customers (default: 1.0)
            CUSTOMER_COUNT: number of customers (default: 50)
        
        Returns:
            Dict with keys: 'customers', 'vendor_manager', 'event_manager'
        """
        use_llm = os.getenv("USE_LLM_NPCS", "false").lower() == "true"
        provider = os.getenv("LLM_NPC_PROVIDER", "openai")
        customer_ratio = float(os.getenv("LLM_CUSTOMER_RATIO", "1.0"))
        customer_count = int(os.getenv("CUSTOMER_COUNT", "50"))
        
        return {
            "customers": NPCFactory.create_customers(
                count=customer_count,
                use_llm=use_llm,
                llm_provider=provider,
                llm_ratio=customer_ratio
            ),
            "vendor_manager": NPCFactory.create_vendor_manager(
                use_llm=use_llm,
                llm_provider=provider
            ),
            "event_manager": NPCFactory.create_event_manager(
                use_llm=use_llm,
                llm_provider=provider
            )
        }
