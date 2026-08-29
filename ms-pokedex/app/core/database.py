from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


# ============================================================================
# CONEXIÓN A LA BASE DE DATOS
# ============================================================================

# El "puente" hacia PostgreSQL. echo=True imprime el SQL en consola (útil aprendiendo)
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    echo=True
)

# Fábrica de sesiones. Versión 2.0 de lo que tu amigo escribió con sessionmaker()
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # los objetos siguen usables tras el commit (clave en APIs)
)


async def get_db():
    """
    Dependency de FastAPI: presta una sesión por petición y la cierra al terminar.
    Se usará así en los routers:  db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        yield session

class Base(DeclarativeBase):
    """
    Clase base de la cual heredarán TODOS los modelos de todas las features.
    """
    pass

class TimestampMixin:
    """
    Mixin para inyectar created_at y updated_at automáticamente.
    """
    
    # server_default=func.now() -> La DB pone la fecha al crear
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        nullable=False
    )
    
    # onupdate=func.now() -> La DB/SQLAlchemy actualiza la fecha al modificar
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )