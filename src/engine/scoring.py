from typing import List, Dict
from src.world.laundromat import LaundromatState

class ScoringSystem:
    @staticmethod
    def calculate_final_scores(laundromats: List[LaundromatState], total_visits_map: Dict[str, int]) -> Dict[str, float]:
        """
        Final score = 
        30% Net Profit (Normalized)
        25% Social Score (Normalized)
        20% Customer Loyalty (Not fully tracked yet, using Visits as proxy for Market Share/Loyalty mix)
        15% Market Share
        10% Adaptability (Placeholder)
        """
        scores = {}
        
        # 1. Normalize Profit
        max_balance = max([l.balance for l in laundromats])
        min_balance = min([l.balance for l in laundromats])
        balance_range = max_balance - min_balance if max_balance != min_balance else 1.0
        
        # 2. Calculate Total Market Visits
        total_market_visits = sum(total_visits_map.values())
        if total_market_visits == 0: total_market_visits = 1
        
        for l in laundromats:
            # Profit Score (0-100)
            profit_score = ((l.balance - min_balance) / balance_range) * 100
            
            # Social Score (0-100)
            social_score = l.social_score.total_score
            
            # Market Share Score (0-100)
            market_share = (total_visits_map.get(l.id, 0) / total_market_visits) * 100
            
            # Weighted Sum
            # 30% Profit + 25% Social + 15% Market Share + ...
            # We'll simplify the user's formula slightly for now
            final_score = (profit_score * 0.30) + (social_score * 0.25) + (market_share * 0.35) + 10 # Base 10 for adaptability
            
            scores[l.id] = {
                "total": round(final_score, 2),
                "profit_score": round(profit_score, 2),
                "social_score": round(social_score, 2),
                "market_share": round(market_share, 2)
            }
            
        return scores
