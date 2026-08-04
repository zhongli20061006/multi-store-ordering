from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "多门店点单后端"
    database_url: str = "sqlite:///./data/ordering.db"
    jwt_secret: str = "dev-only-secret-please-override-in-env-0123456789"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    seed_admin_username: str = "admin"
    seed_admin_password: str = "admin123456"
    cors_origins: str = "*"


settings = Settings()
