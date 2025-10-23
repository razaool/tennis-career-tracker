"""
Match prediction endpoints - MVP version
"""
from fastapi import APIRouter, HTTPException, Query
from database import Database
import math

router = APIRouter()


def calculate_win_probability(elo_diff: float) -> float:
    """Calculate win probability from ELO difference using standard formula"""
    return 1 / (1 + math.pow(10, -elo_diff / 400))


@router.get("/match", response_model=dict)
async def predict_match(
    player1: str = Query(..., description="First player name"),
    player2: str = Query(..., description="Second player name"),
    surface: str = Query(default="hard", regex="^(clay|grass|hard)$")
):
    """
    Predict match outcome between two players
    
    **MVP Version** - Uses ELO and form only
    
    - **player1**: First player name
    - **player2**: Second player name  
    - **surface**: Surface type (clay, grass, hard)
    
    Returns win probabilities and breakdown of factors
    """
    
    # Get both players' data with surface-specific win rates
    query = """
        WITH surface_performance AS (
            SELECT 
                pr.player_id,
                COUNT(*) as surface_matches,
                SUM(CASE WHEN m.winner_id = pr.player_id THEN 1 ELSE 0 END) as surface_wins,
                AVG(pr.elo_rating) as avg_surface_elo
            FROM player_ratings pr
            JOIN matches m ON pr.match_id = m.match_id
            WHERE m.surface = %s
              AND pr.date >= CURRENT_DATE - INTERVAL '2 years'
            GROUP BY pr.player_id
            HAVING COUNT(*) >= 5  -- At least 5 matches on surface
        )
        SELECT 
            p.name,
            p.player_id,
            plr.elo_rating,
            CASE 
                WHEN sp.surface_matches >= 5 THEN
                    -- Adjust ELO based on surface win rate
                    plr.elo_rating + ((sp.surface_wins::float / sp.surface_matches - 0.5) * 100)
                ELSE
                    plr.elo_rating
            END as surface_elo,
            sp.surface_matches,
            sp.surface_wins,
            plr.form_index,
            plr.big_match_rating,
            plr.tsr_uncertainty
        FROM players p
        INNER JOIN player_latest_ratings plr ON p.player_id = plr.player_id
        LEFT JOIN surface_performance sp ON p.player_id = sp.player_id
        WHERE p.name IN (%s, %s)
    """
    
    try:
        players = Database.execute_query(query, (surface, player1, player2))
        
        if len(players) < 2:
            raise HTTPException(
                status_code=404,
                detail=f"One or both players not found. Found: {[p['name'] for p in players]}"
            )
        
        # Organize player data
        p1_data = next(p for p in players if p['name'].lower() == player1.lower())
        p2_data = next(p for p in players if p['name'].lower() == player2.lower())
        
        # Calculate ELO differences
        elo_diff = p1_data['elo_rating'] - p2_data['elo_rating']
        surface_elo_diff = (p1_data['surface_elo'] or p1_data['elo_rating']) - \
                          (p2_data['surface_elo'] or p2_data['elo_rating'])
        
        # Base probability from overall ELO
        base_prob = calculate_win_probability(elo_diff)
        
        # Adjust for surface specialization
        if surface_elo_diff != elo_diff:
            surface_prob = calculate_win_probability(surface_elo_diff)
            # Weight surface ELO more heavily
            adjusted_prob = 0.4 * base_prob + 0.6 * surface_prob
        else:
            adjusted_prob = base_prob
        
        # Adjust for form
        form1 = p1_data['form_index'] or 50.0
        form2 = p2_data['form_index'] or 50.0
        form_diff = form1 - form2
        
        if abs(form_diff) > 10:
            # Form matters: adjust by up to 5% based on form difference
            form_adjustment = (form_diff / 200)  # ±0.05 max
            unclamped_prob = adjusted_prob + form_adjustment
            final_prob = max(0.05, min(0.95, unclamped_prob))  # Clamp between 5-95%
        else:
            final_prob = adjusted_prob
        
        # Determine confidence based on rating uncertainty
        avg_uncertainty = ((p1_data['tsr_uncertainty'] or 150) + (p2_data['tsr_uncertainty'] or 150)) / 2
        if avg_uncertainty < 120:
            confidence = "high"
        elif avg_uncertainty < 160:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Determine expected closeness
        prob_diff = abs(final_prob - 0.5)
        if prob_diff < 0.1:
            closeness = "toss-up"
        elif prob_diff < 0.2:
            closeness = "close_match"
        elif prob_diff < 0.3:
            closeness = "slight_favorite"
        else:
            closeness = "clear_favorite"
        
        return {
            "player1": {
                "name": p1_data['name'],
                "current_elo": round(p1_data['elo_rating'], 1),
                "surface_elo": round(p1_data['surface_elo'] or p1_data['elo_rating'], 1),
                "surface_record": f"{p1_data['surface_wins'] or 0}-{(p1_data['surface_matches'] or 0) - (p1_data['surface_wins'] or 0)}" if p1_data.get('surface_matches') else "Limited data",
                "form": round(form1, 1),
                "big_match_rating": round(p1_data['big_match_rating'], 2) if p1_data['big_match_rating'] else None
            },
            "player2": {
                "name": p2_data['name'],
                "current_elo": round(p2_data['elo_rating'], 1),
                "surface_elo": round(p2_data['surface_elo'] or p2_data['elo_rating'], 1),
                "surface_record": f"{p2_data['surface_wins'] or 0}-{(p2_data['surface_matches'] or 0) - (p2_data['surface_wins'] or 0)}" if p2_data.get('surface_matches') else "Limited data",
                "form": round(form2, 1),
                "big_match_rating": round(p2_data['big_match_rating'], 2) if p2_data['big_match_rating'] else None
            },
            "surface": surface,
            "prediction": {
                "player1_win_probability": round(final_prob * 100, 1),
                "player2_win_probability": round((1 - final_prob) * 100, 1),
                "confidence": confidence,
                "expected_closeness": closeness
            },
            "factors": {
                "elo_advantage": f"{p1_data['name'] if elo_diff > 0 else p2_data['name']} +{abs(round(elo_diff, 0))}",
                "surface_advantage": f"{p1_data['name'] if surface_elo_diff > 0 else p2_data['name']} +{abs(round(surface_elo_diff, 0))} on {surface}",
                "form_advantage": f"{p1_data['name'] if form_diff > 0 else p2_data['name']} +{abs(round(form_diff, 1))}%" if abs(form_diff) > 5 else "Even form",
            },
            "breakdown": {
                "base_probability": round(base_prob * 100, 1),
                "surface_adjusted": round(adjusted_prob * 100, 1),
                "form_adjusted": round(final_prob * 100, 1),
                "clamped": abs(form_diff) > 10 and (unclamped_prob > 0.95 or unclamped_prob < 0.05)
            },
            "note": "MVP prediction using ELO, surface performance, and recent form. Probabilities are clamped to 5-95% range to account for uncertainty."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

