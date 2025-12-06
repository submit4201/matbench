from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class ActionType(Enum):
    SET_PRICE = "set_price"
    MARKETING_CAMPAIGN = "marketing_campaign"
    UPGRADE_MACHINE = "upgrade_machine"
    SEND_MESSAGE = "send_message"
    BUY_SUPPLIES = "buy_supplies"
    RESOLVE_TICKET = "resolve_ticket"
    PROPOSE_ALLIANCE = "propose_alliance"
    INITIATE_BUYOUT = "initiate_buyout"
    NEGOTIATE = "negotiate"
    WAIT = "wait"

@dataclass
class Action:
    type: ActionType
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class Message:
    sender_id: str
    recipient_id: str
    content: str
    week: int

@dataclass
class Observation:
    week: int
    season: str
    my_stats: Dict[str, Any]
    competitor_stats: List[Dict[str, Any]]
    messages: List[Message]
    events: List[str]
    alliances: List[str] = None
    trust_scores: Dict[str, float] = None
    market_data: Dict[str, Any] = None

class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str):
        self.id = agent_id
        self.name = name

    @abstractmethod
    def decide_action(self, observation: Observation) -> Action:
        """
        Given the current state of the world (Observation), return an Action.
        """
        pass
