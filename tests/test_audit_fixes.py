import unittest
from src.engine.game_engine import GameEngine
from src.engine.proposals import Proposal, ProposalStatus

class TestAuditFixes(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine(agent_ids=["p1", "cpu1"])
        self.p1_state = self.engine.get_state("p1")
        # Give P1 some money
        self.p1_state.balance = 5000.0

    def test_proposal_cost_deduction(self):
        """Verify that approving a proposal deducts the setup cost."""
        initial_balance = self.p1_state.balance
        setup_cost = 1500.0
        
        # 1. Create Proposal
        proposal_data = {
            "name": "Luxury Valet",
            "category": "premium",
            "description": "High end service",
            "setup_cost": setup_cost,
            "pricing_model": "$50 per bag"
        }
        
        proposal = self.engine.proposal_manager.submit_proposal("p1", proposal_data, week=1)
        
        self.assertEqual(proposal.setup_cost, setup_cost)
        self.assertEqual(self.p1_state.balance, initial_balance) # Not deducted yet
        
        # 2. Approve Proposal
        success = self.engine.proposal_manager.approve_proposal(proposal.id)
        
        self.assertTrue(success, "Proposal should be approved")
        self.assertEqual(proposal.status, ProposalStatus.APPROVED)
        
        # 3. Check Balance (Should be deducted)
        expected_balance = initial_balance - setup_cost
        self.assertEqual(self.p1_state.balance, expected_balance, 
                         f"Balance should be {expected_balance} but was {self.p1_state.balance}")
                         
    def test_proposal_insufficient_funds(self):
        """Verify approval fails if insufficient funds."""
        self.p1_state.balance = 100.0
        setup_cost = 5000.0
        
        proposal_data = {"name": "Moon Base", "setup_cost": setup_cost}
        proposal = self.engine.proposal_manager.submit_proposal("p1", proposal_data, week=1)
        
        success = self.engine.proposal_manager.approve_proposal(proposal.id)
        
        self.assertFalse(success, "Should fail due to insufficient funds")
        self.assertEqual(proposal.status, ProposalStatus.PENDING)
        self.assertEqual(self.p1_state.balance, 100.0, "Balance should not change")

    def test_metrics_auditor_history(self):
        """Verify metrics are recorded on turn processing."""
        # Run a turn
        self.engine.process_turn()
        
        # Check auditor history
        history = self.engine.metrics_auditor.history
        self.assertGreater(len(history), 0, "Metrics history should not be empty")
        
        # Check structure
        entry = history[0]
        self.assertEqual(entry["agent_id"], "p1")
        self.assertIn("weekly_revenue", entry)
        self.assertIn("social_score_total", entry)
        self.assertIn("cash_balance", entry)
        self.assertEqual(entry["week"], 1) # Should be week 1 as we started at 1 and processed once

if __name__ == '__main__':
    unittest.main()
