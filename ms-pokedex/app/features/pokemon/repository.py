from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field



class PokemonCreate(BaseModel):
    pokeapi_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    types: list[str] | None = None
    photo_url: str | None = None


class PokemonUpdate(BaseModel):
    pokeapi_id: int | None = Field(default=None, gt=0) 
    name: str | None = Field(default=None, min_length=1, max_length=100)
    types: list[str] | None = None
    photo_url: str | None = None

class PokemonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pokeapi_id: int
    name: str
    types: list[str] | None
    photo_url: str | None
    created_at: datetime
    updated_at: datetime


class PokemonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    photo_url: str | None