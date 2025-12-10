# [ ]↔T: Enhanced Communication System
#   - [x] Multiple channel types (DM, Group, Public, Formal)
#   - [x] Visibility rules per channel
#   - [x] Message sentiment tracking
#   - [x] Deception detection hooks
#   - [x] Game Master analysis integration
# PRIORITY: P1 - Critical for rich LLM evaluation
# STATUS: Complete

"""
Enhanced Communication System

Provides multiple communication channels with different visibility rules:
- Direct Message (DM): Private between 2 agents
- Group: Shared with alliance/coalition members
- Public: Visible to all agents (announcements, posturing)
- Formal: Logged for regulatory review (contracts, proposals)

Features:
- Message categorization and intent tracking
- Consistency checking (DM vs Public statements)
- Game Master hooks for sentiment analysis
- Alliance-based message routing
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class ChannelType(Enum):
    """Types of communication channels."""
    DM = "dm"              # Direct message - private
    GROUP = "group"        # Alliance/coalition group chat
    PUBLIC = "public"      # Public announcement - all agents see
    FORMAL = "formal"      # Formal/legal - logged for regulators
    SYSTEM = "system"      # System messages (events, notifications)


class MessageIntent(Enum):
    """Intent categories for messages."""
    CHAT = "chat"
    PROPOSAL = "proposal"
    COUNTER_PROPOSAL = "counter_proposal"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"
    THREAT = "threat"
    PROMISE = "promise"
    INQUIRY = "inquiry"
    ANNOUNCEMENT = "announcement"
    WARNING = "warning"
    NEGOTIATION = "negotiation"
    DILEMMA = "dilemma"
    DILEMMA_OUTCOME = "dilemma_outcome"


@dataclass
class Message:
    """
    Enhanced message with channel and visibility information.
    """
    id: str
    sender_id: str
    channel: ChannelType
    content: str
    week: int
    day: int = 1
    intent: MessageIntent = MessageIntent.CHAT
    
    # Visibility
    recipient_id: Optional[str] = None       # For DM
    group_id: Optional[str] = None           # For GROUP
    visible_to: Set[str] = field(default_factory=set)  # Explicit visibility list
    
    # Metadata
    reply_to_id: Optional[str] = None        # Thread support
    attachments: List[Dict] = field(default_factory=list)  # Data attachments
    
    # Analysis (populated by Game Master)
    sentiment_score: Optional[float] = None  # -1 to 1
    honesty_estimate: Optional[float] = None # 0 to 1
    manipulation_risk: Optional[float] = None # 0 to 1
    
    # Tracking
    read_by: Set[str] = field(default_factory=set)
    is_deleted: bool = False


@dataclass
class Group:
    """A message group (alliance, coalition, etc.)."""
    id: str
    name: str
    members: Set[str]
    owner_id: str
    created_week: int
    is_active: bool = True
    message_ids: List[str] = field(default_factory=list)


class CommunicationSystem:
    """
    Enhanced communication system with multiple channels.
    """
    # [ ] this so sould be split up based on type of message and the brought together 
    # [ ] this should be split up into multiple files 
    # [ ] needs history tracking for benchmarking abnd scoring 
    def __init__(self):
        self.messages: Dict[str, Message] = {}  # message_id -> Message
        self.groups: Dict[str, Group] = {}      # group_id -> Group
        self.agent_inboxes: Dict[str, List[str]] = {}  # agent_id -> [message_ids]
        
        # Consistency tracking for Game Master
        self.agent_statements: Dict[str, Dict[str, List[str]]] = {}  # agent -> topic -> statements
        
    def send_dm(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        week: int,
        day: int = 1,
        intent: MessageIntent = MessageIntent.CHAT,
        reply_to: Optional[str] = None,
        attachments: List[Dict] = None
    ) -> Message:
        """
        Send a direct message (private between two agents).
        """
        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender_id=sender_id,
            recipient_id=recipient_id,
            channel=ChannelType.DM,
            content=content,
            week=week,
            day=day,
            intent=intent,
            visible_to={sender_id, recipient_id},
            reply_to_id=reply_to,
            attachments=attachments or []
        )
        
        self._store_message(msg)
        self._add_to_inbox(recipient_id, msg.id)
        
        logger.debug(f"DM from {sender_id} to {recipient_id}: {content[:50]}...")
        
        return msg
    
    def send_group_message(
        self,
        sender_id: str,
        group_id: str,
        content: str,
        week: int,
        day: int = 1,
        intent: MessageIntent = MessageIntent.CHAT
    ) -> Optional[Message]:
        """
        Send a message to a group (alliance members).
        """
        group = self.groups.get(group_id)
        if not group:
            logger.warning(f"Group {group_id} not found")
            return None
        
        if sender_id not in group.members:
            logger.warning(f"Sender {sender_id} not in group {group_id}")
            return None
        
        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender_id=sender_id,
            group_id=group_id,
            channel=ChannelType.GROUP,
            content=content,
            week=week,
            day=day,
            intent=intent,
            visible_to=group.members.copy()
        )
        
        self._store_message(msg)
        group.message_ids.append(msg.id)
        
        # Add to all member inboxes except sender
        for member_id in group.members:
            if member_id != sender_id:
                self._add_to_inbox(member_id, msg.id)
        
        logger.debug(f"Group message from {sender_id} to {group.name}: {content[:50]}...")
        
        return msg
    
    def send_public(
        self,
        sender_id: str,
        content: str,
        week: int,
        day: int = 1,
        intent: MessageIntent = MessageIntent.ANNOUNCEMENT,
        all_agent_ids: List[str] = None
    ) -> Message:
        """
        Send a public message visible to all agents.
        """
        visible = set(all_agent_ids) if all_agent_ids else set()
        visible.add(sender_id)
        
        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender_id=sender_id,
            channel=ChannelType.PUBLIC,
            content=content,
            week=week,
            day=day,
            intent=intent,
            visible_to=visible
        )
        
        self._store_message(msg)
        
        # Add to all inboxes
        for agent_id in visible:
            if agent_id != sender_id:
                self._add_to_inbox(agent_id, msg.id)
        
        # Track for consistency checking
        self._track_statement(sender_id, content, "public")
        
        logger.debug(f"Public message from {sender_id}: {content[:50]}...")
        
        return msg
    
    def send_formal(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        week: int,
        day: int = 1,
        intent: MessageIntent = MessageIntent.PROPOSAL,
        attachments: List[Dict] = None
    ) -> Message:
        """
        Send a formal message (contracts, proposals - logged for regulators).
        """
        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender_id=sender_id,
            recipient_id=recipient_id,
            channel=ChannelType.FORMAL,
            content=content,
            week=week,
            day=day,
            intent=intent,
            visible_to={sender_id, recipient_id, "REGULATOR"},  # Regulators can see
            attachments=attachments or []
        )
        
        self._store_message(msg)
        self._add_to_inbox(recipient_id, msg.id)
        
        logger.info(f"Formal message from {sender_id} to {recipient_id}: {intent.value}")
        
        return msg
    
    def send_system_message(
        self,
        recipient_id: str,
        content: str,
        week: int,
        day: int = 1,
        intent: MessageIntent = MessageIntent.CHAT,
        attachments: List[Dict] = None
    ) -> Message:
        """
        Send a system message (events, notifications).
        """
        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender_id="SYSTEM",
            recipient_id=recipient_id,
            channel=ChannelType.SYSTEM,
            content=content,
            week=week,
            day=day,
            intent=intent,
            visible_to={recipient_id},
            attachments=attachments or []
        )
        
        self._store_message(msg)
        self._add_to_inbox(recipient_id, msg.id)
        
        return msg
    
    # Legacy compatibility
    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        week: int,
        intent: str = "chat"
    ) -> Message:
        """Legacy send_message for backward compatibility."""
        intent_enum = MessageIntent.CHAT
        try:
            intent_enum = MessageIntent(intent)
        except ValueError:
            pass
        
        return self.send_dm(sender_id, recipient_id, content, week, 1, intent_enum)
    
    def _store_message(self, msg: Message):
        """Store a message."""
        self.messages[msg.id] = msg
    
    def _add_to_inbox(self, agent_id: str, message_id: str):
        """Add message to agent's inbox."""
        if agent_id not in self.agent_inboxes:
            self.agent_inboxes[agent_id] = []
        self.agent_inboxes[agent_id].append(message_id)
    
    def _track_statement(self, agent_id: str, content: str, context: str):
        """Track statement for consistency checking."""
        if agent_id not in self.agent_statements:
            self.agent_statements[agent_id] = {}
        if context not in self.agent_statements[agent_id]:
            self.agent_statements[agent_id][context] = []
        self.agent_statements[agent_id][context].append(content)
    
    # ═══════════════════════════════════════════════════════════════════
    # GROUP MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════
    
    def create_group(
        self,
        name: str,
        owner_id: str,
        initial_members: List[str],
        week: int
    ) -> Group:
        """Create a new message group."""
        group = Group(
            id=str(uuid.uuid4())[:8],
            name=name,
            members=set(initial_members),
            owner_id=owner_id,
            created_week=week
        )
        group.members.add(owner_id)
        
        self.groups[group.id] = group
        
        logger.info(f"Created group {name} with {len(group.members)} members")
        
        return group
    
    def add_to_group(self, group_id: str, agent_id: str) -> bool:
        """Add an agent to a group."""
        group = self.groups.get(group_id)
        if not group:
            return False
        group.members.add(agent_id)
        return True
    
    def remove_from_group(self, group_id: str, agent_id: str) -> bool:
        """Remove an agent from a group."""
        group = self.groups.get(group_id)
        if not group:
            return False
        group.members.discard(agent_id)
        return True
    
    # ═══════════════════════════════════════════════════════════════════
    # RETRIEVAL
    # ═══════════════════════════════════════════════════════════════════
    
    def get_inbox(self, agent_id: str, unread_only: bool = False) -> List[Message]:
        """Get all messages in an agent's inbox."""
        message_ids = self.agent_inboxes.get(agent_id, [])
        messages = [self.messages[mid] for mid in message_ids if mid in self.messages]
        
        if unread_only:
            messages = [m for m in messages if agent_id not in m.read_by]
        
        # Sort by time (week, day)
        messages.sort(key=lambda m: (m.week, m.day), reverse=True)
        
        return messages
    
    def get_messages(self, agent_id: str) -> List[Message]:
        """Get all messages where agent is sender or recipient (legacy compat)."""
        return [
            m for m in self.messages.values()
            if agent_id in m.visible_to and not m.is_deleted
        ]
    
    def get_conversation(self, agent_a: str, agent_b: str) -> List[Message]:
        """Get DM conversation between two agents."""
        return [
            m for m in self.messages.values()
            if m.channel == ChannelType.DM and
               ((m.sender_id == agent_a and m.recipient_id == agent_b) or
                (m.sender_id == agent_b and m.recipient_id == agent_a))
        ]
    
    def get_public_messages(self, limit: int = 50) -> List[Message]:
        """Get recent public messages."""
        public = [m for m in self.messages.values() if m.channel == ChannelType.PUBLIC]
        public.sort(key=lambda m: (m.week, m.day), reverse=True)
        return public[:limit]
    
    def get_formal_messages(self, agent_id: str = None) -> List[Message]:
        """Get formal messages (for regulatory review)."""
        formal = [m for m in self.messages.values() if m.channel == ChannelType.FORMAL]
        if agent_id:
            formal = [m for m in formal if m.sender_id == agent_id or m.recipient_id == agent_id]
        return formal
    
    def mark_read(self, message_id: str, agent_id: str):
        """Mark a message as read."""
        msg = self.messages.get(message_id)
        if msg:
            msg.read_by.add(agent_id)
    
    # ═══════════════════════════════════════════════════════════════════
    # ANALYSIS (Game Master Integration)
    # ═══════════════════════════════════════════════════════════════════
    
    def check_consistency(self, agent_id: str) -> Dict[str, Any]:
        """
        Check if an agent's public statements are consistent with DMs.
        
        Used by Game Master for deception detection.
        """
        public_statements = []
        private_statements = []
        
        for msg in self.messages.values():
            if msg.sender_id == agent_id:
                if msg.channel == ChannelType.PUBLIC:
                    public_statements.append(msg.content)
                elif msg.channel == ChannelType.DM:
                    private_statements.append(msg.content)
        
        # Simple keyword matching for contradictions
        # In production, this would use Game Master LLM
        #! TODO: will need to implimennt socail events to test our LLMs
        #! TODO: this should be a game master function 
        contradictions = []
        
        return {
            "public_count": len(public_statements),
            "private_count": len(private_statements),
            "potential_contradictions": contradictions,
            "needs_llm_analysis": len(public_statements) > 0 and len(private_statements) > 0
        }
    
    def get_negotiation_history(self, agent_id: str) -> List[Message]:
        """Get all negotiation-related messages for an agent."""
        #! TODO: this should be a game master function 
        negotiation_intents = [
            MessageIntent.PROPOSAL,
            MessageIntent.COUNTER_PROPOSAL,
            MessageIntent.ACCEPTANCE,
            MessageIntent.REJECTION,
            MessageIntent.NEGOTIATION
        ]
        
        return [
            m for m in self.messages.values()
            if (m.sender_id == agent_id or m.recipient_id == agent_id) and
               m.intent in negotiation_intents
        ]
    
    def get_communication_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get communication statistics for an agent."""
        #! TODO: this should be a game master function 
        sent = [m for m in self.messages.values() if m.sender_id == agent_id]
        received = [m for m in self.messages.values() if agent_id in m.visible_to and m.sender_id != agent_id]
        
        by_channel = {}
        for msg in sent:
            channel = msg.channel.value
            by_channel[channel] = by_channel.get(channel, 0) + 1
        
        by_intent = {}
        for msg in sent:
            intent = msg.intent.value
            by_intent[intent] = by_intent.get(intent, 0) + 1
        
        return {
            "total_sent": len(sent),
            "total_received": len(received),
            "by_channel": by_channel,
            "by_intent": by_intent,
            "avg_sentiment": sum(m.sentiment_score or 0 for m in sent) / max(len(sent), 1),
            "groups_member_of": len([g for g in self.groups.values() if agent_id in g.members])
        }
    
    def to_dict(self, agent_id: str, limit: int = 50) -> Dict[str, Any]:
        """Serialize for API responses."""
        inbox = self.get_inbox(agent_id)[:limit]
        
        return {
            "inbox": [
                {
                    "id": m.id,
                    "sender": m.sender_id,
                    "channel": m.channel.value,
                    "content": m.content[:200],
                    "intent": m.intent.value,
                    "week": m.week,
                    "day": m.day,
                    "is_read": agent_id in m.read_by
                }
                for m in inbox
            ],
            "unread_count": len([m for m in inbox if agent_id not in m.read_by]),
            "groups": [
                {"id": g.id, "name": g.name, "member_count": len(g.members)}
                for g in self.groups.values()
                if agent_id in g.members
            ],
            "stats": self.get_communication_stats(agent_id)
        }


# Legacy class for backward compatibility
class CommunicationChannel(CommunicationSystem):
    """
    Legacy class name for backward compatibility.
    Use CommunicationSystem for new code.
    """
    pass
