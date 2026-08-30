from app.features.pokedex.repository import PokedexRepository
from app.features.pokemon.repository import PokemonRepository
from app.features.teams.models import Team
from app.features.teams.repository import TeamRepository
from app.features.teams.schemas import (
    TeamCreate,
    TeamDetail,
    TeamPokemonCreate,
    TeamPokemonRead,
    TeamPokemonUpdate,
    TeamUpdate,
)


class TeamService:
    """
    Capa de reglas de negocio.
    NO importa FastAPI. Si lanza errores de negocio, usa ValueError.
    Si falta permiso (equipo ajeno), usa PermissionError.
    El router se encargará de traducirlos a códigos HTTP.
    """

    def __init__(
        self,
        repository: TeamRepository,
        pokemon_repository: PokemonRepository,
        pokedex_repository: PokedexRepository,
    ):
        self.repository = repository
        self.pokemon_repository = pokemon_repository
        self.pokedex_repository = pokedex_repository

    # ---- helpers de construcción de DTOs (vienen de joins con pokemons) ----

    @staticmethod
    def _to_team_pokemon_read(row) -> TeamPokemonRead:
        # La fila viene del join: (TeamPokemon, pokeapi_id, name, photo_url)
        tp, pokeapi_id, name, photo_url = row
        return TeamPokemonRead(
            id=tp.id,
            team_id=tp.team_id,
            pokeapi_id=pokeapi_id,
            name=name,
            photo_url=photo_url,
            slot=tp.slot,
            created_at=tp.created_at,
        )

    @staticmethod
    def _to_team_detail(team: Team, pokemons: list[TeamPokemonRead]) -> TeamDetail:
        return TeamDetail(
            id=team.id,
            name=team.name,
            description=team.description,
            user_id=team.user_id,
            created_at=team.created_at,
            updated_at=team.updated_at,
            pokemons=pokemons,
        )

    # ---- Team ----

    async def list_teams(self, user_id: int) -> list[Team]:
        return await self.repository.list_by_user(user_id)

    async def create_team(self, user_id: int, data: TeamCreate) -> Team:
        if await self.repository.get_by_user_and_name(user_id, data.name):
            raise ValueError(f"Ya existe un equipo llamado '{data.name}'")
        return await self.repository.create(user_id, data)

    async def get_team_detail(self, user_id: int, team_id: int) -> TeamDetail | None:
        team = await self.repository.get_by_id(team_id)
        if team is None:
            return None
        if team.user_id != user_id:
            raise PermissionError("No tienes permiso sobre este equipo")
        pokemons = [
            self._to_team_pokemon_read(row)
            for row in await self.repository.list_pokemons_with_pokemon(team_id)
        ]
        return self._to_team_detail(team, pokemons)

    async def update_team(self, user_id: int, team_id: int, data: TeamUpdate) -> Team | None:
        team = await self.repository.get_by_id(team_id)
        if team is None:
            return None
        if team.user_id != user_id:
            raise PermissionError("No tienes permiso sobre este equipo")
        if data.name is not None and data.name != team.name:
            if await self.repository.get_by_user_and_name(user_id, data.name):
                raise ValueError(f"Ya existe un equipo llamado '{data.name}'")
        return await self.repository.update(team, data)

    async def delete_team(self, user_id: int, team_id: int) -> bool:
        team = await self.repository.get_by_id(team_id)
        if team is None:
            return False
        if team.user_id != user_id:
            raise PermissionError("No tienes permiso sobre este equipo")
        await self.repository.delete(team)
        return True

    # ---- TeamPokemon ----

    async def add_pokemon(
        self,
        user_id: int,
        team_id: int,
        data: TeamPokemonCreate,
    ) -> TeamPokemonRead | None:
        team = await self.repository.get_by_id(team_id)
        if team is None:
            return None
        if team.user_id != user_id:
            raise PermissionError("No tienes permiso sobre este equipo")
        pokemon = await self.pokemon_repository.get_by_pokeapi_id(data.pokeapi_id)
        if pokemon is None:
            # No existe en la tabla pokemons: el router traduce None a 404
            return None
        if await self.repository.get_pokemon_by_team_slot(team_id, data.slot):
            raise ValueError(f"El slot {data.slot} ya está ocupado")

        # Regla cruzada: si la especie no está en la Pokédex del usuario, se registra sola
        if not await self.pokedex_repository.get_by_user_and_pokemon(user_id, pokemon.id):
            await self.pokedex_repository.create(user_id, pokemon.id)

        tp = await self.repository.add_pokemon(team_id, pokemon.id, data.slot)
        return self._to_team_pokemon_read(
            (tp, pokemon.pokeapi_id, pokemon.name, pokemon.photo_url)
        )

    async def update_pokemon_slot(
        self,
        user_id: int,
        team_id: int,
        team_pokemon_id: int,
        data: TeamPokemonUpdate,
    ) -> TeamPokemonRead | None:
        team = await self.repository.get_by_id(team_id)
        if team is None:
            return None
        if team.user_id != user_id:
            raise PermissionError("No tienes permiso sobre este equipo")
        tp = await self.repository.get_pokemon_by_id(team_pokemon_id)
        if tp is None or tp.team_id != team_id:
            return None
        if data.slot is not None and data.slot != tp.slot:
            if await self.repository.get_pokemon_by_team_slot(team_id, data.slot):
                raise ValueError(f"El slot {data.slot} ya está ocupado")
            tp = await self.repository.update_pokemon_slot(tp, data.slot)
        pokemon = await self.pokemon_repository.get_by_id(tp.pokemon_id)
        if pokemon is None:
            return None
        return self._to_team_pokemon_read(
            (tp, pokemon.pokeapi_id, pokemon.name, pokemon.photo_url)
        )

    async def remove_pokemon(
        self,
        user_id: int,
        team_id: int,
        team_pokemon_id: int,
    ) -> bool:
        team = await self.repository.get_by_id(team_id)
        if team is None:
            return False
        if team.user_id != user_id:
            raise PermissionError("No tienes permiso sobre este equipo")
        tp = await self.repository.get_pokemon_by_id(team_pokemon_id)
        if tp is None or tp.team_id != team_id:
            return False
        await self.repository.delete_pokemon(tp)
        return True
