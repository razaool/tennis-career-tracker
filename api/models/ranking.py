"""
Ranking-related Pydantic models
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class RankingEntry(BaseModel):
    """Single ranking entry"""
    rank: int
    name: str
    rating: int
    uncertainty: Optional[float] = None
    form: Optional[float] = None
    last_match: Optional[date] = None
    change_7d: Optional[int] = None
    change_30d: Optional[int] = None


class RankingResponse(BaseModel):
    """Rankings list response"""
    as_of_date: date
    system: str
    total_ranked: int
    rankings: List[RankingEntry]

