from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Supabase
    supabase_url: str
    supabase_service_role_key: str
    # Optional: JWT secret for verifying Supabase tokens (production)
    supabase_jwt_secret: str | None = None
    
    # LLM Provider
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    
    # Search
    tavily_api_key: str | None = None
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    
    # Token limits
    max_tokens_per_response: int = 2000
    max_conversation_length: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
