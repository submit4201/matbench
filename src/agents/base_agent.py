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
    PERFORM_MAINTENANCE = "PERFORM_MAINTENANCE"
    SCHEDULE_MAINTENANCE = "SCHEDULE_MAINTENANCE"
    APPLY_LOAN = "APPLY_LOAN"
    BUY_BUILDING = "BUY_BUILDING"
    RESOLVE_DILEMMA = "RESOLVE_DILEMMA"
    FIRE_STAFF = "FIRE_STAFF"
    TRAIN_STAFF = "TRAIN_STAFF"
    MAKE_PAYMENT = "MAKE_PAYMENT"
    # Extended Tools Actions
    APPLY_FOR_LOAN = "APPLY_FOR_LOAN"
    SCHEDULE_ACTION = "SCHEDULE_ACTION"
    SEND_DM = "SEND_DM"
    SEND_PUBLIC = "SEND_PUBLIC"
    SEND_FORMAL = "SEND_FORMAL"
    
    # Active Perception & Info Gathering
    INSPECT_COMPETITOR = "INSPECT_COMPETITOR"
    CHECK_MARKET_TRENDS = "CHECK_MARKET_TRENDS"
    READ_NEWS = "READ_NEWS"
    INSPECT_FACILITY = "INSPECT_FACILITY"
    INSPECT_INVENTORY = "INSPECT_INVENTORY"
    INSPECT_VENDOR = "INSPECT_VENDOR"
    
    # Financial Info
    
    # Meta (New)
    GET_TOOL_HELP = "GET_TOOL_HELP"

    # Final Gaps (Regulatory & Emergency)
    EMERGENCY_REPAIR = "EMERGENCY_REPAIR"
    CHECK_REGULATIONS = "CHECK_REGULATIONS"
    CHECK_REPUTATION = "CHECK_REPUTATION"
    INSPECT_PUBLIC_RECORDS = "INSPECT_PUBLIC_RECORDS"

    
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
