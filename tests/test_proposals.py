import pytest
from src.engine.game_engine import GameEngine
from src.engine.proposals import ProposalManager, ProposalStatus

def test_proposal_submission_and_evaluation():
    engine = GameEngine(["p1"])
    manager = engine.proposal_manager
    
    data = {
        "name": "Eco Wash",
        "category": "wash",
        "description": "A green wash using eco-friendly soap.",
        "pricing_model": "$5.00 per load",
        "resource_requirements": "Eco Soap"
    }
    
    proposal = manager.submit_proposal("p1", data, 1)
    
    assert proposal.name == "Eco Wash"
    assert proposal.status == ProposalStatus.PENDING
    assert proposal.evaluation is not None
    # Mock evaluation should give positive score for "Eco"
    assert proposal.evaluation["feasibility_score"] > 50
    assert "Eco-conscious" in proposal.evaluation["customer_appeal"]

def test_proposal_approval():
    engine = GameEngine(["p1"])
    manager = engine.proposal_manager
    state = engine.get_state("p1")
    
    data = {
        "name": "Premium Fold",
        "category": "premium",
        "description": "Hand folding service.",
        "pricing_model": "$10.00",
        "resource_requirements": "Staff"
    }
    
    proposal = manager.submit_proposal("p1", data, 1)
    success = manager.approve_proposal(proposal.id)
    
    assert success is True
    assert proposal.status == ProposalStatus.APPROVED
    
    # Check if added to revenue streams
    assert "Premium Fold" in state.revenue_streams
    stream = state.revenue_streams["Premium Fold"]
    assert stream.price == 10.0
    assert stream.unlocked is True

def test_proposal_rejection():
    engine = GameEngine(["p1"])
    manager = engine.proposal_manager
    
    data = {"name": "Bad Idea"}
    proposal = manager.submit_proposal("p1", data, 1)
    
    success = manager.reject_proposal(proposal.id)
    assert success is True
    assert proposal.status == ProposalStatus.REJECTED
