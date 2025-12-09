
from typing import Dict, List, Any, Optional, TYPE_CHECKING
import logging
from .models import TransactionCategory, Bill, TaxRecord, TaxFilingStatus

if TYPE_CHECKING:
    from src.world.laundromat import LaundromatState

logger = logging.getLogger(__name__)

class TaxSystem:
    """
    Manages tax calculation, filing, and enforcement.
    """
    TAX_RATE = 0.08
    TAX_DUE_WEEKS = [6, 12, 18, 24]
    LATE_TAX_PENALTY_RATE = 0.05
    LATE_TAX_FEE = 50.0
    SMALL_BUSINESS_DEDUCTION = 500.0

    def __init__(self):
        self.pending_filings: Dict[str, TaxFilingStatus] = {}

    def is_tax_due(self, current_week: int) -> bool:
        return current_week in self.TAX_DUE_WEEKS

    def get_quarter(self, current_week: int) -> int:
        if current_week <= 6: return 1
        if current_week <= 12: return 2
        if current_week <= 18: return 3
        return 4

    def calculate_quarterly_tax(self, state: 'LaundromatState', quarter: int) -> Dict[str, float]:
        """
        Calculate taxes based on ledger.
        """
        # Simplification: summing all revenue/expenses in ledger
        # In a real scenario, we'd filter by week range for the quarter
        gross_revenue = sum(
            t.amount for t in state.ledger.transactions 
            if t.category == TransactionCategory.REVENUE
        )
        
        expenses = abs(sum(
            t.amount for t in state.ledger.transactions 
            if t.category == TransactionCategory.EXPENSE
        ))
        
        net_profit = gross_revenue - expenses
        taxable_income = max(0, net_profit - self.SMALL_BUSINESS_DEDUCTION)
        
        # Calculate credits (Machine value + Donations + Employees)
        credits = self._calculate_tax_credits(state)
        
        tax_before_credits = taxable_income * self.TAX_RATE
        tax_owed = max(0, tax_before_credits - credits)
        
        return {
            "quarter": quarter,
            "gross_revenue": gross_revenue,
            "deductible_expenses": expenses,
            "net_profit": net_profit,
            "taxable_income": taxable_income,
            "tax_owed": round(tax_owed, 2),
            "credits": round(credits, 2)
        }

    def generate_tax_bill(self, state: 'LaundromatState', current_week: int) -> Optional[Bill]:
        if not self.is_tax_due(current_week):
            return None
            
        quarter = self.get_quarter(current_week)
        tax_info = self.calculate_quarterly_tax(state, quarter)
        
        if tax_info['tax_owed'] <= 0:
            return None
            
        bill = Bill(
            id=f"tax_q{quarter}_{current_week}_{state.id}",
            name=f"Q{quarter} Business Tax",
            amount=tax_info['tax_owed'],
            due_week=current_week + 2,
            category="tax",
            recipient_id="irs",
            generated_week=current_week
        )
        
        # Track filing status
        self.pending_filings[f"{state.id}_q{quarter}"] = TaxFilingStatus(
            quarter=quarter,
            due_week=current_week + 2,
            gross_revenue=tax_info['gross_revenue'],
            deductible_expenses=tax_info['deductible_expenses'],
            net_profit=tax_info['net_profit'],
            tax_owed=tax_info['tax_owed']
        )
        
        return bill

    def _calculate_tax_credits(self, state: 'LaundromatState') -> float:
        credits = 0.0
        
        # Green Equipment (10% value of eco machines)
        eco_value = sum(500.0 for m in state.machines if getattr(m, 'is_eco', False))
        credits += eco_value * 0.10
        
        # Job Creation ($100 per employee)
        credits += len(state.staff) * 100.0
        
        # Donations (5% of donations - simplistic scan)
        donations = sum(
            abs(t.amount) for t in state.ledger.transactions 
            if "donation" in t.description.lower()
        )
        credits += donations * 0.05
        
        return credits

    def check_overdue_taxes(self, state: 'LaundromatState', current_week: int) -> List[Bill]:
        """Apply penalties to overdue tax bills."""
        updated_bills = []
        for bill in state.bills:
            if bill.category == "tax" and not bill.is_paid:
                if current_week > bill.due_week and not bill.penalty_applied:
                    penalty = bill.amount * self.LATE_TAX_PENALTY_RATE + self.LATE_TAX_FEE
                    bill.amount += penalty
                    bill.penalty_applied = True
                    updated_bills.append(bill)
        return updated_bills
