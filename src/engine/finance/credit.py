# [ ]↔T: Credit & FICO Score System
#   - [x] CreditScore dataclass with FICO-like calculation
#   - [x] SBA Loan starting condition
#   - [x] Payment history tracking
#   - [x] Credit utilization tracking
#   - [x] Score impact on loan terms
# PRIORITY: P1 - Critical for financial realism
# STATUS: Complete 

"""
Credit & FICO Score System

Implements a credit scoring system similar to FICO for the laundromat simulation.
Agents start with an SBA loan and must build credit through:
- Timely payments (35% weight)
- Credit utilization (30% weight)
- Length of credit history (15% weight)
- Credit mix (10% weight)
- New credit inquiries (10% weight)

This adds a financial responsibility dimension to LLM evaluation.
"""

from typing import Dict, List, Any, Optional
import logging
import uuid
from src.engine.finance.models import (
    CreditScore, CreditAccount, PaymentRecord, PaymentStatus, CreditRating
)
from src.engine.finance.loans import LoanSystem

logger = logging.getLogger(__name__)

class CreditSystem:
    """
    Manages credit scoring for all agents.
    Delegates loan creation to LoanSystem but determines terms based on score.
    """
    
    def __init__(self):
        self.agent_credit: Dict[str, CreditScore] = {}
        self.agent_accounts: Dict[str, List[CreditAccount]] = {}
        self.scheduled_payments: Dict[str, List[PaymentRecord]] = {}
        self.credit_inquiries: Dict[str, List[int]] = {}  # agent_id -> list of weeks
        self.loan_system = LoanSystem()
    
    def initialize_agent(self, agent_id: str, starting_week: int = 1) -> Dict[str, Any]:
        """
        Initialize an agent with SBA loan starting condition.
        """
        # Create initial credit score (Fair range - new business)
        self.agent_credit[agent_id] = CreditScore(
            payment_history_score=70.0,
            utilization_score=50.0,
            history_length_score=30.0,
            credit_mix_score=50.0,
            new_credit_score=60.0
        )
        
        # Create SBA loan via LoanSystem
        # 6% APR, $5000, 1 year
        sba_loan = self.loan_system.create_loan(
            loan_type="sba_loan",
            amount=5000.0,
            interest_rate=0.06,
            term_weeks=52,
            current_week=starting_week
        )
        sba_loan.id = f"sba_{agent_id}" # Override ID for SBA specific

        self.agent_accounts[agent_id] = [sba_loan]
        
        # Schedule payments
        payments = self.loan_system.schedule_payments(sba_loan)
        self.scheduled_payments[agent_id] = payments
        
        self.credit_inquiries[agent_id] = [starting_week]
        
        logger.info(f"Initialized credit for {agent_id}: SBA Loan $5000, Score {self.agent_credit[agent_id].total_score}")
        
        return {
            "sba_loan_amount": 5000.0,
            "weekly_payment": sba_loan.weekly_payment,
            "initial_credit_score": self.agent_credit[agent_id].total_score,
            "first_payment_due_week": starting_week + 1
        }
    
    def get_due_payments(self, agent_id: str, current_week: int) -> List[PaymentRecord]:
        """Get payments due this week or overdue."""
        payments = self.scheduled_payments.get(agent_id, [])
        due = [p for p in payments if p.due_week <= current_week and p.status == PaymentStatus.SCHEDULED]
        return due
    
    def make_payment(
        self,
        agent_id: str,
        payment_id: str,
        amount: float,
        current_week: int
    ) -> Dict[str, Any]:
        """
        Process a scheduled loan payment (Updates score + delegates balance update).
        """
        payments = self.scheduled_payments.get(agent_id, [])
        payment = next((p for p in payments if p.id == payment_id), None)
        
        if not payment:
            return {"error": "Payment not found"}
        
        if payment.status != PaymentStatus.SCHEDULED:
            return {"error": "Payment already processed"}
        
        # Determine timeliness score impact
        weeks_late = current_week - payment.due_week
        if weeks_late <= 0:
            status = PaymentStatus.ON_TIME
            credit_impact = 2.0
        elif weeks_late <= 4:
            status = PaymentStatus.LATE_30
            credit_impact = -5.0
        elif weeks_late <= 8:
            status = PaymentStatus.LATE_60
            credit_impact = -15.0
        else:
            status = PaymentStatus.LATE_90
            credit_impact = -30.0
        
        # Update record
        payment.amount_paid = amount
        payment.paid_week = current_week
        payment.status = status
        
        # Delegate balance update to LoanSystem
        accounts = self.agent_accounts.get(agent_id, [])
        loan = next((a for a in accounts if a.id == payment.loan_id), None)
        remaining_balance = 0.0
        
        if loan:
            remaining_balance = self.loan_system.process_payment(loan, amount)
        
        # Update Score
        self._update_credit_score(agent_id, credit_impact, "payment_history")
        self._recalculate_utilization(agent_id)
        
        return {
            "success": True,
            "payment_status": status.value,
            "credit_impact": credit_impact,
            "new_credit_score": self.agent_credit[agent_id].total_score,
            "remaining_balance": remaining_balance
        }
    
    def mark_missed_payment(self, agent_id: str, payment_id: str, current_week: int) -> Dict[str, Any]:
        """Mark a payment as missed (called when deadline passes without payment)."""
        payments = self.scheduled_payments.get(agent_id, [])
        payment = next((p for p in payments if p.id == payment_id), None)
        
        if not payment:
            return {"error": "Payment not found"}
        
        weeks_late = current_week - payment.due_week
        
        if weeks_late <= 4:
            payment.status = PaymentStatus.LATE_30
            credit_impact = -10.0
        elif weeks_late <= 8:
            payment.status = PaymentStatus.LATE_60
            credit_impact = -25.0
        else:
            payment.status = PaymentStatus.LATE_90
            credit_impact = -40.0
        
        self._update_credit_score(agent_id, credit_impact, "payment_history")
        
        if payment.status == PaymentStatus.LATE_90:
            self._check_default(agent_id, payment.loan_id)
        
        return {
            "status": payment.status.value,
            "credit_impact": credit_impact,
            "new_score": self.agent_credit[agent_id].total_score
        }
    
    def _update_credit_score(self, agent_id: str, impact: float, component: str):
        """Update a specific component of credit score."""
        credit = self.agent_credit.get(agent_id)
        if not credit:
            return
        
        if component == "payment_history":
            credit.payment_history_score = max(0, min(100, credit.payment_history_score + impact))
        elif component == "utilization":
            credit.utilization_score = max(0, min(100, credit.utilization_score + impact))
        elif component == "history_length":
            credit.history_length_score = max(0, min(100, credit.history_length_score + impact))
        elif component == "credit_mix":
            credit.credit_mix_score = max(0, min(100, credit.credit_mix_score + impact))
        elif component == "new_credit":
            credit.new_credit_score = max(0, min(100, credit.new_credit_score + impact))
    
    def _recalculate_utilization(self, agent_id: str):
        accounts = self.agent_accounts.get(agent_id, [])
        if not accounts: return
        
        total_balance = sum(a.current_balance for a in accounts)
        total_limit = sum(a.credit_limit for a in accounts)
        
        utilization_ratio = total_balance / total_limit if total_limit > 0 else 0
        
        if utilization_ratio <= 0.10: score = 100
        elif utilization_ratio <= 0.30: score = 80
        elif utilization_ratio <= 0.50: score = 60
        elif utilization_ratio <= 0.75: score = 40
        else: score = 20
        
        self.agent_credit[agent_id].utilization_score = score
    
    def _check_default(self, agent_id: str, loan_id: str):
        accounts = self.agent_accounts.get(agent_id, [])
        for account in accounts:
            if account.id == loan_id:
                account.is_defaulted = True
                self._update_credit_score(agent_id, -50.0, "payment_history")
                logger.warning(f"Agent {agent_id} defaulted on loan {loan_id}")
                break
    
    def update_history_length(self, agent_id: str, current_week: int):
        accounts = self.agent_accounts.get(agent_id, [])
        if not accounts: return
        
        oldest_account = min(accounts, key=lambda a: a.opened_week)
        weeks_of_history = current_week - oldest_account.opened_week
        
        if weeks_of_history < 12:
            score = 30 + (weeks_of_history / 12) * 20
        elif weeks_of_history < 24:
            score = 50 + ((weeks_of_history - 12) / 12) * 20
        else:
            score = min(90, 70 + ((weeks_of_history - 24) / 24) * 20)
        
        self.agent_credit[agent_id].history_length_score = score
    
    def apply_for_loan(
        self,
        agent_id: str,
        loan_type: str,
        amount: float,
        current_week: int
    ) -> Dict[str, Any]:
        """
        Evaluates credit score, determines terms, and requests loan creation.
        """
        credit = self.agent_credit.get(agent_id)
        if not credit:
            return {"approved": False, "reason": "No credit history"}
        
        score = credit.total_score
        
        # Record inquiry
        self.credit_inquiries[agent_id] = self.credit_inquiries.get(agent_id, [])
        self.credit_inquiries[agent_id].append(current_week)
        self._update_credit_score(agent_id, -3.0, "new_credit")
        
        # Loan Configs (Underwriting Rules)
        loan_configs = {
            "operating_credit": {"min_score": 580, "max_amount": 5000, "base_rate": 0.08, "term_weeks": 26},
            "equipment_loan": {"min_score": 620, "max_amount": 15000, "base_rate": 0.04 * 12 / 52, "term_weeks": 24},
            "expansion_loan": {"min_score": 700, "max_amount": 30000, "base_rate": 0.035 * 12 / 52, "term_weeks": 48},
            "emergency_loan": {"min_score": 500, "max_amount": 2000, "base_rate": 0.08 * 12 / 52, "term_weeks": 4}
        }
        
        config = loan_configs.get(loan_type)
        if not config:
            return {"approved": False, "reason": f"Unknown loan type: {loan_type}"}
        
        if score < config["min_score"]:
            return {"approved": False, "reason": f"Credit score {score} below minimum {config['min_score']}"}
        
        if amount > config["max_amount"]:
            return {"approved": False, "reason": f"Amount ${amount} exceeds max ${config['max_amount']}"}
        
        # Rate Adjustment
        rate_adjustment = (850 - score) / 850 * 0.05
        final_rate = config["base_rate"] + rate_adjustment
        
        # Create Loan logic
        loan = self.loan_system.create_loan(
            loan_type=loan_type,
            amount=amount,
            interest_rate=final_rate,
            term_weeks=config["term_weeks"],
            current_week=current_week
        )
        
        self.agent_accounts[agent_id].append(loan)
        payments = self.loan_system.schedule_payments(loan)
        self.scheduled_payments[agent_id].extend(payments) # Append to existing?
        # Actually schedule_payments should properly merge or append. 
        # Since scheduled_payments is a list of ALL payments for agent, extend is correct.
        
        # Update Mix
        existing_types = set(a.account_type for a in self.agent_accounts[agent_id])
        if len(existing_types) > 1:
            self._update_credit_score(agent_id, 5.0, "credit_mix")
            
        self._recalculate_utilization(agent_id)
        
        return {
            "approved": True,
            "loan_id": loan.id,
            "amount": amount,
            "interest_rate": round(final_rate, 4),
            "weekly_payment": loan.weekly_payment,
            "term_weeks": config["term_weeks"]
        }
    
    def get_credit_report(self, agent_id: str) -> Dict[str, Any]:
        """Get a full credit report for an agent."""
        credit = self.agent_credit.get(agent_id)
        accounts = self.agent_accounts.get(agent_id, [])
        payments = self.scheduled_payments.get(agent_id, [])
        
        if not credit:
            return {"error": "No credit history"}
        
        paid_payments = [p for p in payments if p.status != PaymentStatus.SCHEDULED]
        on_time = sum(1 for p in paid_payments if p.status == PaymentStatus.ON_TIME)
        late = sum(1 for p in paid_payments if p.status in [PaymentStatus.LATE_30, PaymentStatus.LATE_60, PaymentStatus.LATE_90])
        missed = sum(1 for p in paid_payments if p.status == PaymentStatus.MISSED)
        
        return {
            "credit_score": credit.total_score,
            "rating": credit.rating.value,
            "score_breakdown": {
                "payment_history": round(credit.payment_history_score, 1),
                "utilization": round(credit.utilization_score, 1),
                "history_length": round(credit.history_length_score, 1),
                "credit_mix": round(credit.credit_mix_score, 1),
                "new_credit": round(credit.new_credit_score, 1)
            },
            "accounts": [
                {
                    "id": a.id,
                    "type": a.account_type,
                    "original_amount": a.original_amount,
                    "current_balance": round(a.current_balance, 2),
                    "interest_rate": a.interest_rate,
                    "weekly_payment": a.weekly_payment,
                    "is_active": a.is_active,
                    "is_defaulted": a.is_defaulted
                }
                for a in accounts
            ],
            "total_debt": round(sum(a.current_balance for a in accounts), 2),
            "utilization_ratio": round(credit.utilization_score, 1) # Simplification
        }

    def to_dict(self, agent_id: str) -> Dict[str, Any]:
        """Serialize for API responses."""
        credit = self.agent_credit.get(agent_id)
        if not credit:
            return {"error": "No credit data"}
        
        return {
            "score": credit.total_score,
            "rating": credit.rating.value,
            "accounts_count": len(self.agent_accounts.get(agent_id, []))
        }
