FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copiar dependencias primero (optimización de caché)
COPY ms-pokedex/pyproject.toml ms-pokedex/uv.lock ./

# Instalar con uv (sin dev deps)
RUN uv sync --frozen --no-dev

# Copiar código de la app
COPY ms-pokedex/app/ ./app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]