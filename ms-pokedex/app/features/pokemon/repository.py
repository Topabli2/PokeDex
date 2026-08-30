from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.pokemon.models import Pokemon
from app.features.pokemon.schemas import PokemonCreate, PokemonUpdate


class PokemonRepository:
    """
    Capa de acceso a datos.
    Recibe la sesión por inyección (la presta FastAPI vía get_db).
    Solo sabe hablar con la base de datos. No sabe de reglas de negocio ni de HTTP.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pokemon_id: int) -> Pokemon | None:
        result = await self.session.execute(
            select(Pokemon).where(Pokemon.id == pokemon_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Pokemon | None:
        result = await self.session.execute(
            select(Pokemon).where(Pokemon.name == name)
        )
        return result.scalar_one_or_none()

    async def get_by_pokeapi_id(self, pokeapi_id: int) -> Pokemon | None:
        result = await self.session.execute(
            select(Pokemon).where(Pokemon.pokeapi_id == pokeapi_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Pokemon]:
        result = await self.session.execute(
            select(Pokemon).order_by(Pokemon.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: PokemonCreate) -> Pokemon:
        pokemon = Pokemon(**data.model_dump())
        self.session.add(pokemon)          # lo mete al "carrito"
        await self.session.commit()        # lo manda a la DB
        await self.session.refresh(pokemon)  # recarga el objeto con id y fechas generadas
        return pokemon

    async def update(self, pokemon: Pokemon, data: PokemonUpdate) -> Pokemon:
        # Solo los campos que el cliente SÍ envió
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(pokemon, field, value)
        await self.session.commit()
        await self.session.refresh(pokemon)
        return pokemon

    async def delete(self, pokemon: Pokemon) -> None:
        await self.session.delete(pokemon)
        await self.session.commit()