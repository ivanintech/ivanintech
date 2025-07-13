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
        env_file_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_HOST: str = "http://localhost:8000"
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

    FORCE_SQLITE: bool = False

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
    USERS_OPEN_REGISTRATION: bool = True

    NEWSAPI_API_KEY: str | None = None

    # --- Gemini API --- #
    GEMINI_API_KEY: Optional[str] = None

    # --- Mistral API --- #
    MISTRAL_API_KEY: Optional[str] = None

    # --- YouTube API --- #
    YOUTUBE_API_KEY: Optional[str] = None

    # --- Añadir claves para GNews y Currents ---
    GNEWS_API_KEY: Optional[str] = None
    CURRENTS_API_KEY: Optional[str] = None
    EVENT_REGISTRY_API_KEY: Optional[str] = None

    # --- Añadir claves para APITube y Mediastack ---
    APITUBE_API_KEY: Optional[str] = None
    MEDIASTACK_API_KEY: Optional[str] = None
    # Lista de consultas para las APIs de noticias
    NEWS_QUERIES: List[str] = [
        "artificial intelligence",
        "AI startup",
        "machine learning",
        "deep learning",
        "generative AI",
        "quantum AI",
        "quantum computing",
        "AI innovation",
        "AI breakthrough",
        "AI research",
        "AI robotics",
        "AI healthcare",
        "AI ethics",
        "AI explainability",
        "AI chips",
        "AI hardware",
        "AI open source",
        "AI LLM",
        "AI multimodal",
        "AI agent",
        "AI in industry",
        "AI in startups",
        "AI in quantum",
        "AI in robotics",
        "AI in medicine",
        "AI in finance",
        "AI in education",
        "AI in creativity",
        "AI in art",
        "AI in music",
        "AI in video",
        "AI in gaming",
        "AI in security",
        "AI in privacy",
        "AI in law",
        "AI in government",
        "AI in society",
        "AI in business",
        "AI in science",
        "AI in research",
        "AI in startups",
        "AI in quantum computing",
        "AI in edge computing",
        "AI in cloud",
        "AI in data center",
        "AI in hardware",
        "AI in chips",
        "AI in sensors",
        "AI in IoT",
        "AI in blockchain",
        "AI in web3",
        "AI in metaverse",
        "AI in AR",
        "AI in VR",
        "AI in XR",
        "AI in drones",
        "AI in autonomous vehicles",
        "AI in space",
        "AI in biotech",
        "AI in nanotech",
        "AI in quantum tech",
        "AI in crazy innovation",
        "AI in disruptive tech",
        "AI in next-gen tech",
        "AI in future tech",
    ]

    # Lista de Feeds RSS para obtener noticias adicionales
    NEWS_RSS_FEEDS: List[str] = [
        # Google News
        "https://news.google.com/rss/search?q=artificial+intelligence",
        "https://news.google.com/rss/search?q=ai+startup+OR+artificial+intelligence+startup",
        "https://news.google.com/rss/search?q=quantum+ai+OR+quantum+computing+ai",
        # TechCrunch AI
        "https://techcrunch.com/tag/artificial-intelligence/feed/",
        # VentureBeat AI
        "https://venturebeat.com/category/ai/feed/",
        # The Next Web AI
        "https://thenextweb.com/feed/tag/artificial-intelligence",
        # MIT Technology Review (general, filtrar IA en procesamiento)
        "https://www.technologyreview.com/feed/",
        # Quantum Computing Report
        "https://quantumcomputingreport.com/feed/",
        # Reddit Machine Learning
        "https://www.reddit.com/r/MachineLearning/.rss",
        # Reddit Artificial
        "https://www.reddit.com/r/artificial/.rss",
        # Reddit Quantum Computing
        "https://www.reddit.com/r/QuantumComputing/.rss",
        # Reddit Startups
        "https://www.reddit.com/r/startups/.rss",
        # Hacker News AI
        "https://hnrss.org/newest?q=ai",
        # Hacker News Quantum
        "https://hnrss.org/newest?q=quantum",
    ]

    # --- Supabase Configuration ---
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # --- Control de ejecución de scripts ---
    RUN_DB_RESET_ON_STARTUP: bool = False

    # New environment variables for social logins
    GOOGLE_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

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
        if self.FORCE_SQLITE:
            project_root = Path(__file__).resolve().parents[2] 
            sqlite_path = project_root / self.SQLITE_DB_FILE
            sqlite_url_path = sqlite_path.as_uri().replace("file:///","").replace("\\\\\\\\", "/")
            return f"sqlite+aiosqlite:///{sqlite_url_path}"

        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Fallback to building the URL from components, ensuring async driver
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"{self.POSTGRES_DB}"
            )
        )


settings = Settings()
