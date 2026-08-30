from datetime import datetime

from app.core.database import Base, TimestampMixin

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func


class Pokedex(TimestampMixin, Base):
    __tablename__ = "pokedex"
    __table_args__ = (
        # Un usuario no puede tener dos veces la misma especie registrada
        UniqueConstraint("user_id", "pokemon_id", name="uq_pokedex_user_pokemon"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemons.id", ondelete="CASCADE"))
    date_found: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
