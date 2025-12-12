from datetime import date
from typing import Optional, List

from pydantic import Field

from .core import GameEvent


# --- Transaction Events ---

class DailyRevenueProcessed(GameEvent):
    """Daily revenue processing event."""
    type: str = "DAILY_REVENUE_PROCESSED"
    revenue_wash: float = Field(ge=0)
    revenue_dry: float = Field(ge=0)
    revenue_vending: float = Field(ge=0) # Total vending (kept for total calc)
    revenue_soap: float = Field(default=0.0, ge=0)
    revenue_sheets: float = Field(default=0.0, ge=0)
    customer_count: int = Field(ge=0)
    utility_cost: float = Field(default=0.0, ge=0)
    supply_cost: float = Field(default=0.0, ge=0)

class FundsTransferred(GameEvent):
    """The atom of the financial system."""
    type: str = "FUNDS_TRANSFERRED"
    transaction_id: str
    amount: float
    category: str
    description: str
    related_entity_id: Optional[str] = None


class BalanceAdjusted(GameEvent):
    """For manual corrections or god-mode edits."""
    type: str = "BALANCE_ADJUSTED"
    adjustment_amount: float
    reason: str


class BillGenerated(GameEvent):
    """Event for when a bill is generated (liability created)."""
    type: str = "BILL_GENERATED"
    bill_id: str
    bill_type: str  # Rent, Labor, Utility
    amount: float = Field(ge=0)
    due_week: int
    due_date: Optional[date] = None # Keeping for compatibility if needed, but CSV says due_week


class BillPaid(GameEvent):
    """Event for when a bill is paid (liability resolved)."""
    type: str = "BILL_PAID"
    bill_id: str
    amount_paid: float = Field(ge=0)
    payment_week: int
    was_late: bool


class BillIgnored(GameEvent):
    """Event for when a bill is ignored/unpaid past due."""
    type: str = "BILL_IGNORED"
    bill_id: str
    ignored_week: int


# --- Tax Events ---

class TaxAssessed(GameEvent):
    """Event for quarterly tax assessment."""
    type: str = "TAX_ASSESSED"
    quarter: int
    gross_revenue: float
    deductible_expenses: float
    net_profit: float
    tax_amount: float
    credits_applied: float


class TaxFilingStatusChanged(GameEvent):
    """Event for tax filing status changes."""
    type: str = "TAX_FILING_STATUS_CHANGED"
    quarter: int
    status: str  # Filed, Overdue
    filing_week: int


class TaxPenaltyApplied(GameEvent):
    """Event for tax penalties."""
    type: str = "TAX_PENALTY_APPLIED"
    bill_id: str
    penalty_amount: float
    reason: str


class FiscalQuarterEnded(GameEvent):
    """Event for end of fiscal quarter."""
    type: str = "FISCAL_QUARTER_ENDED"
    quarter: int


# --- Loan & Banking Events ---

class BankInitialized(GameEvent):
    """Event for initial bank state."""
    type: str = "BANK_INITIALIZED"
    starting_balance: float
    interest_rates: float


class LoanOriginated(GameEvent):
    """Event for new loan creation."""
    type: str = "LOAN_ORIGINATED"
    loan_id: str
    principal: float
    interest_rate: float
    term_weeks: int
    weekly_payment: float


class LoanPaymentProcessed(GameEvent):
    """Event for loan payment processing."""
    type: str = "LOAN_PAYMENT_PROCESSED"
    loan_id: str
    payment_amount: float
    principal_portion: float
    interest_portion: float
    remaining_balance: float


class LoanDefaulted(GameEvent):
    """Event for loan default."""
    type: str = "LOAN_DEFAULTED"
    loan_id: str
    week_of_default: int


class CreditScoreUpdated(GameEvent):
    """Event for credit score updates."""
    type: str = "CREDIT_SCORE_UPDATED"
    new_score: int
    rating_tier: str
    change_delta: int


# --- Real Estate Events ---

class RealEstateMarketRefreshed(GameEvent):
    """Event for new real estate listings."""
    type: str = "REAL_ESTATE_MARKET_REFRESHED"
    new_listings: List[dict] # Storing as dicts for immutable event payload simplicity, represents Building objects


class BuildingPurchased(GameEvent):
    """Event for building purchase."""
    type: str = "BUILDING_PURCHASED"
    building_id: str
    price: float
    location_multiplier: float


class BuildingSold(GameEvent):
    """Event for building sale."""
    type: str = "BUILDING_SOLD"
    building_id: str
    sale_price: float


class RentPaid(GameEvent):
    """Event for rent payment specific to a building."""
    type: str = "RENT_PAID"
    building_id: str
    amount: float
