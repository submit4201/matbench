"""World event handlers for global state changes."""
from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.projections.registry import EventRegistry

if TYPE_CHECKING:
    from src.models.world import LaundromatState
    from src.models.events.core import GameEvent


@EventRegistry.register("TIME_ADVANCED")
def apply_time_advanced(state: LaundromatState, event: GameEvent):
    """Stub for time progression - time is managed externally by TimeSystem."""
    pass


@EventRegistry.register("MARKET_TREND_CHANGED")
def apply_market_trend_changed(state: LaundromatState, event: GameEvent):
    """Stub for market trend updates - global state."""
    pass


@EventRegistry.register("WEATHER_CHANGED")
def apply_weather_changed(state: LaundromatState, event: GameEvent):
    """Stub for weather updates - affects customer behavior."""
    pass
