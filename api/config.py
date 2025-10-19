"""
API Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # API Info
    API_TITLE: str = "Tennis Career Tracker API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = """
    🎾 Tennis Career Tracker API
    
    The ultimate tennis analytics platform - track players across eras, 
    compare rating systems, analyze career trajectories, and predict match outcomes.
    
    ## Features
    
    * **Players**: Complete player profiles, career trajectories, statistics
    * **Rankings**: Current, all-time, by surface, by era
    * **Comparison**: Side-by-side player comparisons, head-to-head records
    * **Analysis**: GOAT debate, NextGen tracker, era comparisons
    * **Predictions**: Match outcome predictions with detailed factors
    * **Leaderboards**: Top performers in various categories
    
    ## Data Coverage
    
    * 2.68M matches (1968-2025)
    * 28,986 players tracked
    * 3 rating systems (ELO, TSR, Glicko-2)
    * 5.36M rating calculations
    """
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "tennis_tracker")
    DB_USER: str = os.getenv("DB_USER", "razaool")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        if self.DB_PASSWORD:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # API docs
        "http://localhost:5173",  # Vite dev server
    ]
    
    # Cache
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    CACHE_TTL: int = 3600  # 1 hour
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 500
    
    # Prediction defaults
    DEFAULT_SURFACE: str = "hard"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()

