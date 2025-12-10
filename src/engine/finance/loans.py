
from typing import Dict, List, Any, Optional
import uuid
import logging
from .models import CreditAccount, PaymentRecord, PaymentStatus

logger = logging.getLogger(__name__)

class LoanSystem:
    """
    Manages loan lifecycles: origination, interest, payments.
    """
    
    def create_loan(
        self, 
        loan_type: str, 
        amount: float, 
        interest_rate: float, 
        term_weeks: int,
        current_week: int
    ) -> CreditAccount:
        """Factory method to create a new loan account."""
        weekly_rate = interest_rate / 52
        # Amortization calculation
        if weekly_rate == 0:
            payment = amount / term_weeks
        else:
            payment = amount * (weekly_rate * (1 + weekly_rate)**term_weeks) / ((1 + weekly_rate)**term_weeks - 1)
            
        loan = CreditAccount(
            id=str(uuid.uuid4())[:8],
            account_type=loan_type,
            original_amount=amount,
            current_balance=amount,
            credit_limit=amount,
            interest_rate=interest_rate,
            weekly_payment=round(payment, 2),
            opened_week=current_week,
            term_weeks=term_weeks
        )
        return loan

    def schedule_payments(self, loan: CreditAccount) -> List[PaymentRecord]:
        """Generate payment schedule for a loan."""
        payments = []
        for week_offset in range(1, loan.term_weeks + 1):
            due_week = loan.opened_week + week_offset
            payments.append(PaymentRecord(
                id=str(uuid.uuid4())[:8],
                loan_id=loan.id,
                amount_due=loan.weekly_payment,
                amount_paid=0.0,
                due_week=due_week,
                paid_week=None,
                status=PaymentStatus.SCHEDULED
            ))
        return payments

    def process_payment(self, loan: CreditAccount, amount: float) -> float:
        """
        Apply payment to loan balance.
        Returns the new balance.
        """
        # Simple interest/principal split approximation for game logic
        # Assuming fixed payment, we just reduce balance. 
        # Detailed amortization could go here.
        
        # If paying full weekly amount, assume mostly principal reduction after interest
        # This mirrors the logic removed from credit.py
        principal_portion = amount * 0.85 # Simplified assumption
        
        loan.current_balance = max(0, loan.current_balance - principal_portion)
        
        if loan.current_balance <= 0:
            loan.is_active = False
            
        return loan.current_balance
