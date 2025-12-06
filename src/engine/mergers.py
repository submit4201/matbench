from dataclasses import dataclass
from typing import Optional
from src.world.laundromat import LaundromatState

@dataclass
class MergerProposal:
    buyer_id: str
    target_id: str
    offer_price: float
    status: str = "pending" # pending, accepted, rejected

class MergerSystem:
    def __init__(self):
        self.active_proposals: list[MergerProposal] = []

    def initiate_buyout(self, buyer_state: LaundromatState, target_state: LaundromatState, offer_price: float) -> MergerProposal:
        """
        Initiates a buyout proposal.
        """
        if buyer_state.balance < offer_price:
            raise ValueError("Insufficient funds for buyout offer")
            
        proposal = MergerProposal(
            buyer_id=buyer_state.id,
            target_id=target_state.id,
            offer_price=offer_price
        )
        self.active_proposals.append(proposal)
        return proposal

    def process_response(self, proposal: MergerProposal, accepted: bool, buyer_state: LaundromatState, target_state: LaundromatState):
        """
        Finalizes the merger if accepted.
        """
        if accepted:
            if buyer_state.balance >= proposal.offer_price:
                buyer_state.balance -= proposal.offer_price
                target_state.balance += proposal.offer_price
                
                # Transfer assets
                buyer_state.machines.extend(target_state.machines)
                target_state.machines = []
                
                # Transfer reputation (weighted average or similar logic)
                # Simplified: Buyer absorbs target
                
                proposal.status = "accepted"
                return True
            else:
                proposal.status = "failed_funds"
                return False
        else:
            proposal.status = "rejected"
            return False
