import pytest
from src.world.alliances import TrustSystem, AllianceType
from src.engine.mergers import MergerSystem
from src.engine.communication import CommunicationChannel
from src.world.laundromat import LaundromatState

def test_trust_and_alliances():
    trust_sys = TrustSystem(["agent_a", "agent_b"])
    
    # Initial trust
    assert trust_sys.get_trust("agent_a", "agent_b") == 50.0
    
    # Increase trust
    trust_sys.update_trust("agent_a", "agent_b", 30.0)
    assert trust_sys.get_trust("agent_a", "agent_b") == 80.0
    
    # Propose alliance (should succeed as trust > 70)
    alliance = trust_sys.propose_alliance("agent_b", "agent_a", AllianceType.NON_AGGRESSION, duration=4)
    assert alliance is not None
    assert alliance.type == AllianceType.NON_AGGRESSION
    assert len(trust_sys.active_alliances) == 1

def test_merger_system():
    merger_sys = MergerSystem()
    buyer = LaundromatState(name="Buyer", id="buyer", balance=1000.0)
    target = LaundromatState(name="Target", id="target", balance=100.0)
    
    # Initiate buyout
    proposal = merger_sys.initiate_buyout(buyer, target, offer_price=500.0)
    assert proposal.status == "pending"
    
    # Accept buyout
    success = merger_sys.process_response(proposal, True, buyer, target)
    assert success is True
    assert proposal.status == "accepted"
    assert buyer.balance == 500.0
    assert target.balance == 600.0 # 100 + 500

def test_communication():
    comm = CommunicationChannel()
    comm.send_message("agent_a", "agent_b", "Hello!", week=1)
    
    msgs = comm.get_conversation("agent_a", "agent_b")
    assert len(msgs) == 1
    assert msgs[0].content == "Hello!"

if __name__ == "__main__":
    test_trust_and_alliances()
    test_merger_system()
    test_communication()
    print("All advanced interaction tests passed!")
