"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "eidosSec"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_CONCURRENT_SCANS_PRO: int = 10
    MAX_PROJECTS_PRO: int = 100
    MAX_PROJECTS_SOLO: int = 3
    MAX_CONCURRENT_SCANS_SOLO: int = 1
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Optional integrations
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GITHUB_TOKEN: str = ""
    
    # Feature flags
    ENABLE_TELEMETRY: bool = False
    ENABLE_AI_FEATURES: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_secrets(self):
        """Validate that critical secrets are set and strong"""
        if self.SECRET_KEY == "changeme" or len(self.SECRET_KEY) < 32:
            import logging
            import sys
            logger = logging.getLogger(__name__)
            msg = "FATAL SECURITY ERROR: SECRET_KEY is weak or using default value. Application will not start without a strong SECRET_KEY (min 32 chars)."
            logger.critical(msg)
            if self.ENVIRONMENT == "production":
                print(msg)
                sys.exit(1)
            else:
                logger.warning("Continuing in development mode, but FIX THIS before deployment.")


# Global settings instance
settings = Settings()
