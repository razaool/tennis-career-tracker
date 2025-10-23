"""
Rankings endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
from database import Database
from config import settings

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


@router.get("/surface/{surface}", response_model=dict)
async def get_surface_rankings(
    surface: str,
    limit: int = Query(default=100, le=500),
    active_only: bool = Query(default=True, description="Filter to active players only (played in 2025)")
):
    """
    Get rankings for specific surface (clay, grass, hard)
    
    - **surface**: Surface type (clay, grass, hard)
    - **limit**: Number of players to return (max 500)
    - **active_only**: Show only active players (played in 2025) - default: True
    
    Returns top players by surface-specific ELO rating
    """
    
    # Validate surface
    if surface not in ['clay', 'grass', 'hard']:
        raise HTTPException(status_code=400, detail="Surface must be: clay, grass, or hard")
    
    # Map surface to column name
    surface_column = f"elo_{surface}"
    
    # Build query with optional active filter
    date_filter = "AND pr.date >= '2025-01-01'" if active_only else ""
    
    query = f"""
        WITH latest_ratings AS (
            SELECT 
                player_id,
                MAX(career_match_number) as max_match
            FROM player_ratings
            GROUP BY player_id
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY pr.{surface_column} DESC) as rank,
            p.name,
            pr.{surface_column} as surface_rating,
            pr.elo_rating as overall_elo,
            pr.career_match_number as total_matches,
            pr.date as last_match
        FROM player_ratings pr
        JOIN latest_ratings lr ON pr.player_id = lr.player_id 
            AND pr.career_match_number = lr.max_match
        JOIN players p ON pr.player_id = p.player_id
        WHERE pr.{surface_column} IS NOT NULL
            {date_filter}
        ORDER BY pr.{surface_column} DESC
        LIMIT %s
    """
    
    try:
        rankings = Database.execute_query(query, (limit,))
        
        return {
            "surface": surface,
            "active_only": active_only,
            "total_ranked": len(rankings),
            "rankings": rankings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/historical", response_model=dict)
async def get_historical_rankings(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    limit: int = Query(default=10, le=100),
    rating_system: str = Query(default="elo", regex="^(elo|tsr|glicko2)$")
):
    """
    Get rankings at a specific historical date
    
    - **date**: Date in YYYY-MM-DD format (e.g., "2010-01-01")
    - **limit**: Number of players (max 100)
    - **rating_system**: Rating system (elo, tsr, glicko2)
    
    Returns: Top N players as of that date
    """
    
    # Select rating column
    rating_col = {
        "elo": "elo_rating",
        "tsr": "tsr_rating",
        "glicko2": "glicko2_rating"
    }.get(rating_system, "elo_rating")
    
    query = f"""
        WITH ratings_on_date AS (
            SELECT 
                pr.player_id,
                pr.{rating_col} as rating,
                pr.career_match_number,
                pr.date,
                ROW_NUMBER() OVER (PARTITION BY pr.player_id ORDER BY pr.date DESC, pr.career_match_number DESC) as rn
            FROM player_ratings pr
            WHERE pr.date <= %s
                AND pr.{rating_col} IS NOT NULL
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY rod.rating DESC) as rank,
            p.name,
            rod.rating,
            rod.date as last_match_before_date,
            rod.career_match_number as total_matches
        FROM ratings_on_date rod
        JOIN players p ON rod.player_id = p.player_id
        WHERE rod.rn = 1
        ORDER BY rod.rating DESC
        LIMIT %s
    """
    
    try:
        rankings = Database.execute_query(query, (date, limit))
        
        if not rankings:
            raise HTTPException(status_code=404, detail=f"No rating data available for date: {date}")
        
        return {
            "date": date,
            "rating_system": rating_system,
            "total_ranked": len(rankings),
            "rankings": rankings
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

