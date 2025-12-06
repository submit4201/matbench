
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict
import json

class TicketType(Enum):
    OUT_OF_SOAP = "out_of_soap"

class TicketStatus(Enum):
    OPEN = "open"

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

@dataclass
class LaundromatState:
    name: str
    id: str
    tickets: List[Ticket] = None

def _serialize_state(laundromat_state):
    data = laundromat_state.__dict__.copy()
    # Serialize Tickets
    if data.get("tickets"):
        tickets_data = []
        for t in data["tickets"]:
            t_dict = t.__dict__.copy()
            # Handle Enums
            if hasattr(t_dict["type"], "value"):
                t_dict["type"] = t_dict["type"].value
            if hasattr(t_dict["status"], "value"):
                t_dict["status"] = t_dict["status"].value
            tickets_data.append(t_dict)
        data["tickets"] = tickets_data
    return data

# Test
t1 = Ticket(id="t1", type=TicketType.OUT_OF_SOAP, description="desc", customer_id="c1", laundromat_id="p1", created_week=1)
l1 = LaundromatState(name="L1", id="p1", tickets=[t1])

serialized = _serialize_state(l1)
print("Serialized:", serialized)

try:
    json_str = json.dumps(serialized, indent=2)
    print("JSON Success")
except TypeError as e:
    print("JSON Error:", e)
