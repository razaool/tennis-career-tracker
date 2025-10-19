"""
Rankings endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
from ..database import Database
from ..config import settings

router = APIRouter()


@router.get("/current", response_model=dict)
async def get_current_rankings(
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
    system: str = Query(default="elo", regex="^(elo|tsr|glicko2)$"),
    active: Optional[bool] = True
):
    """
    Get current rankings
    
    - **limit**: Number of players to return (max 500)
    - **offset**: Pagination offset
    - **system**: Rating system (elo, tsr, glicko2)
    - **active**: Only active players (default: true)
    """
    
    # Select rating column based on system
    rating_column = {
        "elo": "plr.elo_rating",
        "tsr": "plr.tsr_rating",
        "glicko2": "plr.glicko2_rating"
    }.get(system, "plr.elo_rating")
    
    query = f"""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY {rating_column} DESC) as rank,
            p.name,
            plr.elo_rating as elo,
            plr.tsr_rating as tsr,
            plr.tsr_uncertainty as uncertainty,
            plr.glicko2_rating as glicko2,
            plr.form_index as form,
            plr.last_match
        FROM players p
        INNER JOIN player_latest_ratings plr ON p.player_id = plr.player_id
        WHERE {rating_column} IS NOT NULL
    """
    
    params = []
    
    if active:
        query += " AND plr.last_match >= CURRENT_DATE - INTERVAL '6 months'"
    
    query += f" ORDER BY {rating_column} DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    try:
        rankings = Database.execute_query(query, tuple(params))
        
        # Get last match date for "as_of_date"
        last_match_query = "SELECT MAX(last_match) as last_date FROM player_latest_ratings"
        last_match_result = Database.execute_one(last_match_query)
        as_of_date = last_match_result['last_date'] if last_match_result else date.today()
        
        return {
            "as_of_date": str(as_of_date),
            "system": system,
            "total_ranked": len(rankings),
            "rankings": rankings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

