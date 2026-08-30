from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.pokemon.repository import PokemonRepository
from app.features.pokemon.schemas import (
    PokemonCreate,
    PokemonRead,
    PokemonSummary,
    PokemonUpdate,
)
from app.features.pokemon.service import PokemonService

router = APIRouter(prefix="/pokemon", tags=["pokemon"])


def get_service(db: AsyncSession = Depends(get_db)) -> PokemonService:
    """Por cada petición: sesión fresca → repository → service."""
    return PokemonService(PokemonRepository(db))


@router.get("/", response_model=list[PokemonSummary])
async def list_pokemons(
    skip: int = 0,
    limit: int = 100,
    service: PokemonService = Depends(get_service),
):
    return await service.list_pokemons(skip, limit)


@router.get("/{pokeapi_id}", response_model=PokemonRead)
async def get_pokemon(
    pokeapi_id: int,
    service: PokemonService = Depends(get_service),
):
    pokemon = await service.get_pokemon(pokeapi_id)
    if pokemon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pokémon no encontrado")
    return pokemon


@router.post("/", response_model=PokemonRead, status_code=status.HTTP_201_CREATED)
async def create_pokemon(
    data: PokemonCreate,
    service: PokemonService = Depends(get_service),
):
    try:
        return await service.create_pokemon(data)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.patch("/{pokeapi_id}", response_model=PokemonRead)
async def update_pokemon(
    pokeapi_id: int,
    data: PokemonUpdate,
    service: PokemonService = Depends(get_service),
):
    try:
        pokemon = await service.update_pokemon(pokeapi_id, data)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    if pokemon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pokémon no encontrado")
    return pokemon


@router.delete("/{pokeapi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pokemon(
    pokeapi_id: int,
    service: PokemonService = Depends(get_service),
):
    if not await service.delete_pokemon(pokeapi_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pokémon no encontrado")