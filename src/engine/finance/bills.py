
from typing import List, Optional, TYPE_CHECKING
import logging
from .models import Bill, FinancialReport, TransactionCategory

if TYPE_CHECKING:
    from src.world.laundromat import LaundromatState

logger = logging.getLogger(__name__)

class BillSystem:
    """
    Manages bill generation and payment processing.
    """
    
    def generate_operating_bills(
        self, 
        state: 'LaundromatState', 
        report: FinancialReport, 
        current_week: int
    ) -> List[Bill]:
        """
        Generate bills for operating expenses (rent, utilities, labor, etc).
        """
        bills = []
        due_week = current_week + 1
        
        if report.expense_rent > 0:
            bills.append(Bill(
                id=f"rent_{current_week}_{state.id}",
                name="Weekly Rent",
                amount=report.expense_rent,
                due_week=due_week,
                category="rent",
                recipient_id="landlord",
                generated_week=current_week
            ))
            
        if report.expense_utilities > 0:
            bills.append(Bill(
                id=f"utilities_{current_week}_{state.id}",
                name="Utilities",
                amount=report.expense_utilities,
                due_week=due_week,
                category="utilities",
                recipient_id="utility_company",
                generated_week=current_week
            ))
            
        if report.expense_labor > 0:
            bills.append(Bill(
                id=f"labor_{current_week}_{state.id}",
                name="Payroll",
                amount=report.expense_labor,
                due_week=due_week,
                category="labor",
                recipient_id="employees",
                generated_week=current_week
            ))
            
        logger.debug(f"Generated {len(bills)} operating bills for {state.id}, week {current_week}")
        return bills

    def pay_bill(self, state: 'LaundromatState', bill_id: str, current_week: int) -> bool:
        """
        Process generic bill payment.
        Returns True if successful.
        Note: Specific logic for Loans/Tax should be handled by their respective systems *after* this generic check?
        Or this system handles the money movement and delegates the side effects?
        
        Let's keep money movement here.
        """
        bill = next((b for b in state.bills if b.id == bill_id), None)
        
        if not bill:
            logger.error(f"Bill {bill_id} not found")
            return False
            
        if bill.is_paid:
            return False
            
        if state.balance < bill.amount:
            return False
        
        # Determine category
        category = "expense"
        if bill.category == "loan_repayment":
            category = "repayment"
        elif bill.category == "tax":
            category = "tax"
            
        # Record in ledger
        state.ledger.add(
            amount=-bill.amount,
            category=category,
            description=f"Paid: {bill.name}",
            week=current_week,
            related_entity_id=bill.id
        )
        
        # Mark as paid
        bill.is_paid = True
        
        return True
