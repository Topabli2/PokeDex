from app.core.database import Base, TimestampMixin

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON

class Pokemon(TimestampMixin, Base):
    __tablename__ = "pokemons"

    id: Mapped[int] = mapped_column(primary_key=True)
    pokeapi_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    types: Mapped[list] = mapped_column(JSON)
    photo_url: Mapped[str|None] = mapped_column(String(255))