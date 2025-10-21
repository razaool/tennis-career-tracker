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
    Dynamic interesting statistic for engagement
    
    Returns a rotating interesting fact pulled from actual data
    """
    
    import random
    random.seed(date.today().timetuple().tm_yday)
    
    try:
        # Query 1: Highest current ELO
        query1 = """
            SELECT p.name, plr.elo_rating
            FROM players p
            JOIN player_latest_ratings plr ON p.player_id = plr.player_id
            WHERE plr.elo_rating IS NOT NULL
            ORDER BY plr.elo_rating DESC
            LIMIT 1
        """
        top_elo = Database.execute_one(query1)
        
        # Query 2: Highest peak ELO of all time
        query2 = """
            SELECT p.name, MAX(pr.elo_rating) as peak_elo
            FROM players p
            JOIN player_ratings pr ON p.player_id = pr.player_id
            WHERE pr.elo_rating IS NOT NULL
            GROUP BY p.name
            ORDER BY peak_elo DESC
            LIMIT 1
        """
        peak_elo = Database.execute_one(query2)
        
        # Query 3: Best current form (active players)
        query3 = """
            SELECT p.name, plr.form_index
            FROM players p
            JOIN player_latest_ratings plr ON p.player_id = plr.player_id
            WHERE plr.form_index IS NOT NULL
              AND plr.last_match >= CURRENT_DATE - INTERVAL '3 months'
            ORDER BY plr.form_index DESC
            LIMIT 1
        """
        best_form = Database.execute_one(query3)
        
        # Query 4: Most Grand Slam matches played
        query4 = """
            SELECT p.name, COUNT(DISTINCT pr.match_id) as gs_count
            FROM players p
            JOIN player_ratings pr ON p.player_id = pr.player_id
            JOIN matches m ON pr.match_id = m.match_id
            WHERE m.tournament_tier = 'Grand Slam'
            GROUP BY p.name
            ORDER BY gs_count DESC
            LIMIT 1
        """
        most_gs = Database.execute_one(query4)
        
        # Query 5: Highest big match rating
        query5 = """
            SELECT p.name, plr.big_match_rating
            FROM players p
            JOIN player_latest_ratings plr ON p.player_id = plr.player_id
            WHERE plr.big_match_rating IS NOT NULL
              AND plr.big_match_rating > 0
            ORDER BY plr.big_match_rating DESC
            LIMIT 1
        """
        big_match = Database.execute_one(query5)
        
        # Query 6: Total matches tracked
        query6 = "SELECT COUNT(*) as total FROM matches"
        total_matches = Database.execute_one(query6)
        
        # Query 7: Most career wins
        query7 = """
            SELECT p.name, COUNT(*) as wins
            FROM players p
            JOIN matches m ON p.player_id = m.winner_id
            GROUP BY p.name
            ORDER BY wins DESC
            LIMIT 1
        """
        most_wins = Database.execute_one(query7)
        
        # Build stat list with actual data
        stats = []
        
        if top_elo:
            stats.append({
                "stat": f"{top_elo['name']} leads the current ELO rankings at {top_elo['elo_rating']:.0f}",
                "category": "current",
                "players": [top_elo['name']],
                "value": round(top_elo['elo_rating'], 2)
            })
        
        if peak_elo:
            stats.append({
                "stat": f"{peak_elo['name']} holds the all-time peak ELO record at {peak_elo['peak_elo']:.0f}",
                "category": "history",
                "players": [peak_elo['name']],
                "value": round(peak_elo['peak_elo'], 2)
            })
        
        if best_form and best_form['form_index'] > 0.8:
            form_pct = best_form['form_index'] * 100
            stats.append({
                "stat": f"{best_form['name']} is in red-hot form with a {form_pct:.0f}% win rate over their last 20 matches",
                "category": "form",
                "players": [best_form['name']],
                "value": round(form_pct, 1)
            })
        
        if most_gs:
            stats.append({
                "stat": f"{most_gs['name']} has played {most_gs['gs_count']} Grand Slam matches - the most in our database",
                "category": "milestone",
                "players": [most_gs['name']],
                "value": most_gs['gs_count']
            })
        
        if big_match and big_match['big_match_rating'] > 0:
            stats.append({
                "stat": f"{big_match['name']} has the highest Big Match Rating at {big_match['big_match_rating']:.0f}",
                "category": "clutch",
                "players": [big_match['name']],
                "value": round(big_match['big_match_rating'], 2)
            })
        
        if total_matches:
            stats.append({
                "stat": f"Our database tracks {total_matches['total']:,} professional tennis matches spanning from 1968 to 2025",
                "category": "database",
                "players": [],
                "value": total_matches['total']
            })
        
        if most_wins:
            stats.append({
                "stat": f"{most_wins['name']} has the most career wins in our database with {most_wins['wins']:,} victories",
                "category": "wins",
                "players": [most_wins['name']],
                "value": most_wins['wins']
            })
        
        # Fallback if no stats available
        if not stats:
            stats.append({
                "stat": "Tennis Career Tracker: Analyzing over 50 years of professional tennis data",
                "category": "general",
                "players": [],
                "value": None
            })
        
        return random.choice(stats)
        
    except Exception as e:
        # Fallback on error
        return {
            "stat": "Tennis has been professionally tracked since 1968, with thousands of players competing worldwide",
            "category": "general",
            "players": [],
            "value": None,
            "error": str(e)
        }

