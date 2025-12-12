from typing import Callable, List, Dict, Any
from src.models.world import LaundromatState
from src.models.events.core import GameEvent

ActionHandler = Callable[[LaundromatState, Dict[str, Any], int, Dict[str, Any]], List[GameEvent]]

class ActionRegistry:
    _handlers: Dict[str, ActionHandler] = {}

    @classmethod
    def register(cls, action_type: str):
        def decorator(func: ActionHandler):
            cls._handlers[action_type] = func
            return func
        return decorator

    @classmethod
    def get_handler(cls, action_type: str) -> ActionHandler:
        return cls._handlers.get(action_type)

    @classmethod
    def list_actions(cls) -> List[str]:
        return list(cls._handlers.keys())
