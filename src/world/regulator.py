from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Regulation:
    name: str
    description: str
    penalty_amount: float
    social_score_penalty: float
    duration_weeks: int

class RegulatoryBody:
    """
    Enforces antitrust laws and fair competition rules.
    Monitors market share, pricing behavior, and collusion.
    """
    def __init__(self):
        self.regulations = {
            "PRICE_FIXING": Regulation(
                "Price Fixing", 
                "Colluding to set prices", 
                1000.0, 
                12.0, 
                16
            ),
            "PREDATORY_PRICING": Regulation(
                "Predatory Pricing", 
                "Pricing below cost to eliminate competition", 
                500.0, 
                6.0, 
                8
            ),
            "MONOPOLY_ABUSE": Regulation(
                "Monopoly Abuse", 
                "Abusing dominant market position", 
                500.0, 
                10.0, 
                8
            )
        }
        self.active_investigations: Dict[str, Any] = {} # agent_id -> investigation details

    def check_for_violations(self, gamestate: Any) -> List[Dict[str, Any]]:
        """
        Checks the current game state for any regulatory violations.
        Returns a list of violation events/notifications.
        """
        violations = []
        
        # 1. Check Market Concentration
        violations.extend(self._check_market_concentration(gamestate))
        
        # 2. Check Price Fixing (Parallel Pricing)
        violations.extend(self._check_price_fixing(gamestate))
        
        # 3. Check Predatory Pricing
        violations.extend(self._check_predatory_pricing(gamestate))
        
        return violations

    def _check_market_concentration(self, gamestate: Any) -> List[Dict[str, Any]]:
        """
        Monitors market share thresholds.
        """
        violations = []
        total_revenue = sum(state.history["revenue"][-1] for state in gamestate.states.values() if state.history["revenue"])
        
        if total_revenue == 0:
            return []

        for agent_id, state in gamestate.states.items():
            if not state.history["revenue"]:
                continue
                
            revenue = state.history["revenue"][-1]
            market_share = revenue / total_revenue
            
            if market_share > 0.50:
                violations.append({
                    "type": "MARKET_CONCENTRATION",
                    "agent_id": agent_id,
                    "severity": "CRITICAL",
                    "message": f"Monopoly Alert: {state.name} holds {market_share:.1%} of the market. Forced divestiture warning."
                })
            elif market_share > 0.40:
                violations.append({
                    "type": "MARKET_CONCENTRATION",
                    "agent_id": agent_id,
                    "severity": "WARNING",
                    "message": f"Dominance Warning: {state.name} holds {market_share:.1%} of the market. Fines possible."
                })
                
        return violations

    def _check_price_fixing(self, gamestate: Any) -> List[Dict[str, Any]]:
        """
        Detects if multiple agents have identical prices significantly above average
        or if they move prices in lockstep.
        """
        violations = []
        prices = {agent_id: state.price for agent_id, state in gamestate.states.items()}
        
        # Simple detection: If > 2 agents have EXACT same price and it's > $5.00
        price_counts = {}
        for p in prices.values():
            price_counts[p] = price_counts.get(p, 0) + 1
            
        suspicious_prices = [p for p, count in price_counts.items() if count >= 2 and p > 6.00]
        
        for p in suspicious_prices:
            suspects = [aid for aid, price in prices.items() if price == p]
            # In a real simulation, we'd check communication logs here
            # For now, just issue a warning if it persists (simulated by random chance)
            import random
            if random.random() < 0.3: # 30% detection chance as per Bible
                for agent_id in suspects:
                    violations.append({
                        "type": "PRICE_FIXING",
                        "agent_id": agent_id,
                        "regulation": self.regulations["PRICE_FIXING"],
                        "message": "Regulatory Inquiry: Suspicious parallel pricing detected."
                    })
        
        return violations

    def _check_predatory_pricing(self, gamestate: Any) -> List[Dict[str, Any]]:
        """
        Checks if price is below estimated variable cost.
        """
        violations = []
        ESTIMATED_VARIABLE_COST = 2.00 # Soap + Water + Electricity per load
        
        for agent_id, state in gamestate.states.items():
            if state.price < ESTIMATED_VARIABLE_COST:
                # Check if this has persisted (would need history, simplified here)
                violations.append({
                    "type": "PREDATORY_PRICING",
                    "agent_id": agent_id,
                    "regulation": self.regulations["PREDATORY_PRICING"],
                    "message": "Predatory Pricing Alert: Prices set below variable cost."
                })
                
        return violations

    def enforce_action(self, gamestate: Any, violation: Dict[str, Any]):
        """
        Applies penalties for a confirmed violation.
        """
        agent_id = violation["agent_id"]
        state = gamestate.states[agent_id]
        
        if "regulation" in violation:
            reg = violation["regulation"]
            state.balance -= reg.penalty_amount
            state.update_social_score(-reg.social_score_penalty)
            logger.info(f"Applied penalty to {agent_id}: -${reg.penalty_amount}, -{reg.social_score_penalty} Social Score")
