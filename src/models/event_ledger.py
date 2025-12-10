# Proxy module for backwards compatibility
# Re-exports classes from src.world.event_ledger

from src.world.event_ledger import GameEventLedger, GameEvent, EventCategory

__all__ = ['GameEventLedger', 'GameEvent', 'EventCategory']
