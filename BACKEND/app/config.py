# Configuration Settings
# Generated from Prompt 15

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/stu_mini_db"
    
    # JWT
    jwt_secret: str = "your-super-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # API Keys
    gemini_api_key: str
    nvidia_nim_api_key: str
    pinecone_api_key: str
    pinecone_environment: str
    jsearch_api_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
