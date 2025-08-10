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
        # Use .env file in the project root directory
        env_file="../.env",
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
        # Base origins from settings
        origins = [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]
        
        # Add frontend host
        if self.FRONTEND_HOST:
            origins.append(self.FRONTEND_HOST.rstrip("/"))
        
        # Add production domains for Render deployment
        production_origins = [
            "https://ivanintech.com",
            "https://www.ivanintech.com",
            "https://ivanintech.onrender.com",
            "https://www.ivanintech.onrender.com"
        ]
        
        # Add production origins if not already present
        for origin in production_origins:
            if origin not in origins:
                origins.append(origin)
        
        return origins

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
        # Queries generales de IA
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
        "AI ethics",
        "AI explainability",
        "AI chips",
        "AI hardware",
        "AI open source",
        "AI LLM",
        "AI multimodal",
        "AI agent",
        
        # IA en Salud y Medicina
        "AI healthcare",
        "AI medicine",
        "AI medical",
        "AI diagnosis",
        "AI treatment",
        "AI drug discovery",
        "AI pharmaceutical",
        "AI clinical",
        "AI patient care",
        "AI medical imaging",
        "AI radiology",
        "AI pathology",
        "AI genomics",
        "AI precision medicine",
        "AI telemedicine",
        "AI health tech",
        "AI medical devices",
        "AI wearable health",
        "AI mental health",
        "AI neurology",
        "AI cardiology",
        "AI oncology",
        "AI surgery",
        "AI robotic surgery",
        
        # IA en Código Abierto
        "open source AI",
        "AI open source",
        "open source machine learning",
        "AI framework",
        "AI library",
        "AI model open source",
        "AI code open source",
        "AI software open source",
        "AI tools open source",
        "AI platform open source",
        "AI research open source",
        "AI community open source",
        "AI collaboration open source",
        "AI development open source",
        "AI innovation open source",
        "AI democratization",
        "AI accessibility",
        "AI for everyone",
        "AI education open source",
        "AI learning open source",
        
        # IA en Robótica
        "AI robotics",
        "AI robot",
        "robotic AI",
        "AI automation",
        "AI autonomous",
        "AI autonomous vehicle",
        "AI self-driving",
        "AI drone",
        "AI drone technology",
        "AI industrial robot",
        "AI service robot",
        "AI humanoid robot",
        "AI robot arm",
        "AI robot navigation",
        "AI robot vision",
        "AI robot learning",
        "AI robot control",
        "AI robot safety",
        "AI robot ethics",
        "AI robot collaboration",
        "AI cobot",
        "AI collaborative robot",
        "AI robot manufacturing",
        "AI robot warehouse",
        "AI robot delivery",
        "AI robot healthcare",
        "AI robot surgery",
        "AI robot agriculture",
        "AI robot space",
        "AI robot underwater",
        "AI robot aerial",
        
        # IA en Ciencia
        "AI science",
        "AI scientific research",
        "AI physics",
        "AI chemistry",
        "AI biology",
        "AI astronomy",
        "AI space research",
        "AI climate science",
        "AI environmental",
        "AI materials science",
        "AI nanotechnology",
        "AI biotechnology",
        "AI neuroscience",
        "AI cognitive science",
        "AI psychology",
        "AI social science",
        "AI economics",
        "AI mathematics",
        "AI statistics",
        "AI data science",
        "AI scientific discovery",
        "AI research breakthrough",
        "AI scientific innovation",
        "AI laboratory",
        "AI experiment",
        "AI simulation",
        "AI modeling",
        "AI prediction science",
        "AI forecasting",
        "AI scientific analysis",
        "AI research tool",
        
        # IA en Sectores Específicos
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
        "AI in gaming",
        "AI in security",
        "AI in privacy",
        "AI in law",
        "AI in government",
        "AI in society",
        "AI in business",
        "AI in research",
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
        
        # Queries específicas para eventos importantes
        "ChatGPT",
        "OpenAI",
        "AI latest",
        "OpenAI latest",
        "Anthropic Claude",
        "Claude",
        "Google Gemini",
        "Gemini Advanced",
        "Meta AI",
        "Microsoft Copilot",
        "AI safety",
        "AI regulation",
        "AI legislation",
        "AI copyright",
        "AI lawsuit",
        "AI investment",
        "AI funding",
        "AI unicorn",
        "AI IPO",
        "AI acquisition",
        "AI merger",
        "AI partnership",
        "AI collaboration",
        "AI competition",
        "AI race",
        "AI arms race",
        "AI superintelligence",
        "AGI",
        "artificial general intelligence",
        
        # Eventos Trending y Noticias que Cambian el Mundo
        "AI breakthrough",
        "AI revolution",
        "AI transformation",
        "AI disruption",
        "AI paradigm shift",
        "AI game changer",
        "AI milestone",
        "AI achievement",
        "AI advancement",
        "AI progress",
        "AI development",
        "AI evolution",
        "AI innovation breakthrough",
        "AI scientific breakthrough",
        "AI medical breakthrough",
        "AI technological breakthrough",
        "AI research breakthrough",
        "AI discovery",
        "AI invention",
        "AI creation",
        "AI new technology",
        "AI cutting edge",
        "AI state of the art",
        "AI latest development",
        "AI recent breakthrough",
        "AI major announcement",
        "AI big news",
        "AI important news",
        "AI significant development",
        "AI world changing",
        "AI life changing",
        "AI society changing",
        "AI industry changing",
        "AI future changing",
        "AI revolutionary",
        "AI transformative",
        "AI disruptive",
        "AI groundbreaking",
        "AI pioneering",
        "AI trailblazing",
        "AI innovative",
        "AI creative",
        "AI novel",
        "AI unique",
        "AI unprecedented",
        "AI first time",
        "AI never before",
        "AI history making",
        "AI record breaking",
        "AI world record",
        "AI fastest",
        "AI most powerful",
        "AI most advanced",
        "AI best",
        "AI top",
        "AI leading",
        "AI premier",
        "AI flagship",
        "AI crown jewel",
        "AI masterpiece",
        "AI masterpiece",
        "AI perfect",
        "AI flawless",
        "AI exceptional",
        "AI extraordinary",
        "AI remarkable",
        "AI amazing",
        "AI incredible",
        "AI unbelievable",
        "AI mind blowing",
        "AI jaw dropping",
        "AI eye opening",
        "AI thought provoking",
        "AI inspiring",
        "AI motivating",
        "AI encouraging",
        "AI hopeful",
        "AI optimistic",
        "AI positive",
        "AI beneficial",
        "AI helpful",
        "AI useful",
        "AI valuable",
        "AI precious",
        "AI important",
        "AI significant",
        "AI meaningful",
        "AI relevant",
        "AI timely",
        "AI current",
        "AI present",
        "AI now",
        "AI today",
        "AI this week",
        "AI this month",
        "AI this year",
        "AI 2024",
        "AI 2025",
        "AI future",
        "AI tomorrow",
        "AI next generation",
        "AI next level",
        "AI next step",
        "AI next phase",
        "AI next era",
        "AI new era",
        "AI new age",
        "AI new world",
        "AI new reality",
        "AI new normal",
        "AI new standard",
        "AI new benchmark",
        "AI new reference",
        "AI new model",
        "AI new approach",
        "AI new method",
        "AI new technique",
        "AI new strategy",
        "AI new solution",
        "AI new answer",
        "AI new way",
        "AI new path",
        "AI new direction",
        "AI new focus",
        "AI new priority",
        "AI new goal",
        "AI new target",
        "AI new objective",
        "AI new mission",
        "AI new vision",
        "AI new dream",
        "AI new hope",
        "AI new promise",
        "AI new potential",
        "AI new possibility",
        "AI new opportunity",
        "AI new chance",
        "AI new beginning",
        "AI new start",
        "AI new chapter",
        "AI new page",
        "AI new story",
        "AI new narrative",
        "AI new tale",
        "AI new legend",
        "AI new myth",
        "AI new folklore",
        "AI new tradition",
        "AI new culture",
        "AI new society",
        "AI new civilization",
        "AI new humanity",
        "AI new species",
        "AI new life",
        "AI new existence",
        "AI new being",
        "AI new consciousness",
        "AI new awareness",
        "AI new understanding",
        "AI new knowledge",
        "AI new wisdom",
        "AI new insight",
        "AI new perspective",
        "AI new viewpoint",
        "AI new angle",
        "AI new approach",
        "AI new method",
        "AI new technique",
        "AI new strategy",
        "AI new solution",
        "AI new answer",
        "AI new way",
        "AI new path",
        "AI new direction",
        "AI new focus",
        "AI new priority",
        "AI new goal",
        "AI new target",
        "AI new objective",
        "AI new mission",
        "AI new vision",
        "AI new dream",
        "AI new hope",
        "AI new promise",
        "AI new potential",
        "AI new possibility",
        "AI new opportunity",
        "AI new chance",
        "AI new beginning",
        "AI new start",
        "AI new chapter",
        "AI new page",
        "AI new story",
        "AI new narrative",
        "AI new tale",
        "AI new legend",
        "AI new myth",
        "AI new folklore",
        "AI new tradition",
        "AI new culture",
        "AI new society",
        "AI new civilization",
        "AI new humanity",
        "AI new species",
        "AI new life",
        "AI new existence",
        "AI new being",
        "AI new consciousness",
        "AI new awareness",
        "AI new understanding",
        "AI new knowledge",
        "AI new wisdom",
        "AI new insight",
        "AI new perspective",
        "AI new viewpoint",
        "AI new angle",
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
        # Google News (funcionan bien)
        "https://news.google.com/rss/search?q=artificial+intelligence",
        "https://news.google.com/rss/search?q=ai+startup+OR+artificial+intelligence+startup",
        "https://news.google.com/rss/search?q=quantum+ai+OR+quantum+computing+ai",
        "https://news.google.com/rss/search?q=AI+healthcare+OR+AI+medicine",
        "https://news.google.com/rss/search?q=AI+robotics+OR+AI+robot",
        "https://news.google.com/rss/search?q=open+source+AI+OR+AI+open+source",
        "https://news.google.com/rss/search?q=AI+science+OR+AI+research",
        "https://news.google.com/rss/search?q=AI+breakthrough+OR+AI+innovation",
        
        # TechCrunch AI (funciona bien)
        "https://techcrunch.com/tag/artificial-intelligence/feed/",
        "https://techcrunch.com/tag/healthcare/feed/",
        "https://techcrunch.com/tag/robotics/feed/",
        
        # VentureBeat AI (funciona bien)
        "https://venturebeat.com/category/ai/feed/",
        "https://venturebeat.com/category/health/feed/",
        "https://venturebeat.com/category/robotics/feed/",
        
        # The Next Web - URL corregida
        "https://thenextweb.com/feed/",
        
        # MIT Technology Review (general, filtrar IA en procesamiento)
        "https://www.technologyreview.com/feed/",
        
        # Quantum Computing Report
        "https://quantumcomputingreport.com/feed/",
        
        # Reddit feeds (funcionan bien)
        "https://www.reddit.com/r/MachineLearning/.rss",
        "https://www.reddit.com/r/artificial/.rss",
        "https://www.reddit.com/r/QuantumComputing/.rss",
        "https://www.reddit.com/r/startups/.rss",
        "https://www.reddit.com/r/healthcare/.rss",
        "https://www.reddit.com/r/robotics/.rss",
        "https://www.reddit.com/r/opensource/.rss",
        "https://www.reddit.com/r/science/.rss",
        "https://www.reddit.com/r/Futurology/.rss",
        "https://www.reddit.com/r/technology/.rss",
        
        # Hacker News (funcionan bien)
        "https://hnrss.org/newest?q=ai",
        "https://hnrss.org/newest?q=quantum",
        "https://hnrss.org/newest?q=healthcare",
        "https://hnrss.org/newest?q=robotics",
        "https://hnrss.org/newest?q=open+source",
        "https://hnrss.org/newest?q=science",
        "https://hnrss.org/newest?q=breakthrough",
        "https://hnrss.org/newest?q=innovation",
        
        # AI Business (más confiable)
        "https://aibusiness.com/feed/",
        
        # Wired AI (confiable)
        "https://www.wired.com/feed/rss",
        
        # Ars Technica (confiable)
        "https://feeds.arstechnica.com/arstechnica/index",
        
        # Feeds específicos de salud y medicina
        "https://www.healthcareitnews.com/rss.xml",
        "https://www.fiercebiotech.com/rss/xml",
        "https://www.fiercepharma.com/rss/xml",
        "https://www.medcitynews.com/feed/",
        
        # Feeds de robótica
        "https://www.robohub.org/feed/",
        "https://www.robotics.org/feed/",
        "https://www.robots.com/feed/",
        
        # Feeds de código abierto
        "https://opensource.com/feed",
        "https://www.linuxfoundation.org/feed/",
        "https://www.gnu.org/software/feed.xml",
        
        # Feeds de ciencia
        "https://www.nature.com/nature.rss",
        "https://www.science.org/rss/news_current.xml",
        "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
        "https://www.sciencedaily.com/rss/health_medicine.xml",
        "https://www.sciencedaily.com/rss/technology.xml",
        
        # Feeds de innovación y tecnología
        "https://www.fastcompany.com/feed",
        "https://www.inc.com/rss/",
        "https://www.forbes.com/innovation/feed/",
        "https://www.wired.com/feed/rss",
        "https://www.theverge.com/rss/index.xml",
        "https://www.engadget.com/rss.xml",
        "https://www.gizmodo.com/rss",
        "https://www.mashable.com/feed.xml",
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
    
    # Firebase configuration variables (for frontend)
    NEXT_PUBLIC_FIREBASE_API_KEY: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_PROJECT_ID: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID: Optional[str] = None
    NEXT_PUBLIC_FIREBASE_APP_ID: Optional[str] = None

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
