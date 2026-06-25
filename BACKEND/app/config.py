from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Base Settings
    APP_NAME: str = "StudHelper"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/studhelper",
        description="PostgreSQL connection string"
    )
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20

    # JWT & Authentication
    SECRET_KEY: str = Field(
        default="your-super-secret-jwt-key-must-be-very-long-and-secure",
        description="JWT signing key"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Keys & External Services (Allow empty defaults to validate manually)
    GOOGLE_API_KEY: str = Field(default="", description="Google Gemini API key")
    NVIDIA_API_KEY: str = Field(default="", description="NVIDIA NIM API key")
    PINECONE_API_KEY: str = Field(default="", description="Pinecone database API key")
    PINECONE_INDEX_NAME: str = "studhelper"
    JSEARCH_API_KEY: str = Field(default="", description="JSearch API key")
    
    # OAuth configuration
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = Field(default=None, description="Google OAuth Client ID")
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = Field(default=None, description="Google OAuth Client Secret")

    # Admin configuration
    ADMIN_API_KEY: str = Field(default="", description="Admin routes API key")

    # Storage Configuration
    STORAGE_PATH: str = "/data/digilocker"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    MAX_STORAGE_PER_USER: int = 500 * 1024 * 1024

    # Interview Configuration
    MAX_INTERVIEW_QUESTIONS: int = 7
    MAX_INTERVIEW_DURATION_HOURS: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def model_post_init(self, __context):
        self.validate_config()

    def validate_config(self) -> None:
        """
        Validate database schemas, API keys, and JWT configurations.
        """
        # Validate Required API keys and configurations
        if not self.SECRET_KEY or self.SECRET_KEY == "your-super-secret-jwt-key-must-be-very-long-and-secure":
            # For local testing, allow it but raise if empty
            if not self.SECRET_KEY:
                raise ValueError("SECRET_KEY not set")
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY length must be at least 32 characters")

        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL not set")
        if not (self.DATABASE_URL.startswith("postgresql://") or self.DATABASE_URL.startswith("postgres://")):
            raise ValueError("DATABASE_URL must start with postgresql:// or postgres://")

        # Required API keys validation
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set")
        if not self.NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY not set")
        if not self.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not set")
        if not self.JSEARCH_API_KEY:
            raise ValueError("JSEARCH_API_KEY not set")
        if not self.ADMIN_API_KEY:
            raise ValueError("ADMIN_API_KEY not set")

    # Properties to maintain backwards-compatibility with lowercase usage in other modules
    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def jwt_secret(self) -> str:
        return self.SECRET_KEY

    @property
    def jwt_algorithm(self) -> str:
        return self.ALGORITHM

    @property
    def jwt_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def gemini_api_key(self) -> str:
        return self.GOOGLE_API_KEY

    @property
    def nvidia_nim_api_key(self) -> str:
        return self.NVIDIA_API_KEY

    @property
    def pinecone_api_key(self) -> str:
        return self.PINECONE_API_KEY

    @property
    def pinecone_environment(self) -> str:
        # Default environment fallback
        return "us-east-1"

    @property
    def jsearch_api_key(self) -> str:
        return self.JSEARCH_API_KEY

    @property
    def jsearch_host(self) -> str:
        return "jsearch.p.rapidapi.com"

    @property
    def environment(self) -> str:
        return "development" if self.DEBUG else "production"


settings = Settings()


