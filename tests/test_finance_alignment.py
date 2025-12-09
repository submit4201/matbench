
import pytest
import pytest
from src.engine.finance.credit import CreditSystem
from src.engine.finance.models import CreditScore, TransactionCategory, FinancialLedger
from src.engine.finance.taxation import TaxSystem
from src.world.laundromat import LaundromatState, Machine


def test_loan_terms_alignment():
    """Verify loan terms match World Bible (Audit Report) specifications."""
    cs = CreditSystem()
    
    # Mock agent with good credit to pass min_score checks
    agent_id = "test_agent"
    cs.agent_credit[agent_id] = CreditScore(
        payment_history_score=100.0,
        utilization_score=100.0,
        history_length_score=100.0,
        credit_mix_score=100.0,
        new_credit_score=100.0
    ) # Should give ~850 score
    cs.agent_accounts[agent_id] = []
    cs.credit_inquiries[agent_id] = []
    cs.scheduled_payments[agent_id] = []
    
    # helper to check specific loan
    def check_loan(loan_type, expected_term, expected_base_rate_approx):
        # Reset state for each check to avoid utilization/inquiry penalties affecting subsequent tests
        cs.agent_accounts[agent_id] = []
        cs.credit_inquiries[agent_id] = []
        cs.agent_credit[agent_id] = CreditScore(
            payment_history_score=100.0,
            utilization_score=100.0,
            history_length_score=100.0,
            credit_mix_score=100.0,
            new_credit_score=100.0
        )
        
        result = cs.apply_for_loan(agent_id, loan_type, 1000.0, current_week=1)
        assert result["approved"] is True
        assert result["term_weeks"] == expected_term
        # Rate check: allowed small margin for calculation differences
        # Base rate in code is (monthly * 12) / 52. 
        # But final rate includes credit score adjustment (0% for perfect score).
        # Wait, code: rate_adjustment = (850 - score) / 850 * 0.05
        # If score is ~850, adj is 0. So rate should be base_rate.
        
        # We can't easily check internal base_rate config, but we can check the result interest_rate
        # We expect it to be close to the monthly_rate * 12 / 52
        margin = 0.001
        assert abs(result["interest_rate"] - expected_base_rate_approx) < margin

    # 1. Equipment Loan: 24 weeks, ~4% monthly
    # 4% monthly * 12 = 48% annual. / 52 = ~0.0092 weekly
    check_loan("equipment_loan", 24, (0.04 * 12) / 52)
    
    # 2. Expansion Loan: 48 weeks, ~3.5% monthly
    # 3.5% * 12 = 42%. / 52 = ~0.0080
    check_loan("expansion_loan", 48, (0.035 * 12) / 52)
    
    # 3. Emergency Loan: 4 weeks, ~8% monthly
    # 8% * 12 = 96%. / 52 = ~0.0184
    check_loan("emergency_loan", 4, (0.08 * 12) / 52)

def test_tax_credits_logic():
    """Verify tax credits are calculated correctly."""
    tax_system = TaxSystem()
    
    state = LaundromatState(id="tax_test", name="Tax Test Laundry")
    # Setup ledger manually
    state.ledger = FinancialLedger()
    
    # 1. Green Equipment Credit (10% of value)
    # Add an eco machine
    eco_machine = Machine(id="M1", type="eco_washer")
    eco_machine.is_eco = True 
    state.machines.append(eco_machine)
    # Value assumed $500 in code. Credit = $50.
    
    # 2. Community Investment (5% of donations)
    state.ledger.add(-1000.0, "expense", "Charity Donation and sponsorship", week=1)
    # Credit = $50
    
    # 3. Job Creation ($100 per employee)
    # Add fake staff
    from dataclasses import dataclass
    @dataclass
    class Staff:
        wage: float = 15.0
    state.staff.append(Staff())
    state.staff.append(Staff())
    # Credit = $200
    
    # Total expected credits: 50 + 50 + 200 = 300
    
    # Pass lists to method locally as the signature changed in refactor to accept (transactions, machines, staff)
    credits = tax_system._calculate_tax_credits(state.ledger.transactions, state.machines, state.staff)
    assert credits == 300.0
