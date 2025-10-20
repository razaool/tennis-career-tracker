"""
Head-to-head endpoints for player rivalries
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database import Database

router = APIRouter()


@router.get("/{player1}/{player2}", response_model=dict)
async def get_head_to_head(
    player1: str,
    player2: str,
    surface: Optional[str] = Query(default=None, regex="^(clay|grass|hard)$")
):
    """
    Get complete head-to-head record between two players
    
    - **player1**: First player name (URL-encoded)
    - **player2**: Second player name (URL-encoded)
    - **surface**: Optional surface filter (clay, grass, hard)
    
    Returns:
    - Total matches, wins for each player
    - Surface breakdown
    - All matches with dates, tournaments, scores
    """
    
    # Decode names
    player1 = player1.replace("%20", " ").replace("+", " ")
    player2 = player2.replace("%20", " ").replace("+", " ")
    
    # Get player IDs
    player_query = """
        SELECT player_id, name FROM players 
        WHERE name IN (%s, %s)
    """
    
    try:
        players = Database.execute_query(player_query, (player1, player2))
        
        if len(players) != 2:
            raise HTTPException(
                status_code=404, 
                detail=f"One or both players not found: '{player1}', '{player2}'"
            )
        
        p1_id = next(p['player_id'] for p in players if p['name'] == player1)
        p2_id = next(p['player_id'] for p in players if p['name'] == player2)
        
        # Build query for all H2H matches
        matches_query = """
            SELECT 
                m.date,
                m.tournament_name,
                m.tournament_tier,
                m.surface,
                m.round,
                m.score,
                CASE 
                    WHEN m.winner_id = %s THEN %s
                    ELSE %s
                END as winner
            FROM matches m
            WHERE ((m.player1_id = %s AND m.player2_id = %s)
                OR (m.player1_id = %s AND m.player2_id = %s))
        """
        
        params = [p1_id, player1, player2, p1_id, p2_id, p2_id, p1_id]
        
        if surface:
            matches_query += " AND m.surface = %s"
            params.append(surface)
        
        matches_query += " ORDER BY m.date DESC"
        
        matches = Database.execute_query(matches_query, tuple(params))
        
        if not matches:
            return {
                "player1": player1,
                "player2": player2,
                "total_matches": 0,
                "player1_wins": 0,
                "player2_wins": 0,
                "message": "These players have never faced each other"
            }
        
        # Calculate stats
        p1_wins = sum(1 for m in matches if m['winner'] == player1)
        p2_wins = sum(1 for m in matches if m['winner'] == player2)
        
        # Surface breakdown
        surface_breakdown = {}
        for match in matches:
            surf = match['surface'] or 'unknown'
            if surf not in surface_breakdown:
                surface_breakdown[surf] = {'total': 0, 'player1_wins': 0, 'player2_wins': 0}
            surface_breakdown[surf]['total'] += 1
            if match['winner'] == player1:
                surface_breakdown[surf]['player1_wins'] += 1
            else:
                surface_breakdown[surf]['player2_wins'] += 1
        
        # Tournament tier breakdown
        tier_breakdown = {}
        for match in matches:
            tier = match['tournament_tier'] or 'Other'
            if tier not in tier_breakdown:
                tier_breakdown[tier] = {'total': 0, 'player1_wins': 0, 'player2_wins': 0}
            tier_breakdown[tier]['total'] += 1
            if match['winner'] == player1:
                tier_breakdown[tier]['player1_wins'] += 1
            else:
                tier_breakdown[tier]['player2_wins'] += 1
        
        # Most recent match
        latest_match = matches[0] if matches else None
        
        return {
            "player1": player1,
            "player2": player2,
            "total_matches": len(matches),
            "player1_wins": p1_wins,
            "player2_wins": p2_wins,
            "win_percentage": {
                "player1": round((p1_wins / len(matches)) * 100, 1),
                "player2": round((p2_wins / len(matches)) * 100, 1)
            },
            "surface_breakdown": surface_breakdown,
            "tier_breakdown": tier_breakdown,
            "latest_match": {
                "date": latest_match['date'],
                "tournament": latest_match['tournament_name'],
                "round": latest_match['round'],
                "winner": latest_match['winner'],
                "score": latest_match['score']
            } if latest_match else None,
            "matches": matches
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/{player1}/{player2}/timeline", response_model=dict)
async def get_head_to_head_timeline(
    player1: str,
    player2: str
):
    """
    Get head-to-head timeline showing rating evolution during rivalry
    
    - **player1**: First player name (URL-encoded)
    - **player2**: Second player name (URL-encoded)
    
    Returns timeline of H2H with ratings at each match
    """
    
    # Decode names
    player1 = player1.replace("%20", " ").replace("+", " ")
    player2 = player2.replace("%20", " ").replace("+", " ")
    
    try:
        # Get H2H matches with ratings
        query = """
            WITH h2h_matches AS (
                SELECT m.match_id, m.date, m.tournament_name, m.round, m.score,
                       m.winner_id, m.player1_id, m.player2_id
                FROM matches m
                WHERE ((m.player1_id = (SELECT player_id FROM players WHERE name = %s)
                        AND m.player2_id = (SELECT player_id FROM players WHERE name = %s))
                    OR (m.player1_id = (SELECT player_id FROM players WHERE name = %s)
                        AND m.player2_id = (SELECT player_id FROM players WHERE name = %s)))
            )
            SELECT 
                h.date,
                h.tournament_name,
                h.round,
                h.score,
                CASE WHEN h.winner_id = (SELECT player_id FROM players WHERE name = %s)
                     THEN %s ELSE %s END as winner,
                pr1.elo_rating as player1_elo,
                pr2.elo_rating as player2_elo
            FROM h2h_matches h
            LEFT JOIN player_ratings pr1 ON pr1.match_id = h.match_id 
                AND pr1.player_id = (SELECT player_id FROM players WHERE name = %s)
            LEFT JOIN player_ratings pr2 ON pr2.match_id = h.match_id 
                AND pr2.player_id = (SELECT player_id FROM players WHERE name = %s)
            ORDER BY h.date ASC
        """
        
        timeline = Database.execute_query(
            query, 
            (player1, player2, player2, player1, player1, player1, player2, player1, player2)
        )
        
        if not timeline:
            raise HTTPException(
                status_code=404,
                detail=f"No matches found between '{player1}' and '{player2}'"
            )
        
        # Calculate running H2H
        p1_wins = 0
        p2_wins = 0
        
        for match in timeline:
            if match['winner'] == player1:
                p1_wins += 1
            else:
                p2_wins += 1
            
            match['running_h2h'] = {
                'player1_wins': p1_wins,
                'player2_wins': p2_wins
            }
        
        return {
            "player1": player1,
            "player2": player2,
            "total_matches": len(timeline),
            "timeline": timeline
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

