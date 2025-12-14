"""World event handlers for global state changes."""
from __future__ import annotations
from typing import TYPE_CHECKING
from src.engine.projections.registry import EventRegistry

if TYPE_CHECKING:
    from src.models.world import LaundromatState
    from src.models.events.core import GameEvent


@EventRegistry.register("TIME_ADVANCED")
def apply_time_advanced(state: LaundromatState, event: GameEvent):
    """
    Time progression projection.
    """
    # Simply sync the world week.
    state.world.current_week = event.week


@EventRegistry.register("MARKET_TREND_CHANGED")
def apply_market_trend_changed(state: LaundromatState, event: GameEvent):
    """
    Update global market trends.
    """
    payload = event.payload if hasattr(event, "payload") else {}
    trend_data = getattr(event, "trend_data", payload.get("trend_data"))
    if trend_data:
        # Merge or replace trends
        state.world.market_trends.update(trend_data)


@EventRegistry.register("WEATHER_CHANGED")
def apply_weather_changed(state: LaundromatState, event: GameEvent):
    """
    Update global weather.
    """
    payload = event.payload if hasattr(event, "payload") else {}
    weather = getattr(event, "weather_condition", payload.get("weather_condition"))
    if weather:
        state.world.weather = weather
