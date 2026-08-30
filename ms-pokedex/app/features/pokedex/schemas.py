from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PokedexCreate(BaseModel):
    pokeapi_id: int = Field(gt=0)


class PokedexRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pokeapi_id: int
    name: str
    photo_url: str | None
    date_found: datetime
