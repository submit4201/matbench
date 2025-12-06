"""
Game History Tracking System

Records all participant turns, thinking, and actions for end-of-game analysis.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class TurnRecord:
    """Record of a single turn for one participant"""
    week: int
    agent_id: str
    agent_name: str
    timestamp: str
    
    # State Before Action
    balance_before: float
    social_score_before: float
    inventory_before: Dict[str, int]
    
    # AI Reasoning (extracted from XML)
    thinking: List[str] = field(default_factory=list)
    
    # Actions Taken
    actions: List[Dict] = field(default_factory=list)  # Each action with type + params
    raw_response: str = ""  # Full response (for debugging)
    
    # State After Action
    balance_after: float = 0.0
    social_score_after: float = 0.0
    inventory_after: Dict[str, int] = field(default_factory=dict)
    
    # Context
    competitors_snapshot: List[Dict] = field(default_factory=list)
    events_active: List[str] = field(default_factory=list)
    
    # Metadata
    is_human: bool = False
    llm_provider: str = ""
    parse_errors: List[str] = field(default_factory=list)


class GameHistory:
    """Complete history of a game session"""
    
    def __init__(self, scenario_name: str = None):
        self.scenario = scenario_name
        self.start_time = datetime.now().isoformat()
        self.end_time: Optional[str] = None
        self.turns: List[TurnRecord] = []
        self.weekly_summaries: Dict[int, Dict] = {}
        self.final_rankings: List[Dict] = []
        
    def record_turn(self, record: TurnRecord):
        """Record a turn in the history"""
        self.turns.append(record)
        
        # Update weekly summary
        week = record.week
        if week not in self.weekly_summaries:
            self.weekly_summaries[week] = {
                "participants": {},
                "total_actions": 0
            }
        
        self.weekly_summaries[week]["participants"][record.agent_id] = {
            "actions_count": len(record.actions),
            "thinking_count": len(record.thinking),
            "balance_change": record.balance_after - record.balance_before
        }
        self.weekly_summaries[week]["total_actions"] += len(record.actions)
    
    def get_agent_history(self, agent_id: str) -> List[TurnRecord]:
        """Get all turns for a specific agent"""
        return [t for t in self.turns if t.agent_id == agent_id]
    
    def get_week_history(self, week: int) -> List[TurnRecord]:
        """Get all turns for a specific week"""
        return [t for t in self.turns if t.week == week]
    
    def finalize(self, rankings: List[Dict] = None):
        """Mark game as complete and record final rankings"""
        self.end_time = datetime.now().isoformat()
        if rankings:
            self.final_rankings = rankings
    
    def export_to_json(self, filepath: str):
        """Export full history to JSON file for analysis"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            "metadata": {
                "scenario": self.scenario,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "total_weeks": max((t.week for t in self.turns), default=0),
                "total_turns": len(self.turns),
                "participants": list(set(t.agent_id for t in self.turns))
            },
            "final_rankings": self.final_rankings,
            "weekly_summaries": self.weekly_summaries,
            "turns": [asdict(t) for t in self.turns]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
    
    def generate_comparison_report(self) -> Dict[str, Any]:
        """Generate side-by-side comparison of all participants"""
        agents = list(set(t.agent_id for t in self.turns))
        report = {"participants": {}, "summary": {}}
        
        for agent_id in agents:
            history = self.get_agent_history(agent_id)
            if not history:
                continue
                
            # Action breakdown
            action_counts = {}
            for turn in history:
                for action in turn.actions:
                    action_type = action.get("type", "unknown")
                    action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
            # Thinking samples
            all_thinking = []
            for turn in history:
                all_thinking.extend(turn.thinking)
            
            # Balance trajectory
            balance_trajectory = [
                {"week": t.week, "balance": t.balance_after} 
                for t in history
            ]
            
            report["participants"][agent_id] = {
                "name": history[0].agent_name,
                "is_human": history[0].is_human,
                "llm_provider": history[0].llm_provider if not history[0].is_human else "human",
                "total_turns": len(history),
                "action_breakdown": action_counts,
                "total_actions": sum(len(t.actions) for t in history),
                "thinking_samples": all_thinking[:10],  # First 10 thoughts
                "balance_trajectory": balance_trajectory,
                "initial_balance": history[0].balance_before,
                "final_balance": history[-1].balance_after if history else 0,
                "balance_change": (history[-1].balance_after - history[0].balance_before) if history else 0,
                "initial_social_score": history[0].social_score_before,
                "final_social_score": history[-1].social_score_after if history else 0,
            }
        
        # Summary stats
        if report["participants"]:
            report["summary"] = {
                "total_participants": len(agents),
                "total_weeks_played": max((t.week for t in self.turns), default=0),
                "winner": max(
                    report["participants"].items(),
                    key=lambda x: x[1]["final_balance"]
                )[0] if report["participants"] else None,
                "most_active": max(
                    report["participants"].items(),
                    key=lambda x: x[1]["total_actions"]
                )[0] if report["participants"] else None
            }
        
        return report
    
    def get_thinking_timeline(self, agent_id: str = None) -> List[Dict]:
        """Get timeline of all thinking for analysis"""
        turns = self.turns if agent_id is None else self.get_agent_history(agent_id)
        
        timeline = []
        for turn in turns:
            if turn.thinking:
                timeline.append({
                    "week": turn.week,
                    "agent_id": turn.agent_id,
                    "agent_name": turn.agent_name,
                    "thinking": turn.thinking,
                    "actions_taken": [a.get("type") for a in turn.actions]
                })
        
        return timeline
    
    def to_dict(self) -> Dict:
        """Convert entire history to dictionary"""
        return {
            "scenario": self.scenario,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "turns": [asdict(t) for t in self.turns],
            "weekly_summaries": self.weekly_summaries,
            "final_rankings": self.final_rankings
        }
    
    @classmethod
    def from_json(cls, filepath: str) -> 'GameHistory':
        """Load history from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        history = cls(data.get("metadata", {}).get("scenario"))
        history.start_time = data.get("metadata", {}).get("start_time", "")
        history.end_time = data.get("metadata", {}).get("end_time")
        history.final_rankings = data.get("final_rankings", [])
        history.weekly_summaries = data.get("weekly_summaries", {})
        
        for turn_data in data.get("turns", []):
            record = TurnRecord(**turn_data)
            history.turns.append(record)
        
        return history
