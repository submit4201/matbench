"""
Proxy for backward compatibility.

All models have been migrated to src/models/social.py.
Import from there for new code.
"""

# Re-export from new location for backward compatibility
from src.models.social import (
    Ticket,
    TicketType,
    TicketStatus
)

__all__ = [
    'Ticket',
    'TicketType',
    'TicketStatus'
]
