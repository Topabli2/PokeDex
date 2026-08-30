from app.features.pokemon.models import Pokemon
from app.features.pokemon.repository import PokemonRepository
from app.features.pokemon.schemas import PokemonCreate, PokemonUpdate


class PokemonService:
    """
    Capa de reglas de negocio.
    NO importa FastAPI. Si lanza errores de negocio, usa ValueError.
    El router se encargará de traducirlos a códigos HTTP.
    """

    def __init__(self, repository: PokemonRepository):
            self.repository = repository

    async def list_pokemons(self, skip: int = 0, limit: int = 100) -> list[Pokemon]:
        return await self.repository.list_all(skip, limit)

    async def get_pokemon(self, pokeapi_id: int) -> Pokemon | None:
        return await self.repository.get_by_pokeapi_id(pokeapi_id)

    async def create_pokemon(self, data: PokemonCreate) -> Pokemon:
        if await self.repository.get_by_name(data.name):
            raise ValueError(f"Ya existe un Pokémon con el nombre '{data.name}'")
        if await self.repository.get_by_pokeapi_id(data.pokeapi_id):
            raise ValueError(f"Ya existe un Pokémon con pokeapi_id {data.pokeapi_id}")
        return await self.repository.create(data)

    async def update_pokemon(self, pokeapi_id: int, data: PokemonUpdate) -> Pokemon | None:
        pokemon = await self.repository.get_by_pokeapi_id(pokeapi_id)
        if pokemon is None:
            return None
        if data.name is not None and data.name != pokemon.name:
            if await self.repository.get_by_name(data.name):
                raise ValueError(f"Ya existe un Pokémon con el nombre '{data.name}'")
        return await self.repository.update(pokemon, data)

    async def delete_pokemon(self, pokeapi_id: int) -> bool:
        pokemon = await self.repository.get_by_pokeapi_id(pokeapi_id)
        if pokemon is None:
            return False
        await self.repository.delete(pokemon)
        return True