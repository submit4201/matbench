from typing import Optional

from .core import GameEvent


class TimeAdvanced(GameEvent):
    """Event for time advancement (tick)."""
    type: str = "TIME_ADVANCED"
    new_week: int
    new_day: int
    season: str


class MarketTrendChanged(GameEvent):
    """Event for global market trend changes."""
    type: str = "MARKET_TREND_CHANGED"
    trend_name: str
    impact_multiplier: float
    description: str


class WeatherChanged(GameEvent):
    """Event for weather changes."""
    type: str = "WEATHER_CHANGED"
    weather_type: str
    intensity: float  # 0.0 to 1.0 maybe?
