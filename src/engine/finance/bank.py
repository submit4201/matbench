
from typing import Dict, List, Any, Optional, TYPE_CHECKING
import logging
from .models import FinancialReport, Bill

if TYPE_CHECKING:
    from src.world.laundromat import LaundromatState
from .credit import CreditSystem
from .bills import BillSystem
from .tax import TaxSystem
from .loans import LoanSystem

from .loans import LoanSystem
from src.utils.logger import get_logger

logger = get_logger("src.engine.finance.bank", category="finance")

class BankSystem:
    """
    Central financial authority facade.
    Orchestrates generic bills, taxes, loans, and credit scoring.
    """
    
    def __init__(self, agent_ids: List[str] = None):
        self.credit_system = CreditSystem() # Contains LoanSystem internally or we separate?
        # Current credit.py instantiation we just made *has* LoanSystem inside it.
        # But for clean Bank facade, generic systems below:
        self.bill_system = BillSystem()
        self.tax_system = TaxSystem()
        
    def initialize_agent(self, agent_id: str, starting_week: int = 1) -> Dict[str, Any]:
        """
        Initialize financial systems for an agent.
        """
        credit_info = self.credit_system.initialize_agent(agent_id, starting_week)
        
        logger.info(f"Bank initialized for {agent_id}")
        return {
            **credit_info,
            "tax_rate": self.tax_system.TAX_RATE
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # ORCHESTRATION
    # ═══════════════════════════════════════════════════════════════════

    def process_week(self, state: 'LaundromatState', current_week: int, report: FinancialReport):
        """
        Main weekly processing loop for financial system.
        """
        # 1. Generate Operating Bills (Rent, Utilities, etc.)
        self.generate_operating_bills(state, report, current_week)
        
        # 2. Generate Loan Repayment Bills
        self.generate_loan_bills(state, current_week)
        
        # 3. Tax Enforcement (Quarterly)
        if self.tax_system.is_tax_due(current_week):
            bill = self.generate_tax_bill(state, current_week)
            if bill:
                logger.info(f"Tax bill generated for {state.id}: ${bill.amount:.2f}")
                
        # 4. Check Overdue Taxes (Penalties)
        self.check_overdue_taxes(state, current_week)

    # ═══════════════════════════════════════════════════════════════════
    # DELEGATED METHODS
    # ═══════════════════════════════════════════════════════════════════

    def generate_operating_bills(self, state: 'LaundromatState', report: FinancialReport, current_week: int) -> List[Bill]:
        bills = self.bill_system.generate_operating_bills(state, report, current_week)
        # Add to state is handled inside generators or here?
        # Our new bills.py methods return the list, caller extends state.
        state.bills.extend(bills) 
        return bills

    def generate_loan_bills(self, state: 'LaundromatState', current_week: int) -> List[Bill]:
        # This one is tricky. Loans are in 'state.loans'?
        # In current credit.py refactor, loans are in `credit_system.agent_accounts`.
        # State.loans is likely valid legacy or sync'd copy?
        # The CreditSystem manages the "Bank's view" of loans.
        # We need to generate BILLS for those payments.
        
        # We can ask CreditSystem for due payments
        bills = []
        due_payments = self.credit_system.get_due_payments(state.id, current_week)
        
        for payment in due_payments:
            # Check if bill exists
            bill_id = f"loan_pmt_{payment.id}"
            existing = next((b for b in state.bills if b.id == bill_id), None)
            
            if not existing:
                bill = Bill(
                    id=bill_id,
                    name=f"Loan Payment",
                    amount=payment.amount_due,
                    due_week=payment.due_week,
                    category="loan_repayment",
                    recipient_id=payment.loan_id,
                    generated_week=current_week
                )
                bills.append(bill)
        
        state.bills.extend(bills)
        return bills

    def generate_tax_bill(self, state: 'LaundromatState', current_week: int) -> Optional[Bill]:
        bill = self.tax_system.generate_tax_bill(state, current_week)
        if bill:
            state.bills.append(bill)
        return bill

    def pay_bill(self, state: 'LaundromatState', bill_id: str, current_week: int) -> Dict[str, Any]:
        """
        Process payment via BillSystem, then handle side effects (Loans, Tax).
        """
        bill = next((b for b in state.bills if b.category == "loan_repayment" and b.id == bill_id), None)
        
        # 1. Money Movement
        success = self.bill_system.pay_bill(state, bill_id, current_week)
        if not success:
            return {"success": False, "error": "Payment failed (funding or duplicate)"}
            
        # 2. Side Effects
        # Re-fetch bill because pay_bill might have modified 'is_paid'
        bill = next((b for b in state.bills if b.id == bill_id), None)
        if not bill: return {"success": True} # Should be there
        
        result = {"success": True, "new_balance": state.balance}
        
        if bill.category == "loan_repayment":
            # Recipient ID in bill should match loan_id logic?
            # In generate_loan_bills above, recipient_id was payment.loan_id? 
            # actually it's payment.loan_id. Wait, payment object needed for credit system.
            # Bill ID was f"loan_pmt_{payment.id}".
            # We need to extract payment ID to tell CreditSystem.
            payment_id = bill.id.replace("loan_pmt_", "")
            
            # CreditSystem.make_payment handles balance update + score update
            # But wait, BillSystem already deducted money from ledger/balance.
            # CreditSystem.make_payment *also* decrements balance?
            # No, CreditSystem.make_payment calculates score and updates LOAN balance.
            # It accepts 'amount', but does it touch the 'LaundromatState.balance'? NO.
            # It updates 'agent_accounts' (Bank side).
            # Perfect.
            
            cred_res = self.credit_system.make_payment(state.id, payment_id, bill.amount, current_week)
            result.update(cred_res)
            
        elif bill.category == "tax":
            # Update tax filing status in TaxSystem
            # Need filing key
            filing_key = f"{state.id}_{bill.id.split('_')[1]}" # e.g. "p1_q1"
            # TaxSystem tracks pending filings. We might need a method there 'mark_paid'.
            # For now, simplistic access:
            if filing_key in self.tax_system.pending_filings:
                self.tax_system.pending_filings[filing_key].is_filed = True
        
        return result

    def check_overdue_taxes(self, state: 'LaundromatState', current_week: int):
        return self.tax_system.check_overdue_taxes(state, current_week)

    def to_dict(self, agent_id: str) -> Dict[str, Any]:
        return self.credit_system.to_dict(agent_id)