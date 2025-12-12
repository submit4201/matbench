from src.engine.projections.registry import EventRegistry
from src.models.world import LaundromatState
from src.models.events.core import GameEvent

@EventRegistry.register("INVENTORY_STOCKED")
@EventRegistry.register("INVENTORY_UPDATED")
def apply_inventory_stock(state: LaundromatState, event: GameEvent):
    payload = event.payload
    item = getattr(event, "item_type", payload.get("item"))
    qty = getattr(event, "quantity", payload.get("quantity", 0))
    
    current = state.primary_location.inventory.get(item, 0)
    state.primary_location.inventory[item] = max(0, current + qty)

@EventRegistry.register("PRICE_SET")
def apply_price_set(state: LaundromatState, event: GameEvent):
    payload = event.payload
    val = getattr(event, "new_price", payload.get("price"))
    if val is not None:
        state.primary_location.price = val
