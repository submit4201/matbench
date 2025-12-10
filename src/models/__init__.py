"""
Pydantic models for Laundromat Tycoon.

All game data models are defined here for consistent type safety,
validation, and TypeScript generation.
"""

from .base import GameModel
from .agent import Action, Message, Observation
from .financial import (
    Transaction,
    TransactionCategory, 
    FinancialLedger,
    Bill,
    RevenueStream,
    Loan,
    FinancialReport
)
from .world import (
    Machine,
    StaffMember,
    Building,
    LaundromatState
)
from .social import (
    SocialScore,
    SocialTier,
    Ticket,
    TicketType,
    TicketStatus,
    SOCIAL_SCORE_WEIGHTS,
    TIER_INFO_CONFIG
)
from .commerce import (
    VendorProfile,
    VendorTier,
    SupplyOffer,
    SupplyChainEvent,
    SupplyChainEventType,
    Proposal,
    ProposalStatus
)
from .population import (
    CustomerMemory,
    Persona,
    CustomerSegment
)
from .communication import (
    Alliance,
    AllianceType,
    CommunicationGroup,
    CommunicationMessage,
    ChannelType,
    MessageIntent
)

__all__ = [
    # Base
    'GameModel',
    # Agent
    'Action',
    'Message', 
    'Observation',
    # Financial
    'Transaction',
    'TransactionCategory',
    'FinancialLedger',
    'Bill',
    'RevenueStream',
    'Loan',
    'FinancialReport',
    # World
    'Machine',
    'StaffMember',
    'Building',
    'LaundromatState',
    # Social
    'SocialScore',
    'SocialTier',
    'Ticket',
    'TicketType',
    'TicketStatus',
    'SOCIAL_SCORE_WEIGHTS',
    'TIER_INFO_CONFIG',
    # Commerce
    'VendorProfile',
    'VendorTier',
    'SupplyOffer',
    'SupplyChainEvent',
    'SupplyChainEventType',
    'Proposal',
    'ProposalStatus',
    # Population
    'CustomerMemory',
    'Persona',
    'CustomerSegment',
    # Communication
    'Alliance',
    'AllianceType',
    'CommunicationGroup',
    'CommunicationMessage',
    'ChannelType',
    'MessageIntent',
]
