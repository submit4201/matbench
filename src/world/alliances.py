from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class AllianceType(Enum):
    NON_AGGRESSION = "non_aggression"
    PRICE_STABILITY = "price_stability" # Borderline illegal
    JOINT_MARKETING = "joint_marketing"
    FULL_PARTNERSHIP = "full_partnership"

@dataclass
class Alliance:
    id: str
    members: List[str]
    type: AllianceType
    start_week: int
    duration_weeks: int
    terms: str

class TrustSystem:
    """Tracks trust levels between agents."""
    def __init__(self, agent_ids: List[str]):
        self.trust_matrix: Dict[str, Dict[str, float]] = {
            agent_id: {other: 50.0 for other in agent_ids if other != agent_id}
            for agent_id in agent_ids
        }
        self.active_alliances: List[Alliance] = []

    def get_trust(self, agent_a: str, agent_b: str) -> float:
        return self.trust_matrix.get(agent_a, {}).get(agent_b, 50.0)

    def update_trust(self, agent_a: str, agent_b: str, delta: float):
        if agent_a in self.trust_matrix and agent_b in self.trust_matrix[agent_a]:
            current = self.trust_matrix[agent_a][agent_b]
            self.trust_matrix[agent_a][agent_b] = max(0.0, min(100.0, current + delta))

    def propose_alliance(self, initiator: str, target: str, type: AllianceType, duration: int) -> Optional[Alliance]:
        # Simple logic: Accept if trust > 70
        if self.get_trust(target, initiator) > 70.0:
            alliance = Alliance(
                id=f"{initiator}_{target}_{type.value}",
                members=[initiator, target],
                type=type,
                start_week=0, # Should be passed in
                duration_weeks=duration,
                terms="Standard terms"
            )
            self.active_alliances.append(alliance)
            return alliance
        return None
