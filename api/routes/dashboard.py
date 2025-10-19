"""
Dashboard endpoints - quick summary data for homepage
"""
from fastapi import APIRouter, HTTPException
from datetime import date
from ..database import Database

router = APIRouter()


@router.get("/top10", response_model=dict)
async def get_top10():
    """
    Get current top 10 players (for homepage widget)
    
    Returns quick summary with flag emojis for visual appeal
    """
    
    query = """
        SELECT 
            ROW_NUMBER() OVER (ORDER BY plr.elo_rating DESC) as rank,
            p.name,
            p.country,
            plr.elo_rating,
            plr.form_index,
            plr.last_match
        FROM players p
        INNER JOIN player_latest_ratings plr ON p.player_id = plr.player_id
        WHERE plr.last_match >= CURRENT_DATE - INTERVAL '6 months'
          AND plr.elo_rating IS NOT NULL
        ORDER BY plr.elo_rating DESC
        LIMIT 10
    """
    
    try:
        top10 = Database.execute_query(query)
        
        # Get as_of date
        date_query = "SELECT MAX(last_match) as last_date FROM player_latest_ratings"
        date_result = Database.execute_one(date_query)
        as_of = date_result['last_date'] if date_result else date.today()
        
        return {
            "as_of": str(as_of),
            "top10": top10
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/trending", response_model=dict)
async def get_trending():
    """
    Get trending players (biggest recent changes)
    
    Currently returns placeholder - will calculate ELO changes later
    """
    
    # Placeholder for now
    return {
        "period": "30 days",
        "trending_up": [],
        "trending_down": []
    }


@router.get("/stat-of-day", response_model=dict)
async def get_stat_of_day():
    """
    Random interesting statistic for engagement
    
    Returns a rotating interesting fact about tennis history
    """
    
    # Simple rotation based on day of year
    import random
    random.seed(date.today().timetuple().tm_yday)
    
    stats = [
        {
            "stat": "Jannik Sinner has the highest current ELO rating at 3,379",
            "category": "current",
            "players": ["Jannik Sinner"]
        },
        {
            "stat": "Carlos Alcaraz is 100% in form - winning his last 20 matches!",
            "category": "form",
            "players": ["Carlos Alcaraz"]
        },
        {
            "stat": "The Big 3 era produced the 3 highest peak ELO ratings in history",
            "category": "history",
            "players": ["Novak Djokovic", "Rafael Nadal", "Roger Federer"]
        }
    ]
    
    return random.choice(stats)

