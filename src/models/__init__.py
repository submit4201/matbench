"""
Pydantic models for Laundromat Tycoon.

All game data models are defined here for consistent type safety,
validation, and TypeScript generation.

Note: Uses lazy loading for some modules to avoid circular imports.
"""
from typing import TYPE_CHECKING

# Safe imports (no circular dependencies)
from .base import GameModel
from .agent import Action, Message, Observation
from .social import (
    SocialScore,
    SocialTier,
    Ticket,
    TicketType,
    TicketStatus,
    SOCIAL_SCORE_WEIGHTS,
    TIER_INFO_CONFIG
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

# Lazy-loaded imports to avoid circular dependencies
# These modules import from src.engine which may import back to src.models
_lazy_imports = {
    # Financial
    'Transaction': '.financial',
    'TransactionCategory': '.financial',
    'FinancialLedger': '.financial',
    'Bill': '.financial',
    'RevenueStream': '.financial',
    'Loan': '.financial',
    'FinancialReport': '.financial',
    # World
    'Machine': '.world',
    'StaffMember': '.world',
    'Building': '.world',
    'LaundromatState': '.world',
    # Commerce
    'VendorProfile': '.commerce',
    'VendorTier': '.commerce',
    'SupplyOffer': '.commerce',
    'SupplyChainEvent': '.commerce',
    'SupplyChainEventType': '.commerce',
    'Proposal': '.commerce',
    'ProposalStatus': '.commerce',
}

def __getattr__(name: str):
    if name in _lazy_imports:
        module_name = _lazy_imports[name]
        import importlib
        module = importlib.import_module(module_name, __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

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
