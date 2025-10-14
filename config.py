"""
Configuration settings for the Tennis Career Tracker
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Create directories if they don't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "tennis_tracker"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# Database connection string for SQLAlchemy
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Tennis Abstract GitHub repository URLs
TENNIS_ABSTRACT_REPOS = {
    "atp": "https://github.com/JeffSackmann/tennis_atp.git",
    "wta": "https://github.com/JeffSackmann/tennis_wta.git",
}

# Tournament tier weights for Bayesian model
TOURNAMENT_TIERS = {
    "Grand Slam": {"weight": 2.0, "importance": 100},
    "ATP Finals": {"weight": 1.8, "importance": 90},
    "Masters 1000": {"weight": 1.5, "importance": 80},
    "Masters": {"weight": 1.5, "importance": 80},  # Alias
    "ATP 500": {"weight": 1.2, "importance": 60},
    "ATP 250": {"weight": 1.0, "importance": 40},
    "Davis Cup": {"weight": 1.3, "importance": 70},
    "Olympics": {"weight": 1.6, "importance": 85},
    "Challenger": {"weight": 0.8, "importance": 30},
    "ITF": {"weight": 0.6, "importance": 20},
}

# Surface types
SURFACES = ["clay", "grass", "hard", "carpet"]

# Initial ELO rating for new players
INITIAL_ELO = 1500

# K-factor for ELO calculations (will vary by tournament tier)
BASE_K_FACTOR = 32

