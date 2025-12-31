"""
Core Configuration & Settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application Settings"""
    
    # App Info
    app_name: str = "Hister 2.0"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # Spotify API
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str = "http://localhost:8000/callback"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated string to list"""
        return [origin.strip() for origin in self.allowed_origins.split(',')]
    
    # Database
    database_url: str = "sqlite:///./hister.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton Instance
settings = Settings()
