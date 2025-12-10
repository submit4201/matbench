from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import math
from src.engine.finance.models import RevenueStream, Loan, TaxRecord, FinancialReport

@dataclass
class MarketTrend:
    week: int
    primary_resource: str # e.g., "detergent", "parts"
    price_multiplier: float # 1.2 = 20% higher cost
    demand_shift: float # 1.1 = 10% more customer demand
    news_headline: str

class MarketSystem:
    def __init__(self):
        self.tax_rate = 0.08
        self.inflation_rate = 0.0
        
        # Trends
        self.active_trend: Optional[MarketTrend] = None
        self.history: List[MarketTrend] = []
        
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

    def update_trends(self, current_week: int):
        """Generates or updates market trends."""
        import random
        # 20% chance to change trend each week
        if not self.active_trend or random.random() < 0.2:
            resources = ["detergent", "softener", "parts", "electricity", "water"]
            target = random.choice(resources)
            
            # Fluctuation -0.2 to +0.3
            price_mult = 1.0 + (random.random() * 0.5 - 0.2)
            demand_mult = 1.0 + (random.random() * 0.4 - 0.2)
            
            headlines = {
                "detergent": "Chemical plant strike affects soap prices!",
                "softener": "New eco-regulations impact softener supply.",
                "parts": "Global shipping delays cause shortage of machine parts.",
                "electricity": "Grid instability leads to power rate hikes.",
                "water": "Drought conditions trigger water conservation pricing."
            }
            
            headline = headlines.get(target, f"Market fluctuations observed in {target}.")
            
            self.active_trend = MarketTrend(
                week=current_week,
                primary_resource=target,
                price_multiplier=round(price_mult, 2),
                demand_shift=round(demand_mult, 2),
                news_headline=headline
            )
            self.history.append(self.active_trend)

    def get_market_report(self) -> Dict[str, Any]:
        """Returns a snapshot of the current market state."""
        if not self.active_trend:
            return {"status": "Stable", "headline": "The market is calm."}
            
        return {
            "week": self.active_trend.week,
            "status": "Volatile" if abs(self.active_trend.price_multiplier - 1.0) > 0.1 else "Stable",
            "impact_resource": self.active_trend.primary_resource,
            "price_factor": self.active_trend.price_multiplier,
            "demand_factor": self.active_trend.demand_shift,
            "headline": self.active_trend.news_headline
        }

    def get_available_loans(self, social_score: float, weeks_operated: int, profitable_weeks: int) -> List[Dict[str, Any]]:
        loans = []
        
        # 1. Operating Line of Credit
        if social_score >= 30:
            loans.append({
                "type": "operating_credit",
                "name": "Operating Line of Credit",
                "max_amount": 5000,
                "interest_rate_monthly": 0.05, 
                "term_weeks": 52, 
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
        

