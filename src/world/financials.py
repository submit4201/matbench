from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class RevenueStream:
    name: str
    category: str  # "wash", "dry", "bundle", "vending", "premium", "loyalty", "ancillary", "custom"
    price: float
    cost_per_unit: float = 0.0
    demand_multiplier: float = 1.0
    unlocked: bool = False
    description: str = ""
    # Track weekly performance
    weekly_revenue: float = 0.0

@dataclass
class Loan:
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
    quarter: int
    gross_revenue: float = 0.0
    deductible_expenses: float = 0.0
    net_profit: float = 0.0
    tax_owed: float = 0.0
    tax_paid: float = 0.0
    is_filed: bool = False
    due_week: int = 0

@dataclass
class FinancialReport:
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
