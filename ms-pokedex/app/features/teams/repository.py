from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.pokemon.models import Pokemon
from app.features.teams.models import Team, TeamPokemon
from app.features.teams.schemas import TeamCreate, TeamUpdate


class TeamRepository:
    """
    Capa de acceso a datos.
    Recibe la sesión por inyección (la presta FastAPI vía get_db).
    Solo sabe hablar con la base de datos. No sabe de reglas de negocio ni de HTTP.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---- Team ----

    async def list_by_user(self, user_id: int) -> list[Team]:
        result = await self.session.execute(
            select(Team).where(Team.user_id == user_id).order_by(Team.id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, team_id: int) -> Team | None:
        result = await self.session.execute(
            select(Team).where(Team.id == team_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_name(self, user_id: int, name: str) -> Team | None:
        result = await self.session.execute(
            select(Team).where(Team.user_id == user_id, Team.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, data: TeamCreate) -> Team:
        team = Team(user_id=user_id, **data.model_dump())
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        return team

    async def update(self, team: Team, data: TeamUpdate) -> Team:
        # Solo los campos que el cliente SÍ envió
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(team, field, value)
        await self.session.commit()
        await self.session.refresh(team)
        return team

    async def delete(self, team: Team) -> None:
        await self.session.delete(team)
        await self.session.commit()

    # ---- TeamPokemon ----

    async def get_pokemon_by_team_slot(self, team_id: int, slot: int) -> TeamPokemon | None:
        result = await self.session.execute(
            select(TeamPokemon).where(
                TeamPokemon.team_id == team_id,
                TeamPokemon.slot == slot,
            )
        )
        return result.scalar_one_or_none()

    async def get_pokemon_by_id(self, team_pokemon_id: int) -> TeamPokemon | None:
        result = await self.session.execute(
            select(TeamPokemon).where(TeamPokemon.id == team_pokemon_id)
        )
        return result.scalar_one_or_none()

    async def add_pokemon(self, team_id: int, pokemon_id: int, slot: int) -> TeamPokemon:
        team_pokemon = TeamPokemon(team_id=team_id, pokemon_id=pokemon_id, slot=slot)
        self.session.add(team_pokemon)
        await self.session.commit()
        await self.session.refresh(team_pokemon)
        return team_pokemon

    async def update_pokemon_slot(self, team_pokemon: TeamPokemon, slot: int) -> TeamPokemon:
        team_pokemon.slot = slot
        await self.session.commit()
        await self.session.refresh(team_pokemon)
        return team_pokemon

    async def delete_pokemon(self, team_pokemon: TeamPokemon) -> None:
        await self.session.delete(team_pokemon)
        await self.session.commit()

    async def list_pokemons_with_pokemon(self, team_id: int) -> list:
        # Une con pokemons para traer pokeapi_id, name y photo_url en la misma consulta
        result = await self.session.execute(
            select(TeamPokemon, Pokemon.pokeapi_id, Pokemon.name, Pokemon.photo_url)
            .join(Pokemon, Pokemon.id == TeamPokemon.pokemon_id)
            .where(TeamPokemon.team_id == team_id)
            .order_by(TeamPokemon.slot)
        )
        return list(result.all())
