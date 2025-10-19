"""
Player endpoints - OPTIMIZED VERSION
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database import Database
from ..models.player import PlayerSummary, PlayerDetail
from ..config import settings

router = APIRouter()


@router.get("/", response_model=dict)
async def list_players(
    limit: int = Query(default=100, le=settings.MAX_PAGE_SIZE),
    offset: int = Query(default=0, ge=0),
    active: Optional[bool] = None,
    min_elo: Optional[int] = None,
    sort_by: str = Query(default="elo", regex="^(elo|name|matches)$")
):
    """
    List all players (paginated)
    
    - **limit**: Results per page (max 500)
    - **offset**: Pagination offset
    - **active**: Filter by active status (played in last 6 months)
    - **min_elo**: Minimum ELO rating
    - **sort_by**: Sort field (elo, name, matches)
    """
    
    # Fast query using materialized view
    query = """
        SELECT 
            p.name,
            plr.elo_rating as current_elo,
            plr.elo_rating as peak_elo,  -- Simplified for now
            0 as career_matches,  -- Simplified for now
            0 as grand_slams,
            CASE 
                WHEN plr.last_match >= CURRENT_DATE - INTERVAL '6 months' 
                THEN true 
                ELSE false 
            END as is_active,
            plr.last_match
        FROM players p
        INNER JOIN player_latest_ratings plr ON p.player_id = plr.player_id
        WHERE 1=1
    """
    
    params = []
    
    # Add filters
    if active is not None:
        if active:
            query += " AND plr.last_match >= CURRENT_DATE - INTERVAL '6 months'"
        else:
            query += " AND plr.last_match < CURRENT_DATE - INTERVAL '6 months'"
    
    if min_elo:
        query += " AND plr.elo_rating >= %s"
        params.append(min_elo)
    
    # Add sorting
    sort_column = {
        "elo": "plr.elo_rating",
        "name": "p.name",
        "matches": "plr.elo_rating"  # Fallback to ELO
    }.get(sort_by, "plr.elo_rating")
    
    query += f" ORDER BY {sort_column} DESC NULLS LAST"
    
    # Add pagination
    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    # Execute query
    try:
        players = Database.execute_query(query, tuple(params))
        
        # Get total count (simple)
        count_query = """
            SELECT COUNT(DISTINCT pr.player_id) as total 
            FROM player_ratings pr
            WHERE pr.elo_rating IS NOT NULL
        """
        total_result = Database.execute_one(count_query)
        total = total_result['total'] if total_result else 0
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "players": players
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{player_name}", response_model=dict)
async def get_player(player_name: str):
    """
    Get complete player profile
    
    - **player_name**: Player name (URL-encoded)
    """
    
    # Decode name
    player_name = player_name.replace("%20", " ").replace("+", " ")
    
    # Fast query using materialized view
    query = """
        WITH player_info AS (
            SELECT player_id FROM players WHERE name = %s
        ),
        peak_ratings AS (
            SELECT 
                MAX(elo_rating) as peak_elo,
                MAX(tsr_rating) as peak_tsr,
                MAX(glicko2_rating) as peak_glicko2
            FROM player_ratings
            WHERE player_id = (SELECT player_id FROM player_info)
        ),
        match_count AS (
            SELECT COUNT(*) as total_matches
            FROM player_ratings
            WHERE player_id = (SELECT player_id FROM player_info)
        )
        SELECT 
            p.name,
            EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.date_of_birth) as age,
            p.country,
            p.turned_pro,
            CASE 
                WHEN plr.last_match >= CURRENT_DATE - INTERVAL '6 months' 
                THEN true 
                ELSE false 
            END as is_active,
            plr.elo_rating as current_elo,
            plr.tsr_rating as current_tsr,
            plr.tsr_uncertainty,
            plr.glicko2_rating as current_glicko2,
            plr.glicko2_rd,
            pr.peak_elo,
            pr.peak_tsr,
            pr.peak_glicko2,
            plr.form_index,
            plr.big_match_rating,
            plr.tournament_success_score,
            mc.total_matches,
            0 as wins,
            0 as losses
        FROM players p
        JOIN player_info pi ON true
        LEFT JOIN player_latest_ratings plr ON plr.player_id = pi.player_id
        LEFT JOIN peak_ratings pr ON true
        LEFT JOIN match_count mc ON true
        WHERE p.player_id = pi.player_id
    """
    
    try:
        player = Database.execute_one(query, (player_name,))
        
        if not player:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
        # Calculate win percentage (simplified)
        total = player['total_matches'] or 0
        win_pct = 0.0  # We'll calculate this properly later
        
        # Format response
        return {
            "name": player['name'],
            "age": int(player['age']) if player['age'] else None,
            "country": player['country'],
            "turned_pro": player['turned_pro'],
            "is_active": player['is_active'],
            "ratings": {
                "current": {
                    "elo": int(player['current_elo']) if player['current_elo'] else None,
                    "tsr": int(player['current_tsr']) if player['current_tsr'] else None,
                    "tsr_uncertainty": round(float(player['tsr_uncertainty']), 1) if player['tsr_uncertainty'] else None,
                    "glicko2": int(player['current_glicko2']) if player['current_glicko2'] else None,
                    "glicko2_rd": round(float(player['glicko2_rd']), 1) if player['glicko2_rd'] else None
                },
                "peak": {
                    "elo": int(player['peak_elo']) if player['peak_elo'] else None,
                    "tsr": int(player['peak_tsr']) if player['peak_tsr'] else None,
                    "glicko2": int(player['peak_glicko2']) if player['peak_glicko2'] else None
                }
            },
            "career_stats": {
                "total_matches": total,
                "wins": player['wins'],
                "losses": player['losses'],
                "win_percentage": win_pct
            },
            "current_metrics": {
                "form_index": round(float(player['form_index']), 1) if player['form_index'] else None,
                "big_match_rating": round(float(player['big_match_rating']), 2) if player['big_match_rating'] else None,
                "tournament_success": round(float(player['tournament_success_score']), 1) if player['tournament_success_score'] else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{player_name}/trajectory", response_model=dict)
async def get_player_trajectory(
    player_name: str,
    system: str = Query(default="all", regex="^(all|elo|tsr|glicko2)$"),
    limit: Optional[int] = Query(default=None, le=5000)
):
    """
    Get player's complete career trajectory for charting
    
    - **player_name**: Player name (URL-encoded)
    - **system**: Rating system (all, elo, tsr, glicko2)
    - **limit**: Limit data points (useful for large careers)
    """
    
    # Decode name
    player_name = player_name.replace("%20", " ").replace("+", " ")
    
    # Build column selection based on system
    if system == "elo":
        columns = "elo_rating, NULL as tsr_rating, NULL as glicko2_rating"
    elif system == "tsr":
        columns = "NULL as elo_rating, tsr_rating, tsr_uncertainty, tsr_smoothed, NULL as glicko2_rating"
    elif system == "glicko2":
        columns = "NULL as elo_rating, NULL as tsr_rating, glicko2_rating, glicko2_rd"
    else:  # all
        columns = "elo_rating, tsr_rating, tsr_uncertainty, tsr_smoothed, glicko2_rating, glicko2_rd"
    
    query = f"""
        SELECT 
            career_match_number as match_number,
            date,
            {columns}
        FROM player_ratings
        WHERE player_id = (SELECT player_id FROM players WHERE name = %s)
        ORDER BY career_match_number ASC
    """
    
    params = [player_name]
    
    if limit:
        query += " LIMIT %s"
        params.append(limit)
    
    try:
        trajectory = Database.execute_query(query, tuple(params))
        
        if not trajectory:
            raise HTTPException(status_code=404, detail=f"No data found for player '{player_name}'")
        
        return {
            "player": player_name,
            "total_matches": len(trajectory),
            "data_points": trajectory
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
