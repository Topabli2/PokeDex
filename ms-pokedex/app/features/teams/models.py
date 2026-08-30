from app.core.database import Base, TimestampMixin

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint


class Team(TimestampMixin, Base):
    __tablename__ = "teams"
    __table_args__ = (
        # Un usuario no puede tener dos equipos con el mismo nombre
        UniqueConstraint("user_id", "name", name="uq_teams_user_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))


class TeamPokemon(TimestampMixin, Base):
    __tablename__ = "team_pokemons"
    __table_args__ = (
        # Un equipo no puede tener dos Pokémon en el mismo slot
        UniqueConstraint("team_id", "slot", name="uq_team_pokemons_team_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemons.id", ondelete="CASCADE"))
    slot: Mapped[int] = mapped_column(Integer)
