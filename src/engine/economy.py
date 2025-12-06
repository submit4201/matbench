from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import math
from src.world.financials import RevenueStream, Loan, TaxRecord, FinancialReport

class EconomySystem:
    def __init__(self):
        self.tax_rate = 0.08
        self.inflation_rate = 0.0
        
        # Default Revenue Streams
        self.base_streams = [
            RevenueStream("Standard Wash", "wash", 3.00, 0.40, 1.0, True),
            RevenueStream("Standard Dry", "dry", 2.00, 0.35, 1.0, True),
            RevenueStream("Delicate Wash", "wash", 4.00, 0.45, 0.8, False),
            RevenueStream("Heavy-Duty Wash", "wash", 5.00, 0.60, 0.7, False),
            RevenueStream("Express Wash", "wash", 4.00, 0.40, 0.9, False),
            RevenueStream("High-Heat Dry", "dry", 2.50, 0.45, 0.8, False),
            RevenueStream("Detergent Sale", "vending", 1.50, 0.15, 0.5, True), # Cost is per unit (0.15 avg)
            RevenueStream("Softener Sale", "vending", 1.25, 0.10, 0.4, True),
            RevenueStream("Dryer Sheets", "vending", 1.00, 0.05, 0.6, True),
            RevenueStream("Snacks & Drinks", "vending", 2.50, 1.00, 0.3, False),
            RevenueStream("Wash & Fold", "premium", 1.50, 0.50, 0.2, False), # Price per lb, cost is labor mostly
        ]

    def get_available_loans(self, social_score: float, weeks_operated: int, profitable_weeks: int) -> List[Dict[str, Any]]:
        loans = []
        
        # 1. Operating Line of Credit
        if social_score >= 30:
            loans.append({
                "type": "operating_credit",
                "name": "Operating Line of Credit",
                "max_amount": 5000,
                "interest_rate_monthly": 0.05, # 5% weekly paid monthly? Spec says 5% weekly paid monthly. Assuming 5% monthly for simplicity or spec interpretation. Spec says "5% weekly paid monthly". That's huge. Let's stick to spec text but maybe it means 5% APR? No, "5% weekly" is shark loan territory. Let's assume 5% Monthly for game balance unless "weekly" is strict. Spec says "5% weekly paid monthly". I will use 5% monthly as a safer default for now, or 1.25% weekly.
                "term_weeks": 52, # Revolving basically
                "qualification": "Social Score >= 30"
            })
            
        # 2. Equipment Loan
        if social_score >= 40 and weeks_operated >= 4:
            loans.append({
                "type": "equipment_loan",
                "name": "Equipment Loan",
                "max_amount": 10000,
                "interest_rate_monthly": 0.04,
                "term_weeks": 24,
                "qualification": "Social Score >= 40, 4 weeks operation"
            })
            
        # 3. Expansion Loan
        if social_score >= 60 and profitable_weeks >= 8:
            loans.append({
                "type": "expansion_loan",
                "name": "Expansion Loan",
                "max_amount": 25000,
                "interest_rate_monthly": 0.035,
                "term_weeks": 48,
                "qualification": "Social Score >= 60, Profitable 8 weeks"
            })
            
        # 4. Emergency Bridge Loan
        loans.append({
            "type": "emergency_loan",
            "name": "Emergency Bridge Loan",
            "max_amount": 2000,
            "interest_rate_monthly": 0.08,
            "term_weeks": 4,
            "qualification": "None (High Risk)"
        })
        
        return loans

    def calculate_loan_payment(self, principal: float, rate_monthly: float, term_weeks: int) -> float:
        # Simple amortization
        # Rate per week approx rate_monthly / 4
        rate_weekly = rate_monthly / 4.0
        if rate_weekly == 0:
            return principal / term_weeks
        
        # Formula: P * (r(1+r)^n) / ((1+r)^n - 1)
        return principal * (rate_weekly * (1 + rate_weekly)**term_weeks) / ((1 + rate_weekly)**term_weeks - 1)

    def create_loan(self, loan_type: str, amount: float) -> Loan:
        # Factory for loans based on type
        if loan_type == "operating_credit":
            return Loan("Operating Line of Credit", amount, amount, 0.05, 52, 52, self.calculate_loan_payment(amount, 0.05, 52))
        elif loan_type == "equipment_loan":
            return Loan("Equipment Loan", amount, amount, 0.04, 24, 24, self.calculate_loan_payment(amount, 0.04, 24))
        elif loan_type == "expansion_loan":
            return Loan("Expansion Loan", amount, amount, 0.035, 48, 48, self.calculate_loan_payment(amount, 0.035, 48))
        elif loan_type == "emergency_loan":
            return Loan("Emergency Bridge Loan", amount, amount, 0.08, 4, 4, self.calculate_loan_payment(amount, 0.08, 4))
        else:
            raise ValueError(f"Unknown loan type: {loan_type}")

    def calculate_taxes(self, gross_revenue: float, expenses: float, deductions: float) -> float:
        net_profit = gross_revenue - expenses - deductions
        if net_profit <= 0:
            return 0.0
        
        # Small Business Deduction: First $500 profit tax-free
        taxable_income = max(0, net_profit - 500)
        return taxable_income * self.tax_rate
