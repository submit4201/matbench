from pydantic import BaseModel, ConfigDict

class GameModel(BaseModel):
    """Base model for all game entities."""
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True # Temporary until all types are Pydantic
    )
