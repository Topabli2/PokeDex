from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class TeamUpdate(BaseModel):
    # Todo opcional: PATCH parcial
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime


class TeamPokemonCreate(BaseModel):
    # El Pokémon se identifica públicamente por su pokeapi_id
    pokeapi_id: int = Field(gt=0)
    slot: int = Field(ge=1, le=6)


class TeamPokemonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    pokeapi_id: int
    name: str
    photo_url: str | None
    slot: int
    created_at: datetime


class TeamPokemonUpdate(BaseModel):
    slot: int | None = Field(default=None, ge=1, le=6)


class TeamDetail(TeamRead):
    pokemons: list[TeamPokemonRead]
