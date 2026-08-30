from app.features.auth.models import User
from app.features.auth.repository import UserRepository
from app.features.auth.schemas import UserCreate, UserUpdate
from app.features.auth.security import create_access_token, hash_password, verify_password


class AuthService:
    """
    Capa de reglas de negocio.
    NO importa FastAPI. Si lanza errores de negocio, usa ValueError.
    El router se encargará de traducirlos a códigos HTTP.
    """

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, data: UserCreate) -> User:
        # email es único: duplicado => 409
        if await self.repository.get_by_email(data.email):
            raise ValueError(f"Ya existe un usuario con el email '{data.email}'")
        return await self.repository.create(data, hash_password(data.password))

    async def login(self, email: str, password: str) -> str:
        user = await self.repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            # Credenciales inválidas: el router lo traduce a 401 en login
            raise PermissionError("Credenciales inválidas")
        return create_access_token(user.id)

    async def get_user(self, user_id: int) -> User | None:
        return await self.repository.get_by_id(user_id)

    async def update_user(self, user: User, data: UserUpdate) -> User:
        hashed_password = hash_password(data.password) if data.password is not None else None
        return await self.repository.update(user, data, hashed_password)
