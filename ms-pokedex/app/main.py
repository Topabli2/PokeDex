from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.features.auth.models import User  # noqa: F401 (registra el modelo en Base.metadata)
from app.features.auth.router import router as auth_router
from app.features.auth.router import users_router as auth_users_router
from app.features.pokedex.models import Pokedex  # noqa: F401 (registra el modelo en Base.metadata)
from app.features.pokedex.router import router as pokedex_router
from app.features.pokemon.models import Pokemon  # noqa: F401 (registra el modelo en Base.metadata)
from app.features.pokemon.router import router as pokemon_router
from app.features.teams.models import Team, TeamPokemon  # noqa: F401 (registra el modelo en Base.metadata)
from app.features.teams.router import router as teams_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Pokedex API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(auth_users_router)
app.include_router(teams_router)
app.include_router(pokedex_router)
app.include_router(pokemon_router)


@app.get("/health")
async def health():
    return {"status": "ok"}