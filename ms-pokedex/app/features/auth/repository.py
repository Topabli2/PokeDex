from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.auth.schemas import UserCreate, UserUpdate


class UserRepository:
    """
    Capa de acceso a datos.
    Recibe la sesión por inyección (la presta FastAPI vía get_db).
    Solo sabe hablar con la base de datos. No sabe de reglas de negocio ni de HTTP.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, data: UserCreate, hashed_password: str) -> User:
        # El hash llega ya calculado desde el service (regla de negocio)
        user = User(name=data.name, email=data.email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, data: UserUpdate, hashed_password: str | None = None) -> User:
        # Solo los campos que el cliente SÍ envió
        if data.name is not None:
            user.name = data.name
        if hashed_password is not None:
            user.hashed_password = hashed_password
        await self.session.commit()
        await self.session.refresh(user)
        return user
