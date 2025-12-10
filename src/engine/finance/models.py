
# [ ]↔T: Financial Models - Data Structures
#   - [x] RevenueStream for revenue tracking
#   - [x] Loan for debt obligations  
#   - [x] TaxRecord for tax filing
#   - [x] FinancialReport for P&L statement
#   - [x] FinancialLedger for immutable transaction log
#   - [x] Bill for payment obligations
# PRIORITY: P1 - Core data models
# STATUS: Complete
# ═══════════════════════════════════════════════════════════════════════

"""
Financial Data Models

Core data structures for the finance package:
- RevenueStream: Revenue tracking per service
- Loan: Debt obligations
- TaxRecord: Tax filing records
- FinancialReport: Weekly P&L statement
- FinancialLedger: Immutable transaction log (event repository)
- Bill: Pending payment obligations

NOTE: Credit-related classes (CreditScore, CreditAccount, etc.) are in credit.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


# ═══════════════════════════════════════════════════════════════════════
# REVENUE & BUSINESS MODELS
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class RevenueStream:
    """
    Represents a revenue stream for the laundromat.
    
    Categories: wash, dry, bundle, vending, premium, loyalty, ancillary, custom
    """
    name: str
    category: str
    price: float
    cost_per_unit: float = 0.0
    demand_multiplier: float = 1.0
    unlocked: bool = False
    description: str = ""
    weekly_revenue: float = 0.0


@dataclass
class Loan:
    """
    Represents an active loan obligation.
    """
    name: str
    principal: float
    balance: float
    interest_rate_monthly: float
    term_weeks: int
    weeks_remaining: int
    weekly_payment: float
    is_defaulted: bool = False
    missed_payments: int = 0


@dataclass
class TaxRecord:
    """
    Stores tax filing information for a fiscal quarter.
    """
    quarter: int
    gross_revenue: float = 0.0
    deductible_expenses: float = 0.0
    net_profit: float = 0.0
    tax_owed: float = 0.0
    tax_paid: float = 0.0
    is_filed: bool = False
    due_week: int = 0
    is_overdue: bool = False


@dataclass
class TaxFilingStatus:
    """Tracks quarterly tax filing status."""
    quarter: int
    due_week: int
    gross_revenue: float = 0.0
    deductible_expenses: float = 0.0
    net_profit: float = 0.0
    tax_owed: float = 0.0
    tax_paid: float = 0.0
    is_filed: bool = False
    is_overdue: bool = False


# ═══════════════════════════════════════════════════════════════════════
# FINANCIAL REPORT (Weekly P&L)
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class FinancialReport:
    """
    Weekly Profit & Loss statement data per World Bible 2.3.5.
    """
    week: int
    # Revenue
    revenue_wash: float = 0.0
    revenue_dry: float = 0.0
    revenue_vending: float = 0.0
    revenue_premium: float = 0.0
    revenue_membership: float = 0.0
    revenue_other: float = 0.0
    total_revenue: float = 0.0
    
    # COGS
    cogs_supplies: float = 0.0
    cogs_vending: float = 0.0
    total_cogs: float = 0.0
    
    # Gross Profit
    gross_profit: float = 0.0
    
    # Operating Expenses
    expense_rent: float = 0.0
    expense_utilities: float = 0.0
    expense_labor: float = 0.0
    expense_maintenance: float = 0.0
    expense_marketing: float = 0.0
    expense_insurance: float = 0.0
    expense_other: float = 0.0
    total_operating_expenses: float = 0.0
    
    # Operating Income
    operating_income: float = 0.0
    
    # Other
    income_interest: float = 0.0
    expense_interest: float = 0.0
    fines: float = 0.0
    
    # Net
    net_income_before_tax: float = 0.0
    tax_provision: float = 0.0
    net_income: float = 0.0
    
    # Cash Flow
    cash_beginning: float = 0.0
    cash_ending: float = 0.0


# ═══════════════════════════════════════════════════════════════════════
# LEDGER SYSTEM (Immutable Event Repository)
# ═══════════════════════════════════════════════════════════════════════

class TransactionCategory(Enum):
    """Categories for ledger transactions."""
    REVENUE = "revenue"
    EXPENSE = "expense"
    LOAN = "loan"           # Loan principal received
    REPAYMENT = "repayment"
    TAX = "tax"
    ADJUSTMENT = "adjustment"
    GRANT = "grant"
    CAPITAL = "capital"     # Initial capital
    TRANSFER = "transfer"
    REAL_ESTATE = "real_estate"


@dataclass
class Transaction:
    """
    Immutable ledger entry representing a financial event.
    """
    amount: float
    category: TransactionCategory
    description: str
    week: int
    related_entity_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FinancialLedger:
    """
    Immutable ledger of financial events (event repository pattern).
    Each laundromat has its own ledger.
    """
    transactions: List[Transaction] = field(default_factory=list)
    
    def add(
        self, 
        amount: float, 
        category: str, 
        description: str, 
        week: int, 
        related_entity_id: str = None
    ) -> Transaction:
        """Record a financial event (append-only)."""
        try:
            cat = TransactionCategory(category.lower()) if isinstance(category, str) else category
        except ValueError:
            cat = TransactionCategory.ADJUSTMENT
             
        tx = Transaction(
            amount=amount,
            category=cat,
            description=description,
            week=week,
            related_entity_id=related_entity_id
        )
        self.transactions.append(tx)
        return tx
    
    @property
    def balance(self) -> float:
        """Calculate current balance from all transactions."""
        return sum(t.amount for t in self.transactions)

    def get_history(self) -> List[Transaction]:
        """Get sorted list of transactions."""
        return sorted(self.transactions, key=lambda x: x.timestamp)


# ═══════════════════════════════════════════════════════════════════════
# BILL SYSTEM (Payment Obligations)
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Bill:
    """
    Represents a financial obligation (rent, utilities, loan payment, tax).
    Bills are generated weekly and must be paid manually by the player.
    """
    id: str
    name: str
    amount: float
    due_week: int
    category: str  # rent, utilities, loan_repayment, tax
    recipient_id: str = "system"
    is_paid: bool = False
    generated_week: int = 0
    penalty_applied: bool = False


# ═══════════════════════════════════════════════════════════════════════
# CREDIT & LOAN MODELS
# ═══════════════════════════════════════════════════════════════════════

class PaymentStatus(Enum):
    """Status of a payment."""
    ON_TIME = "on_time"
    LATE_30 = "late_30"      # 30 days late
    LATE_60 = "late_60"      # 60 days late
    LATE_90 = "late_90"      # 90+ days late
    MISSED = "missed"
    SCHEDULED = "scheduled"


class CreditRating(Enum):
    """Credit rating tiers."""
    EXCEPTIONAL = "exceptional"  # 800-850
    VERY_GOOD = "very_good"      # 740-799
    GOOD = "good"                # 670-739
    FAIR = "fair"                # 580-669
    POOR = "poor"                # 300-579


@dataclass
class PaymentRecord:
    """Record of a single payment."""
    id: str
    loan_id: str
    amount_due: float
    amount_paid: float
    due_week: int
    paid_week: Optional[int]
    status: PaymentStatus
    
    @property
    def is_paid(self) -> bool:
        return self.status in [PaymentStatus.ON_TIME, PaymentStatus.LATE_30]
    
    @property
    def days_late(self) -> int:
        if self.paid_week is None:
            return 999  # Unpaid
        weeks_late = self.paid_week - self.due_week
        return max(0, weeks_late * 7)


@dataclass
class CreditAccount:
    """A credit account (loan, line of credit, etc.)."""
    id: str
    account_type: str  # sba_loan, equipment_loan, credit_line, vendor_credit
    original_amount: float
    current_balance: float
    credit_limit: float  # For credit lines
    interest_rate: float
    weekly_payment: float
    opened_week: int
    term_weeks: int
    payments: List[PaymentRecord] = field(default_factory=list)
    is_active: bool = True
    is_defaulted: bool = False


@dataclass
class CreditScore:
    """
    Credit score calculation following FICO-like methodology.
    Score Range: 300-850
    """
    # Component scores (0-100 each)
    payment_history_score: float = 70.0
    utilization_score: float = 80.0
    history_length_score: float = 50.0
    credit_mix_score: float = 60.0
    new_credit_score: float = 70.0
    
    # Weights (FICO standard)
    WEIGHTS = {
        "payment_history": 0.35,
        "utilization": 0.30,
        "history_length": 0.15,
        "credit_mix": 0.10,
        "new_credit": 0.10
    }
    
    @property
    def total_score(self) -> int:
        """Calculate the overall credit score (300-850 range)."""
        weighted_score = (
            self.payment_history_score * self.WEIGHTS["payment_history"] +
            self.utilization_score * self.WEIGHTS["utilization"] +
            self.history_length_score * self.WEIGHTS["history_length"] +
            self.credit_mix_score * self.WEIGHTS["credit_mix"] +
            self.new_credit_score * self.WEIGHTS["new_credit"]
        )
        # Map 0-100 to 300-850
        return int(300 + (weighted_score / 100) * 550)
    
    @property
    def rating(self) -> CreditRating:
        """Get the credit rating tier."""
        score = self.total_score
        if score >= 800:
            return CreditRating.EXCEPTIONAL
        elif score >= 740:
            return CreditRating.VERY_GOOD
        elif score >= 670:
            return CreditRating.GOOD
        elif score >= 580:
            return CreditRating.FAIR
        else:
            return CreditRating.POOR
