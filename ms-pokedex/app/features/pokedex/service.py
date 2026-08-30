from app.features.pokedex.models import Pokedex
from app.features.pokedex.repository import PokedexRepository
from app.features.pokedex.schemas import PokedexCreate, PokedexRead
from app.features.pokemon.repository import PokemonRepository


class PokedexService:
    """
    Capa de reglas de negocio.
    NO importa FastAPI. Si lanza errores de negocio, usa ValueError.
    El router se encargará de traducirlos a códigos HTTP.
    """

    def __init__(
        self,
        repository: PokedexRepository,
        pokemon_repository: PokemonRepository,
    ):
        self.repository = repository
        self.pokemon_repository = pokemon_repository

    @staticmethod
    def _to_read(row) -> PokedexRead:
        # La fila viene del join: (Pokedex, pokeapi_id, name, photo_url)
        entry, pokeapi_id, name, photo_url = row
        return PokedexRead(
            pokeapi_id=pokeapi_id,
            name=name,
            photo_url=photo_url,
            date_found=entry.date_found,
        )

    async def list_pokedex(self, user_id: int) -> list[PokedexRead]:
        return [self._to_read(row) for row in await self.repository.list_for_user(user_id)]

    async def add_pokemon(self, user_id: int, data: PokedexCreate) -> PokedexRead | None:
        pokemon = await self.pokemon_repository.get_by_pokeapi_id(data.pokeapi_id)
        if pokemon is None:
            # No está en la tabla pokemons: el router traduce None a 404
            return None
        if await self.repository.get_by_user_and_pokemon(user_id, pokemon.id):
            raise ValueError(f"La especie '{pokemon.name}' ya estaba en tu Pokédex")
        entry = await self.repository.create(user_id, pokemon.id)
        return self._to_read((entry, pokemon.pokeapi_id, pokemon.name, pokemon.photo_url))
