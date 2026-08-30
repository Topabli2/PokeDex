from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.models import User
from app.features.auth.security import get_current_user
from app.features.pokedex.repository import PokedexRepository
from app.features.pokemon.repository import PokemonRepository
from app.features.teams.repository import TeamRepository
from app.features.teams.schemas import (
    TeamCreate,
    TeamDetail,
    TeamPokemonCreate,
    TeamPokemonRead,
    TeamPokemonUpdate,
    TeamRead,
    TeamUpdate,
)
from app.features.teams.service import TeamService

router = APIRouter(prefix="/teams", tags=["teams"])


def get_service(db: AsyncSession = Depends(get_db)) -> TeamService:
    """Por cada petición: sesión fresca → repository → service.
    El TeamService necesita además PokedexRepository para la regla cruzada."""
    return TeamService(
        TeamRepository(db),
        PokemonRepository(db),
        PokedexRepository(db),
    )


@router.get("/", response_model=list[TeamRead])
async def list_teams(
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    return await service.list_teams(user.id)


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    try:
        return await service.create_team(user.id, data)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.get("/{team_id}", response_model=TeamDetail)
async def get_team(
    team_id: int,
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    try:
        team = await service.get_team_detail(user.id, team_id)
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipo no encontrado")
    return team


@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(
    team_id: int,
    data: TeamUpdate,
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    try:
        team = await service.update_team(user.id, team_id, data)
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipo no encontrado")
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    try:
        deleted = await service.delete_team(user.id, team_id)
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipo no encontrado")


@router.post(
    "/{team_id}/pokemons",
    response_model=TeamPokemonRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_pokemon(
    team_id: int,
    data: TeamPokemonCreate,
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    try:
        team_pokemon = await service.add_pokemon(user.id, team_id, data)
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    if team_pokemon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipo o Pokémon no encontrado")
    return team_pokemon


@router.patch("/{team_id}/pokemons/{team_pokemon_id}", response_model=TeamPokemonRead)
async def update_pokemon_slot(
    team_id: int,
    team_pokemon_id: int,
    data: TeamPokemonUpdate,
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    try:
        team_pokemon = await service.update_pokemon_slot(
            user.id, team_id, team_pokemon_id, data
        )
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    if team_pokemon is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipo o Pokémon no encontrado")
    return team_pokemon


@router.delete("/{team_id}/pokemons/{team_pokemon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_pokemon(
    team_id: int,
    team_pokemon_id: int,
    user: User = Depends(get_current_user),
    service: TeamService = Depends(get_service),
):
    try:
        removed = await service.remove_pokemon(user.id, team_id, team_pokemon_id)
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    if not removed:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipo o Pokémon no encontrado")
