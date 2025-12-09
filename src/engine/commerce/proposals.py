from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import uuid
import json

class ProposalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"

@dataclass
class Proposal:
    id: str
    agent_id: str
    name: str
    category: str  # wash, dry, bundle, premium, ancillary, other
    description: str
    pricing_model: str
    resource_requirements: str
    setup_cost: float = 0.0
    status: ProposalStatus = ProposalStatus.PENDING
    evaluation: Dict[str, Any] = field(default_factory=dict)
    created_week: int = 0

class ProposalManager:
    def __init__(self, game_engine, llm_provider="azure"):
        self.game_engine = game_engine
        self.proposals: Dict[str, Proposal] = {}
        self.llm_provider = llm_provider
        
        # Initialize LLM
        try:
            from src.engine.llm_utils import LLMHelper
            self.llm_client, self.deployment = LLMHelper.setup_llm(llm_provider)
        except Exception as e:
            print(f"Failed to initialize LLM for ProposalManager: {e}")
            self.llm_client = None
            self.deployment = None
        
    def submit_proposal(self, agent_id: str, data: Dict[str, Any], week: int) -> Proposal:
        proposal_id = str(uuid.uuid4())[:8]
        proposal = Proposal(
            id=proposal_id,
            agent_id=agent_id,
            name=data.get("name", "Untitled Proposal"),
            category=data.get("category", "other"),
            description=data.get("description", ""),
            pricing_model=data.get("pricing_model", ""),
            resource_requirements=data.get("resource_requirements", ""),
            setup_cost=float(data.get("setup_cost", 0.0)),
            created_week=week
        )
        self.proposals[proposal_id] = proposal
        
        # Trigger Evaluation
        self._evaluate_proposal(proposal)
        
        return proposal

    def _evaluate_proposal(self, proposal: Proposal):
        """
        Evaluates the proposal using LLM (or mock if unavailable).
        """
        if self.llm_client:
            try:
                self._llm_evaluate(proposal)
            except Exception as e:
                print(f"LLM evaluation failed, falling back to mock: {e}")
                self._mock_evaluate(proposal)
        else:
            self._mock_evaluate(proposal)

    def _llm_evaluate(self, proposal: Proposal):
        from src.engine.llm_utils import LLMHelper
        
        prompt = f"""
        You are a business consultant for a laundromat simulation game. 
        Evaluate the following revenue stream proposal:
        
        Name: {proposal.name}
        Category: {proposal.category}
        Description: {proposal.description}
        Pricing Model: {proposal.pricing_model}
        Resource Requirements: {proposal.resource_requirements}
        
        Analyze the feasibility, profitability, and customer appeal of this idea.
        
        Respond with a JSON object in the following format:
        {{
            "feasibility_score": <0-100 integer>,
            "profitability": "<Low/Medium/High>",
            "customer_appeal": "<Low/Moderate/High> (<Brief Reason>)",
            "upkeep": "<Brief description of maintenance costs/effort>",
            "reasoning": "<1-2 sentences explaining the evaluation>"
        }}
        """
        
        response_text = LLMHelper.call_llm(
            self.llm_client, 
            self.deployment, 
            prompt, 
            max_tokens=300, 
            provider=self.llm_provider
        )
        
        data = LLMHelper.parse_json_response(response_text)
        
        proposal.evaluation = {
            "feasibility_score": data.get("feasibility_score", 50),
            "profitability": data.get("profitability", "Medium"),
            "customer_appeal": data.get("customer_appeal", "Moderate"),
            "upkeep": data.get("upkeep", "Standard maintenance"),
            "reasoning": data.get("reasoning", "Automated evaluation.")
        }

    def _mock_evaluate(self, proposal: Proposal):
        """Mock evaluation logic based on keywords."""
        score = 50
        profitability = "Medium"
        appeal = "Moderate"
        
        desc = proposal.description.lower()
        if "eco" in desc or "green" in desc:
            score += 20
            appeal = "High (Eco-conscious)"
        if "luxury" in desc or "premium" in desc:
            profitability = "High"
            score += 10
        if "free" in desc:
            profitability = "None"
            score -= 30
            
        proposal.evaluation = {
            "feasibility_score": score,
            "profitability": profitability,
            "customer_appeal": appeal,
            "upkeep": "Requires weekly maintenance ($50)",
            "reasoning": "Automated preliminary assessment (Mock)."
        }

    def approve_proposal(self, proposal_id: str) -> bool:
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
            
        state = self.game_engine.get_state(proposal.agent_id)
        if not state:
            return False
            
        # Check and deduct funds
        if state.balance < proposal.setup_cost:
            return False
            
        state.balance -= proposal.setup_cost
        
        proposal.status = ProposalStatus.APPROVED
        
        # Add to agent's revenue streams
        if state:
            from src.engine.finance import RevenueStream
            
            # Determine price from model or default
            price = 5.0
            try:
                # Simple extraction if user put a number
                import re
                prices = re.findall(r'\d+\.?\d*', proposal.pricing_model)
                if prices:
                    price = float(prices[0])
            except:
                pass
                
            stream = RevenueStream(
                name=proposal.name,
                category="custom",
                price=price,
                cost_per_unit=price * 0.3, # Assume 30% cost
                demand_multiplier=1.0, # Baseline
                unlocked=True,
                description=proposal.description
            )
            state.revenue_streams[proposal.name] = stream
            
        return True

    def reject_proposal(self, proposal_id: str) -> bool:
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False
        proposal.status = ProposalStatus.REJECTED
        return True

    def get_proposals(self, agent_id: str) -> List[Proposal]:
        return [p for p in self.proposals.values() if p.agent_id == agent_id]
