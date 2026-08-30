from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.models import User
from app.features.auth.security import get_current_user
from app.features.pokedex.repository import PokedexRepository
from app.features.pokedex.schemas import PokedexCreate, PokedexRead
from app.features.pokedex.service import PokedexService
from app.features.pokemon.repository import PokemonRepository

router = APIRouter(prefix="/pokedex", tags=["pokedex"])


def get_service(db: AsyncSession = Depends(get_db)) -> PokedexService:
    """Por cada petición: sesión fresca → repository → service."""
    return PokedexService(
        PokedexRepository(db),
        PokemonRepository(db),
    )


@router.get("/", response_model=list[PokedexRead])
async def list_pokedex(
    user: User = Depends(get_current_user),
    service: PokedexService = Depends(get_service),
):
    return await service.list_pokedex(user.id)


@router.post("/", response_model=PokedexRead, status_code=status.HTTP_201_CREATED)
async def add_pokemon(
    data: PokedexCreate,
    user: User = Depends(get_current_user),
    service: PokedexService = Depends(get_service),
):
    try:
        entry = await service.add_pokemon(user.id, data)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pokémon no encontrado")
    return entry
