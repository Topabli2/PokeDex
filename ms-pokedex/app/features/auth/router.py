from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.models import User
from app.features.auth.repository import UserRepository
from app.features.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.features.auth.security import get_current_user
from app.features.auth.service import AuthService

# Dos routers: los endpoints de registro/login van bajo /auth
# y los del perfil propio bajo /users (protegidos).
router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["auth"])


def get_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Por cada petición: sesión fresca → repository → service."""
    return AuthService(UserRepository(db))


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    service: AuthService = Depends(get_service),
):
    try:
        return await service.register(data)
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_service),
):
    try:
        access_token = await service.login(data.email, data.password)
    except PermissionError as e:
        # En login, credenciales malas son 401 (no 403)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))
    return TokenResponse(access_token=access_token)


@users_router.get("/me", response_model=UserRead)
async def get_me(
    user: User = Depends(get_current_user),
):
    return user


@users_router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    service: AuthService = Depends(get_service),
):
    return await service.update_user(user, data)
