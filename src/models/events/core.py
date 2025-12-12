from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
import uuid

class GameEvent(BaseModel):
    """
    Base class for all game events.
    Events are immutable facts that happened in the past.
    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # e.g., "STAFF_HIRED", "TRANSACTION_RECORDED"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Context
    week: int
    agent_id: str
    
    # Payload - The specifics of what changed
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata for debugging/audit
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        frozen = True # Events should be immutable
