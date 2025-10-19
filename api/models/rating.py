"""
Rating-related Pydantic models
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class RatingPoint(BaseModel):
    """Single rating data point"""
    match_number: int
    date: date
    elo: Optional[int] = None
    tsr: Optional[int] = None
    tsr_uncertainty: Optional[float] = None
    glicko2: Optional[int] = None
    glicko2_rd: Optional[float] = None


class RatingSummary(BaseModel):
    """Summary of ratings for a system"""
    current: Optional[int] = None
    peak: Optional[int] = None
    peak_date: Optional[date] = None
    current_rank: Optional[int] = None
    peak_rank: Optional[int] = None


class SurfaceRating(BaseModel):
    """Surface-specific rating"""
    current: Optional[int] = None
    peak: Optional[int] = None


class SurfaceRatings(BaseModel):
    """All surface ratings"""
    clay: Optional[SurfaceRating] = None
    grass: Optional[SurfaceRating] = None
    hard: Optional[SurfaceRating] = None

