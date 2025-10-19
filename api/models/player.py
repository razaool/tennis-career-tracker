"""
Player-related Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class PlayerSummary(BaseModel):
    """Simplified player info for lists"""
    name: str
    current_elo: Optional[int] = None
    peak_elo: Optional[int] = None
    career_matches: Optional[int] = None
    grand_slams: Optional[int] = None
    is_active: bool = False
    last_match: Optional[date] = None
    
    class Config:
        from_attributes = True


class RatingCurrent(BaseModel):
    """Current ratings across all systems"""
    elo: Optional[int] = None
    tsr: Optional[int] = None
    tsr_uncertainty: Optional[float] = None
    glicko2: Optional[int] = None
    glicko2_rd: Optional[float] = None


class RatingPeak(BaseModel):
    """Peak ratings across all systems"""
    elo: Optional[int] = None
    elo_date: Optional[date] = None
    tsr: Optional[int] = None
    tsr_uncertainty: Optional[float] = None
    glicko2: Optional[int] = None
    glicko2_date: Optional[date] = None


class CareerStats(BaseModel):
    """Career statistics"""
    total_matches: int
    wins: int
    losses: int
    win_percentage: float
    career_span: str


class Achievements(BaseModel):
    """Player achievements"""
    grand_slams: int = 0
    masters_1000: int = 0
    atp_500: int = 0
    atp_250: int = 0


class CurrentMetrics(BaseModel):
    """Current performance metrics"""
    form_index: Optional[float] = None
    big_match_rating: Optional[float] = None
    tournament_success: Optional[float] = None


class SurfaceRating(BaseModel):
    """Surface-specific rating"""
    current: Optional[int] = None
    peak: Optional[int] = None


class SurfaceRatings(BaseModel):
    """Ratings broken down by surface"""
    clay: Optional[SurfaceRating] = None
    grass: Optional[SurfaceRating] = None
    hard: Optional[SurfaceRating] = None


class PlayerDetail(BaseModel):
    """Complete player details"""
    name: str
    age: Optional[int] = None
    country: Optional[str] = None
    turned_pro: Optional[int] = None
    is_active: bool
    
    ratings: Optional[dict] = None  # RatingCurrent + RatingPeak
    career_stats: Optional[CareerStats] = None
    achievements: Optional[Achievements] = None
    current_metrics: Optional[CurrentMetrics] = None
    surface_ratings: Optional[SurfaceRatings] = None
    
    class Config:
        from_attributes = True


class TrajectoryPoint(BaseModel):
    """Single point in career trajectory"""
    match_number: int
    date: date
    elo: Optional[int] = None
    tsr: Optional[int] = None
    tsr_uncertainty: Optional[float] = None
    tsr_smoothed: Optional[float] = None
    glicko2: Optional[int] = None
    glicko2_rd: Optional[float] = None


class PlayerTrajectory(BaseModel):
    """Career trajectory data for charting"""
    player: str
    total_matches: int
    data_points: List[TrajectoryPoint]


class PlayerStats(BaseModel):
    """Detailed statistics"""
    player: str
    ratings_summary: dict
    surface_breakdown: dict
    form_metrics: dict
    big_match_performance: dict
    achievements: dict
    career_progression: dict


class PlayerSearch(BaseModel):
    """Player search result"""
    name: str
    match_score: float = Field(..., ge=0, le=1, description="Match quality 0-1")
    current_elo: Optional[int] = None
    is_active: bool
    grand_slams: int = 0

