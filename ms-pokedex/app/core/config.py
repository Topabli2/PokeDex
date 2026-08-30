from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Lee variables de entorno y archivo .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Si existe la variable DATABASE_URL en el entorno (Docker), la usa.
    # Si no, usa este default para desarrollo local.
    database_url: str = "postgresql+asyncpg://pokedex:devpassword123@localhost:5432/pokedex"
    app_env: str = "development"

    # JWT: clave para firmar/verificar tokens y tiempo de expiración
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60


settings = Settings()