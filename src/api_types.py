from pydantic import BaseModel
from typing import Dict, Any, Optional

class ActionRequest(BaseModel):
    agent_id: str
    action_type: str
    parameters: Dict[str, Any]

class ScenarioRequest(BaseModel):
    scenario_name: Optional[str] = None

class NegotiateRequest(BaseModel):
    agent_id: str
    vendor_id: str
    item: str

class ProposalRequest(BaseModel):
    agent_id: str
    name: str
    category: str
    description: str
    pricing_model: str
    resource_requirements: str

class CreditPaymentRequest(BaseModel):
    payment_id: str
    amount: float

class DiplomacyProposalRequest(BaseModel):
    agent_id: str
    target_id: str
    type: str = "alliance" # alliance, buyout, trade
