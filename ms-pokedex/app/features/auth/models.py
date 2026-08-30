from app.core.database import Base, TimestampMixin

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # El password nunca se guarda en claro: solo su hash (bcrypt)
    hashed_password: Mapped[str] = mapped_column(String(255))
