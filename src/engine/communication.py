from dataclasses import dataclass
from typing import List, Dict, Optional
import uuid

@dataclass
class NegotiationMessage:
    id: str
    sender_id: str
    recipient_id: str
    content: str
    week: int
    intent: str = "chat" # chat, proposal, threat, agreement

class CommunicationChannel:
    """
    Handles direct messaging and negotiation between agents.
    """
    def __init__(self):
        self.message_log: List[NegotiationMessage] = []

    def send_message(self, sender_id: str, recipient_id: str, content: str, week: int, intent: str = "chat") -> NegotiationMessage:
        msg = NegotiationMessage(
            id=str(uuid.uuid4())[:8],
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            week=week,
            intent=intent
        )
        self.message_log.append(msg)
        return msg

    def get_messages(self, agent_id: str) -> List[NegotiationMessage]:
        """Get all messages where agent is sender or recipient."""
        return [m for m in self.message_log if m.sender_id == agent_id or m.recipient_id == agent_id]

    def get_conversation(self, agent_a: str, agent_b: str) -> List[NegotiationMessage]:
        """Get conversation history between two specific agents."""
        return [
            m for m in self.message_log 
            if (m.sender_id == agent_a and m.recipient_id == agent_b) or 
               (m.sender_id == agent_b and m.recipient_id == agent_a)
        ]
