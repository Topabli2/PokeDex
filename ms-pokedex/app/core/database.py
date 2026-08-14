from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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