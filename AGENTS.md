# AGENTS.md

Personal learning project (Spanish-speaking author). Repo comments are in Spanish — keep new comments/commits in Spanish.

## Layout

- `ms-pokedex/` — the only app: FastAPI, Python >=3.12, dependency-managed with `uv` (`pyproject.toml` + `uv.lock`). Entrypoint: `app/main.py` (app object `app.main:app`).
- `infra/docker-compose.yml` — `api` + `db` (Postgres 16). Compose project name: `pokedex`.
- `Dockerfile` — repo root, builds `ms-pokedex` with `uv sync --frozen --no-dev`.

## Run

`uv` and `docker` are not installed on the dev machine; the app is run via Docker:

- `docker compose -f infra/docker-compose.yml up --build` (compose file lives in `infra/`, so `-f` is required)
- API: http://localhost:8000 , healthcheck endpoint: `/health` (the compose healthcheck depends on it — do not remove/rename)
- DB is reachable by the API at `db:5432`; `DATABASE_URL` is set in compose.

Local (non-Docker) dev would be `uv run uvicorn app.main:app --reload` from `ms-pokedex/`.

## Gotchas

- No tests or lint/typecheck tooling configured yet. Don't assume pytest/ruff/mypy exist.
- There is no DB driver in `dependencies` yet (only `fastapi`). `DATABASE_URL` is set in compose but the app does not connect to Postgres — adding DB code means first adding the driver via `uv add` (updates `pyproject.toml` + `uv.lock`; the Dockerfile installs with `--frozen --no-dev`, so commit both).
- `.env` is gitignored; only `.env.example` is tracked. Never commit `.env`. Compose falls back to `devpassword123` for `DB_PASSWORD` if unset.
- Workflow: feature branches (prefixed, e.g. `infra/...`), PRs merged into `main`.
