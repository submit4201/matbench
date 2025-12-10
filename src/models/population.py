"""
Pydantic models for population system (Customers, Personas, Memory).
"""

from pydantic import Field, field_validator
from typing import Dict, Optional
from enum import Enum

from .base import GameModel


# ═══════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════

class CustomerSegment(str, Enum):
    """Customer demographic segments."""
    STUDENT = "Student"
    FAMILY = "Family"
    SENIOR = "Senior"
    ADULT = "Adult"


# ═══════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════

class CustomerMemory(GameModel):
    """
    Memory of a customer's interactions with a specific laundromat.
    Affects future decision-making.
    """
    laundromat_id: str
    interaction_count: int = 0
    bad_experiences: int = 0
    good_experiences: int = 0
    last_visit_week: int = -1


class Persona(GameModel):
    """
    Customer personality archetype that drives behavior.
    
    Sensitivity values range from 0.0 to 1.0:
    - 1.0 price_sensitivity = very budget-conscious
    - 1.0 quality_sensitivity = demands premium service
    - 1.0 ethics_sensitivity = cares deeply about social score
    - 1.0 patience = very tolerant of wait times
    - 1.0 irrationality_factor = decisions are random/emotional
    """
    name: str
    segment: CustomerSegment = CustomerSegment.ADULT
    price_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    quality_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    ethics_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    patience: float = Field(default=0.5, ge=0.0, le=1.0)
    irrationality_factor: float = Field(default=0.1, ge=0.0, le=1.0)
