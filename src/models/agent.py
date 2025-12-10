from typing import List, Dict, Any, Optional
from pydantic import Field
from src.models.base import GameModel

class Action(GameModel):
    type: str # Enum ActionType name
    parameters: Dict[str, Any] = Field(default_factory=dict)

class Message(GameModel):
    id: str
    sender_id: str
    recipient_id: str
    content: str
    week: int
    day: str = "MONDAY"
    intent: str = "general"
    read_by: List[str] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    channel: str = "direct"

class Observation(GameModel):
    week: int
    day: str
    phase: str
    season: str
    my_stats: Dict[str, Any]
    competitor_stats: List[Dict[str, Any]]
    messages: List[Message] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    alliances: List[str] = Field(default_factory=list)
    trust_scores: Dict[str, float] = Field(default_factory=dict)
    market_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Enhanced data
    credit_info: Optional[Dict[str, Any]] = None
    zone_info: Optional[Dict[str, Any]] = None
    calendar_info: Optional[Dict[str, Any]] = None
    ethical_dilemma: Optional[Dict[str, Any]] = None
