from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str =  postgresql://user:password@localhost:5432/stu_mini_db
    SECRET_KEY: str = your-secret-key-change-in-production
    ALGORITHM: str = HS256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = [http://localhost:5173, http://localhost:3000]
    class Config:
        env_file = .env
        env_file_encoding = utf-8
        case_sensitive = True

settings = Settings()
