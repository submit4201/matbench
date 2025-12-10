import logging
import json
from typing import Dict, Any, List, Optional
from src.world.laundromat import LaundromatState

logger = logging.getLogger(__name__)

class MetricsAuditor:
    """
    Centralized auditor for capturing, logging, and exporting simulation telemetry.
    Designed to bridge the gap between internal game state and external observability tools (logging, New Relic, etc).
    """
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.enabled = True

    def record_weekly_state(self, week: int, states: Dict[str, LaundromatState]):
        """
        Snapshot the state of all agents at the end of a week.
        """
        if not self.enabled: return

        for agent_id, state in states.items():
            try:
                metrics = self._extract_metrics(week, agent_id, state)
                self._log_metrics(metrics)
                self.history.append(metrics)
            except Exception as e:
                logger.error(f"Failed to record metrics for {agent_id} week {week}: {e}")

    def _extract_metrics(self, week: int, agent_id: str, state: LaundromatState) -> Dict[str, Any]:
        """
        Extracts a flat dictionary of key metrics from the complex state object.
        """
        # Financials (get latest report if available)
        revenue = 0.0
        expenses = 0.0
        net_income = 0.0
        
        if state.financial_reports:
            last_report = state.financial_reports[-1]
            if last_report.week == week:
                revenue = last_report.total_revenue
                expenses = last_report.total_operating_expenses + last_report.total_cogs
                net_income = last_report.net_income
        
        # Social
        social_total = state.social_score.total_score if hasattr(state.social_score, "total_score") else 50.0
        try:
            tier = state.social_score.tier.value
        except:
            tier = "Unknown"

        return {
            "event_type": "WeeklySnapshot",
            "week": week,
            "agent_id": agent_id,
            "agent_name": state.name,
            
            # Key performance indicators
            "cash_balance": round(state.balance, 2),
            "net_worth": round(state.balance + self._calculate_assets(state), 2),
            "weekly_revenue": round(revenue, 2),
            "weekly_expenses": round(expenses, 2),
            "weekly_net_income": round(net_income, 2),
            
            # Operational
            "customer_count": getattr(state, "active_customers", 0),
            "machines_total": len(state.machines),
            "machines_broken": sum(1 for m in state.machines if m.is_broken),
            
            # Social
            "social_score_total": round(social_total, 1),
            "social_tier": tier,
            "reputation": round(state.reputation, 1),
            
            # Inventory
            "inv_detergent": state.inventory.get("detergent", 0),
            "inv_softener": state.inventory.get("softener", 0),
            "inv_parts": state.inventory.get("parts", 0),
        }

    def _calculate_assets(self, state: LaundromatState) -> float:
        # Simplified asset valuation
        machine_value = len(state.machines) * 500.0 # Depreciated value assumption
        return machine_value

    def _log_metrics(self, metrics: Dict[str, Any]):
        """
        Writes metrics to logger in JSON format for easy parsing (e.g. by Splunk/ELK/CloudWatch).
        Also hooks into New Relic if available.
        """
        # 1. Structured Logging
        logger.info(f"METRIC_EVENT: {json.dumps(metrics)}")

        # 2. New Relic Integration (Placeholder/Check)
        try:
            import newrelic.agent
            newrelic.agent.record_custom_event(metrics["event_type"], metrics)
        except ImportError:
            pass
        except Exception as e:
            # Don't crash game for metrics
            pass
