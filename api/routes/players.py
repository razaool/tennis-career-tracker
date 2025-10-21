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
        ),
        win_loss_stats AS (
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN m.winner_id = pi.player_id THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN m.winner_id != pi.player_id THEN 1 ELSE 0 END) as losses
            FROM player_ratings pr
            JOIN matches m ON pr.match_id = m.match_id
            JOIN player_info pi ON pi.player_id = pr.player_id
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
            wls.total_matches,
            wls.wins,
            wls.losses
        FROM players p
        JOIN player_info pi ON true
        LEFT JOIN player_latest_ratings plr ON plr.player_id = pi.player_id
        LEFT JOIN peak_ratings pr ON true
        LEFT JOIN win_loss_stats wls ON true
        WHERE p.player_id = pi.player_id
    """
    
    try:
        player = Database.execute_one(query, (player_name,))
        
        if not player:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
        # Calculate win percentage
        total = player['total_matches'] or 0
        wins = player['wins'] or 0
        win_pct = (wins / total * 100) if total > 0 else 0.0
        
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


@router.get("/{player_name}/titles", response_model=dict)
async def get_player_titles(player_name: str):
    """
    Get all tournament titles won by player, organized by tier
    
    - **player_name**: Player name (URL-encoded)
    
    Returns titles by tier with tournament details
    """
    
    # Decode name
    player_name = player_name.replace("%20", " ").replace("+", " ")
    
    query = """
        SELECT 
            m.date,
            m.tournament_name,
            m.tournament_tier,
            m.surface,
            p_opp.name as defeated_in_final,
            m.score
        FROM matches m
        JOIN players p ON m.winner_id = p.player_id
        JOIN players p_opp ON (CASE WHEN m.player1_id = p.player_id THEN m.player2_id ELSE m.player1_id END) = p_opp.player_id
        WHERE p.name = %s
            AND m.round = 'F'
        ORDER BY m.date DESC
    """
    
    try:
        titles = Database.execute_query(query, (player_name,))
        
        if not titles:
            return {
                "player": player_name,
                "total_titles": 0,
                "by_tier": {},
                "by_surface": {},
                "titles": []
            }
        
        # Group by tier
        by_tier = {}
        by_surface = {}
        
        for title in titles:
            tier = title['tournament_tier'] or 'Other'
            surf = title['surface'] or 'Unknown'
            
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(title)
            
            if surf not in by_surface:
                by_surface[surf] = []
            by_surface[surf].append(title)
        
        # Count by tier
        tier_counts = {tier: len(titles_list) for tier, titles_list in by_tier.items()}
        surface_counts = {surf: len(titles_list) for surf, titles_list in by_surface.items()}
        
        return {
            "player": player_name,
            "total_titles": len(titles),
            "by_tier": tier_counts,
            "by_surface": surface_counts,
            "titles": titles
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/compare/trajectory", response_model=dict)
async def compare_player_trajectories(
    players: str = Query(..., description="Comma-separated player names (e.g., 'Carlos Alcaraz,Jannik Sinner')"),
    start_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
    rating_system: str = Query(default="elo", regex="^(elo|tsr|glicko2)$")
):
    """
    Compare multiple players' trajectories over a specific date range
    
    - **players**: Comma-separated player names (e.g., "Carlos Alcaraz,Jannik Sinner,Novak Djokovic")
    - **start_date**: Optional start date (YYYY-MM-DD)
    - **end_date**: Optional end date (YYYY-MM-DD)
    - **rating_system**: Rating system to use (elo, tsr, glicko2)
    
    Examples:
    - Compare Alcaraz vs Sinner in 2024-2025
    - Compare Big 3 from 2010-2015
    - Compare NextGen from 2023 onwards
    """
    
    # Parse player names
    player_names = [p.strip() for p in players.split(',')]
    
    if len(player_names) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 players allowed")
    
    # Build column selection based on rating system
    if rating_system == "elo":
        rating_col = "elo_rating"
        extra_cols = ""
    elif rating_system == "tsr":
        rating_col = "tsr_rating"
        extra_cols = ", tsr_uncertainty, tsr_smoothed"
    else:  # glicko2
        rating_col = "glicko2_rating"
        extra_cols = ", glicko2_rd, glicko2_volatility"
    
    # Build query with date filters
    query = f"""
        SELECT 
            p.name,
            pr.career_match_number as match_number,
            pr.date,
            pr.{rating_col} as rating
            {extra_cols}
        FROM player_ratings pr
        JOIN players p ON pr.player_id = p.player_id
        WHERE p.name = ANY(%s)
            AND pr.{rating_col} IS NOT NULL
    """
    
    params = [player_names]
    
    if start_date:
        query += " AND pr.date >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND pr.date <= %s"
        params.append(end_date)
    
    query += " ORDER BY p.name, pr.career_match_number ASC"
    
    try:
        data = Database.execute_query(query, tuple(params))
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found for specified players and date range")
        
        # Group by player
        players_data = {}
        for row in data:
            name = row['name']
            if name not in players_data:
                players_data[name] = []
            players_data[name].append(row)
        
        return {
            "rating_system": rating_system,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "players": [
                {
                    "name": name,
                    "data_points": len(trajectory),
                    "trajectory": trajectory
                }
                for name, trajectory in players_data.items()
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{player_name}/titles", response_model=dict)
async def get_player_titles(player_name: str):
    """
    Get all tournament titles won by player, organized by tier
    
    - **player_name**: Player name (URL-encoded)
    
    Returns titles by tier with tournament details
    """
    
    # Decode name
    player_name = player_name.replace("%20", " ").replace("+", " ")
    
    query = """
        SELECT 
            m.date,
            m.tournament_name,
            m.tournament_tier,
            m.surface,
            p_opp.name as defeated_in_final,
            m.score
        FROM matches m
        JOIN players p ON m.winner_id = p.player_id
        JOIN players p_opp ON (CASE WHEN m.player1_id = p.player_id THEN m.player2_id ELSE m.player1_id END) = p_opp.player_id
        WHERE p.name = %s
            AND m.round = 'F'
        ORDER BY m.date DESC
    """
    
    try:
        titles = Database.execute_query(query, (player_name,))
        
        if not titles:
            return {
                "player": player_name,
                "total_titles": 0,
                "by_tier": {},
                "by_surface": {},
                "titles": []
            }
        
        # Group by tier
        by_tier = {}
        by_surface = {}
        
        for title in titles:
            tier = title['tournament_tier'] or 'Other'
            surf = title['surface'] or 'Unknown'
            
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(title)
            
            if surf not in by_surface:
                by_surface[surf] = []
            by_surface[surf].append(title)
        
        # Count by tier
        tier_counts = {tier: len(titles_list) for tier, titles_list in by_tier.items()}
        surface_counts = {surf: len(titles_list) for surf, titles_list in by_surface.items()}
        
        return {
            "player": player_name,
            "total_titles": len(titles),
            "by_tier": tier_counts,
            "by_surface": surface_counts,
            "titles": titles
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


@router.get("/{player_name}/titles", response_model=dict)
async def get_player_titles(player_name: str):
    """
    Get all tournament titles won by player, organized by tier
    
    - **player_name**: Player name (URL-encoded)
    
    Returns titles by tier with tournament details
    """
    
    # Decode name
    player_name = player_name.replace("%20", " ").replace("+", " ")
    
    query = """
        SELECT 
            m.date,
            m.tournament_name,
            m.tournament_tier,
            m.surface,
            p_opp.name as defeated_in_final,
            m.score
        FROM matches m
        JOIN players p ON m.winner_id = p.player_id
        JOIN players p_opp ON (CASE WHEN m.player1_id = p.player_id THEN m.player2_id ELSE m.player1_id END) = p_opp.player_id
        WHERE p.name = %s
            AND m.round = 'F'
        ORDER BY m.date DESC
    """
    
    try:
        titles = Database.execute_query(query, (player_name,))
        
        if not titles:
            return {
                "player": player_name,
                "total_titles": 0,
                "by_tier": {},
                "by_surface": {},
                "titles": []
            }
        
        # Group by tier
        by_tier = {}
        by_surface = {}
        
        for title in titles:
            tier = title['tournament_tier'] or 'Other'
            surf = title['surface'] or 'Unknown'
            
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(title)
            
            if surf not in by_surface:
                by_surface[surf] = []
            by_surface[surf].append(title)
        
        # Count by tier
        tier_counts = {tier: len(titles_list) for tier, titles_list in by_tier.items()}
        surface_counts = {surf: len(titles_list) for surf, titles_list in by_surface.items()}
        
        return {
            "player": player_name,
            "total_titles": len(titles),
            "by_tier": tier_counts,
            "by_surface": surface_counts,
            "titles": titles
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{player_name}/recent", response_model=dict)
async def get_recent_matches(
    player_name: str,
    limit: int = Query(default=20, le=100, description="Number of recent matches")
):
    """
    Get player's most recent matches
    
    - **player_name**: Player name (URL-encoded)
    - **limit**: Number of recent matches (max 100)
    
    Returns recent match results with opponents, tournaments, scores
    """
    
    # Decode name
    player_name = player_name.replace("%20", " ").replace("+", " ")
    
    query = """
        WITH player_matches AS (
            SELECT 
                m.date,
                m.tournament_name,
                m.tournament_tier,
                m.surface,
                m.round,
                m.score,
                CASE 
                    WHEN m.winner_id = p.player_id THEN 'Won'
                    ELSE 'Lost'
                END as result,
                CASE 
                    WHEN m.player1_id = p.player_id THEN p2.name
                    ELSE p1.name
                END as opponent,
                pr.elo_rating as player_elo,
                CASE 
                    WHEN m.player1_id = p.player_id THEN pr2.elo_rating
                    ELSE pr1.elo_rating
                END as opponent_elo
            FROM matches m
            JOIN players p ON (p.player_id = m.player1_id OR p.player_id = m.player2_id)
            LEFT JOIN players p1 ON m.player1_id = p1.player_id
            LEFT JOIN players p2 ON m.player2_id = p2.player_id
            LEFT JOIN player_ratings pr ON pr.match_id = m.match_id AND pr.player_id = p.player_id
            LEFT JOIN player_ratings pr1 ON pr1.match_id = m.match_id AND pr1.player_id = m.player1_id
            LEFT JOIN player_ratings pr2 ON pr2.match_id = m.match_id AND pr2.player_id = m.player2_id
            WHERE p.name = %s
            ORDER BY m.date DESC
            LIMIT %s
        )
        SELECT * FROM player_matches
    """
    
    try:
        matches = Database.execute_query(query, (player_name, limit))
        
        if not matches:
            raise HTTPException(status_code=404, detail=f"No matches found for player '{player_name}'")
        
        # Calculate summary stats
        wins = sum(1 for m in matches if m['result'] == 'Won')
        losses = len(matches) - wins
        win_pct = (wins / len(matches)) * 100 if matches else 0
        
        return {
            "player": player_name,
            "matches_shown": len(matches),
            "summary": {
                "wins": wins,
                "losses": losses,
                "win_percentage": round(win_pct, 1)
            },
            "matches": matches
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{player_name}/titles", response_model=dict)
async def get_player_titles(player_name: str):
    """
    Get all tournament titles won by player, organized by tier
    
    - **player_name**: Player name (URL-encoded)
    
    Returns titles by tier with tournament details
    """
    
    # Decode name
    player_name = player_name.replace("%20", " ").replace("+", " ")
    
    query = """
        SELECT 
            m.date,
            m.tournament_name,
            m.tournament_tier,
            m.surface,
            p_opp.name as defeated_in_final,
            m.score
        FROM matches m
        JOIN players p ON m.winner_id = p.player_id
        JOIN players p_opp ON (CASE WHEN m.player1_id = p.player_id THEN m.player2_id ELSE m.player1_id END) = p_opp.player_id
        WHERE p.name = %s
            AND m.round = 'F'
        ORDER BY m.date DESC
    """
    
    try:
        titles = Database.execute_query(query, (player_name,))
        
        if not titles:
            return {
                "player": player_name,
                "total_titles": 0,
                "by_tier": {},
                "by_surface": {},
                "titles": []
            }
        
        # Group by tier
        by_tier = {}
        by_surface = {}
        
        for title in titles:
            tier = title['tournament_tier'] or 'Other'
            surf = title['surface'] or 'Unknown'
            
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(title)
            
            if surf not in by_surface:
                by_surface[surf] = []
            by_surface[surf].append(title)
        
        # Count by tier
        tier_counts = {tier: len(titles_list) for tier, titles_list in by_tier.items()}
        surface_counts = {surf: len(titles_list) for surf, titles_list in by_surface.items()}
        
        return {
            "player": player_name,
            "total_titles": len(titles),
            "by_tier": tier_counts,
            "by_surface": surface_counts,
            "titles": titles
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
