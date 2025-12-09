from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
from src.models.agent import Action, Message, Observation

class ActionType(str, Enum):
    """Enumeration of possible agent actions."""
    SET_PRICE = "SET_PRICE"
    BUY_SUPPLIES = "BUY_SUPPLIES"
    MARKETING_CAMPAIGN = "MARKETING_CAMPAIGN"
    UPGRADE_MACHINE = "UPGRADE_MACHINE"
    RESOLVE_TICKET = "RESOLVE_TICKET"
    SEND_MESSAGE = "SEND_MESSAGE"
    WAIT = "WAIT"
    # Extended
    PROPOSE_ALLIANCE = "PROPOSE_ALLIANCE"
    INITIATE_BUYOUT = "INITIATE_BUYOUT"
    NEGOTIATE = "NEGOTIATE"
    PAY_BILL = "PAY_BILL"
    HIRE_STAFF = "HIRE_STAFF"
    SCHEDULE_MAINTENANCE = "SCHEDULE_MAINTENANCE"
    APPLY_LOAN = "APPLY_LOAN"
    BUY_BUILDING = "BUY_BUILDING"
    RESOLVE_DILEMMA = "RESOLVE_DILEMMA"

    
class BaseAgent(ABC):
    """
    Abstract base class for all Laundromat Tycoon agents.
    """
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name

    @property
    def id(self) -> str:
        return self.agent_id

    @abstractmethod
    def decide_action(self, observation: Observation) -> List[Action]:
        """
        Core decision method.
        Args:
            observation: Current game state perceived by the agent
        Returns:
            List of Action objects to execute
        """
        pass
