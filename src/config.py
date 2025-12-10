import os
from typing import Dict, Optional, Any, List
from pydantic import Field, computed_field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMProviderConfig(BaseModel):
    api_key: Optional[str] = Field(None, validation_alias="API_KEY")
    base_url: Optional[str] = Field(None, validation_alias="BASE_URL")
    model: Optional[str] = Field(None)
    deployment_name: Optional[str] = Field(None) # Azure specific
    version: str = "2024-12-01-preview"

class EconomyConfig(BaseSettings):
    # Machines
    machine_cost: float = Field(500.0, description="Cost to buy a new standard machine")
    machine_upgrade_cost: float = Field(500.0, description="Cost to upgrade a machine")
    
    # Staff
    hiring_cost: float = 100.0
    staff_min_wage: float = 15.0 # Hourly? or Weekly? Server uses ~300/week, Models use 15. Standardize on Weekly?
    # Let's support both but default to weekly in server logic
    staff_weekly_wage_default: float = 300.0 
    staff_training_cost: float = 150.0
    severance_weeks: int = 2
    
    # Marketing
    marketing_cost_divisor: float = 20.0 # Cost / Divisor = Boost
    marketing_base_boost: float = 0.05
    marketing_decay_rate: float = 5.0
    
    # Defaults
    initial_balance: float = 2500.0
    default_price: float = 5.0
    
class SimulationConfig(BaseSettings):
    # World
    default_game_master_model: str = "gemini-flash-latest"
    default_judge_model: str = "claude-4.5-opus"
    default_npc_provider: str = "PHI"
    
    # Agents
    agent_default_model: str = "gemini-1.5-flash"
    agent_temperature: float = 0.7
    agent_max_tokens: int = 1000
    
    # Game Mechanics
    machine_wear_rate: float = 0.01
    machine_breakdown_threshold: float = 0.2
    machine_breakdown_chance: float = 0.3
    
class VendorConfig(BaseSettings):
    # Market
    price_fluctuation_rate: float = 0.2
    special_offer_chance: float = 0.2
    special_offer_discount_base: float = 0.8
    negotiation_discount_step: float = 0.05
    negotiation_max_discount: float = 0.3

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        case_sensitive=False
    )
    
    # Nested Configs
    economy: EconomyConfig = Field(default_factory=EconomyConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    vendor: VendorConfig = Field(default_factory=VendorConfig)
    
    # LLM Providers (Dynamic Dict)
    # We map environment variables like AZURE_API_KEY to this dict structure? 
    # Actually, pydantic-settings handles env vars well for nested classes if named correctly (LLM__AZURE__API_KEY),
    # but our env vars are AZURE_api_key. 
    # We will stick to a helper to load these specific legacy env vars into the structure or use the computed field.
    
    # Legacy env var mapping support
    @computed_field
    @property
    def llm(self) -> Dict[str, LLMProviderConfig]:
        """Load LLM configs from environment using legacy naming convention (PROVIDER_Suffix)."""
        providers = ["AZURE", "OPENAI", "GEMINI", "OPSUS", "META", "MISTRAL", "PHI"]
        configs = {}
        for p in providers:
            configs[p] = LLMProviderConfig(
                api_key=os.environ.get(f"{p}_api_key"),
                base_url=os.environ.get(f"{p}_base_url"),
                model=os.environ.get(f"{p}_deployment_name") or os.environ.get(f"{p}_model"),
                deployment_name=os.environ.get(f"{p}_deployment_name"),
                version="2024-12-01-preview"
            )
        return configs
        
    # Global Configs
    debug_mode: bool = False
    log_level: str = "INFO"

settings = Settings()

# Backward compatibility for LLMDICT
LLMDICT = {}
for name, conf in settings.llm.items():
    LLMDICT[name] = {
        "APIKEY": conf.api_key,
        "BASEURL": conf.base_url,
        "MODEL": conf.model,
        "VERSION": conf.version,
    }
