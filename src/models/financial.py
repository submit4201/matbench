from typing import List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid
from pydantic import Field
from src.models.base import GameModel

# Enums
class TransactionCategory(str, Enum):
    """Categories for ledger transactions."""
    REVENUE = "revenue"
    EXPENSE = "expense"
    LOAN = "loan"
    REPAYMENT = "repayment"
    TAX = "tax"
    ADJUSTMENT = "adjustment"
    GRANT = "grant"
    CAPITAL = "capital"
    TRANSFER = "transfer"
    REAL_ESTATE = "real_estate"

class CreditRating(str, Enum):
    EXCEPTIONAL = "exceptional"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class PaymentStatus(str, Enum):
    ON_TIME = "on_time"
    LATE_30 = "late_30"
    LATE_60 = "late_60"
    LATE_90 = "late_90"
    MISSED = "missed"
    SCHEDULED = "scheduled"

# Models
class RevenueStream(GameModel):
    name: str
    category: str
    price: float
    cost_per_unit: float = 0.0
    demand_multiplier: float = 1.0
    unlocked: bool = False
    description: str = ""
    weekly_revenue: float = 0.0

class Transaction(GameModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    amount: float
    category: TransactionCategory
    description: str
    week: int
    related_entity_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class FinancialLedger(GameModel):
    transactions: List[Transaction] = Field(default_factory=list)

    @property
    def balance(self) -> float:
        return sum(t.amount for t in self.transactions)

    def add(self, amount: float, category: TransactionCategory, description: str, week: int, related_entity_id: Optional[str] = None) -> Transaction:
        tx = Transaction(
            amount=amount,
            category=category,
            description=description,
            week=week,
            related_entity_id=related_entity_id
        )
        self.transactions.append(tx)
        return tx

class Bill(GameModel):
    id: str
    name: str
    amount: float
    due_week: int
    category: str
    recipient_id: str = "system"
    is_paid: bool = False
    generated_week: int = 0
    penalty_applied: bool = False

class TaxRecord(GameModel):
    """Stores tax filing information for a fiscal quarter."""
    quarter: int
    gross_revenue: float = 0.0
    deductible_expenses: float = 0.0
    net_profit: float = 0.0
    tax_owed: float = 0.0
    tax_paid: float = 0.0
    is_filed: bool = False
    due_week: int = 0
    is_overdue: bool = False

class Loan(GameModel):
    name: str
    principal: float
    balance: float
    interest_rate_monthly: float
    term_weeks: int
    weeks_remaining: int
    weekly_payment: float
    is_defaulted: bool = False
    missed_payments: int = 0

class FinancialReport(GameModel):
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
