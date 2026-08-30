from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.pokedex.models import Pokedex
from app.features.pokemon.models import Pokemon


class PokedexRepository:
    """
    Capa de acceso a datos.
    Recibe la sesión por inyección (la presta FastAPI vía get_db).
    Solo sabe hablar con la base de datos. No sabe de reglas de negocio ni de HTTP.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_and_pokemon(self, user_id: int, pokemon_id: int) -> Pokedex | None:
        result = await self.session.execute(
            select(Pokedex).where(
                Pokedex.user_id == user_id,
                Pokedex.pokemon_id == pokemon_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list:
        # Une con pokemons para traer pokeapi_id, name y photo_url en la misma consulta
        result = await self.session.execute(
            select(Pokedex, Pokemon.pokeapi_id, Pokemon.name, Pokemon.photo_url)
            .join(Pokemon, Pokemon.id == Pokedex.pokemon_id)
            .where(Pokedex.user_id == user_id)
            .order_by(Pokedex.date_found)
        )
        return list(result.all())

    async def create(self, user_id: int, pokemon_id: int) -> Pokedex:
        entry = Pokedex(user_id=user_id, pokemon_id=pokemon_id)
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry
