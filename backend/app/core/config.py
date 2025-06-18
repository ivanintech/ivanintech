import secrets
import warnings
from typing import Annotated, Any, Literal, List, Optional
import os
from pathlib import Path

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self
from fastapi_mail import ConnectionConfig


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use .env file in the current directory (backend/)
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:3000"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
    SENTRY_DSN: str | None = None
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    DATABASE_URL: Optional[str] = None
    SQLITE_DB_FILE: str = "ivanintech.db"
    GITHUB_TOKEN: Optional[str] = ""

    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: EmailStr | None = None
    MAIL_PORT: int = 587
    MAIL_SERVER: str | None = None
    MAIL_FROM_NAME: str = "Iván In Tech Web"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    @model_validator(mode="after")
    def _set_default_mail_from_name(self) -> Self:
        if not self.MAIL_FROM_NAME:
            self.MAIL_FROM_NAME = self.PROJECT_NAME
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.MAIL_SERVER and self.MAIL_USERNAME and self.MAIL_FROM)

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    NEWSAPI_API_KEY: str | None = None

    # --- Gemini API --- #
    GEMINI_API_KEY: Optional[str] = None

    # --- YouTube API --- #
    YOUTUBE_API_KEY: Optional[str] = None

    # --- Añadir claves para GNews y Currents ---
    GNEWS_API_KEY: Optional[str] = None
    CURRENTS_API_KEY: Optional[str] = None
    EVENT_REGISTRY_API_KEY: Optional[str] = None

    # --- Añadir claves para APITube y Mediastack ---
    APITUBE_API_KEY: Optional[str] = None
    MEDIASTACK_API_KEY: Optional[str] = None

    # --- Control de ejecución de scripts ---
    RUN_DB_RESET_ON_STARTUP: bool = False

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        if self.POSTGRES_SERVER:
            self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self

    @property
    def fm_connection_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.MAIL_USERNAME,
            MAIL_PASSWORD=self.MAIL_PASSWORD,
            MAIL_FROM=self.MAIL_FROM,
            MAIL_PORT=self.MAIL_PORT,
            MAIL_SERVER=self.MAIL_SERVER,
            MAIL_FROM_NAME=self.MAIL_FROM_NAME,
            MAIL_STARTTLS=self.MAIL_STARTTLS,
            MAIL_SSL_TLS=self.MAIL_SSL_TLS,
            USE_CREDENTIALS=self.USE_CREDENTIALS,
            VALIDATE_CERTS=self.VALIDATE_CERTS,
            TEMPLATE_FOLDER=None
        )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            if "postgresql" in self.DATABASE_URL and not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            elif "sqlite" in self.DATABASE_URL and not self.DATABASE_URL.startswith("sqlite+aiosqlite:///"):
                return self.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
            return self.DATABASE_URL
            
        elif self.POSTGRES_SERVER and self.POSTGRES_USER and self.POSTGRES_DB:
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        else:
            # Construir la ruta absoluta usando pathlib
            # Asume que config.py está en backend/app/core
            # Sube 2 niveles para llegar a backend/
            project_root = Path(__file__).resolve().parents[2] 
            sqlite_path = project_root / self.SQLITE_DB_FILE
            # Convertir a formato URI compatible con Windows/Linux
            sqlite_url_path = sqlite_path.as_uri().replace("file:///","").replace("\\\\\\\\", "/")
            final_url = f"sqlite+aiosqlite:///{sqlite_url_path}"
            print("---" * 20)
            print(f"CONECTANDO A LA BASE DE DATOS EN: {final_url}")
            print("---" * 20)
            return final_url


settings = Settings()
