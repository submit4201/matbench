from dataclasses import dataclass
from enum import Enum

class TicketType(Enum):
    OUT_OF_SOAP = "out_of_soap"
    MACHINE_BROKEN = "machine_broken"
    DIRTY_FLOOR = "dirty_floor"
    LONG_WAIT = "long_wait"
    OTHER = "other"

class TicketStatus(Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    EXPIRED = "expired"

@dataclass
class Ticket:
    id: str
    type: TicketType
    description: str
    customer_id: str
    laundromat_id: str
    created_week: int
    severity: str = "medium"
    status: TicketStatus = TicketStatus.OPEN
    resolution_week: int = -1
