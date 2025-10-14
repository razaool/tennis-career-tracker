"""
Calculate rolling/average ELO ratings to better represent player performance.

This addresses the "frozen ELO" problem where inactive players maintain
outdated high ratings while active players' ratings fluctuate.
"""
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_rolling_average_elo(db, window_size=50, active_within_months=6):
    """
    Calculate rolling average ELO for all players.
    
    Args:
        db: DatabaseManager instance
        window_size: Number of recent matches to average over
        active_within_months: Only include players active within this many months
    
    Returns:
        DataFrame with player rankings by rolling average ELO
    """
    cutoff_date = datetime.now() - timedelta(days=active_within_months * 30)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')
    
    with db.get_cursor() as cursor:
        # Get all players with their ratings
        cursor.execute("""
            WITH player_recent_matches AS (
                SELECT 
                    pr.player_id,
                    p.name,
                    pr.elo_rating,
                    pr.date,
                    pr.career_match_number,
                    ROW_NUMBER() OVER (
                        PARTITION BY pr.player_id 
                        ORDER BY pr.career_match_number DESC
                    ) as match_recency
                FROM player_ratings pr
                JOIN players p ON pr.player_id = p.player_id
                WHERE pr.elo_rating IS NOT NULL
            ),
            player_stats AS (
                SELECT 
                    player_id,
                    name,
                    AVG(elo_rating) FILTER (WHERE match_recency <= %s) as avg_elo_recent,
                    MAX(elo_rating) as peak_elo,
                    MAX(elo_rating) FILTER (WHERE match_recency = 1) as current_elo,
                    MAX(date) as last_match_date,
                    COUNT(*) FILTER (WHERE match_recency <= %s) as matches_in_window,
                    MAX(career_match_number) as total_matches
                FROM player_recent_matches
                GROUP BY player_id, name
            )
            SELECT 
                name,
                avg_elo_recent,
                current_elo,
                peak_elo,
                matches_in_window,
                total_matches,
                last_match_date
            FROM player_stats
            WHERE last_match_date >= %s  -- Only active players
              AND matches_in_window >= 10  -- Must have at least 10 matches in window
            ORDER BY avg_elo_recent DESC
            LIMIT 20
        """, (window_size, window_size, cutoff_str))
        
        results = cursor.fetchall()
    
    return results


def compare_ranking_methods(db):
    """Compare different ranking methods side-by-side"""
    
    logger.info("=" * 100)
    logger.info("COMPARING RANKING METHODS")
    logger.info("=" * 100)
    
    # Method 1: Current ELO (last match only)
    logger.info("\n📍 METHOD 1: CURRENT ELO (Last Match Only)")
    logger.info("-" * 100)
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH latest_ratings AS (
                SELECT 
                    player_id,
                    MAX(career_match_number) as max_match
                FROM player_ratings
                GROUP BY player_id
            )
            SELECT 
                p.name,
                pr.elo_rating as current_elo,
                pr.date as last_match_date,
                pr.career_match_number as total_matches
            FROM player_ratings pr
            JOIN latest_ratings lr ON pr.player_id = lr.player_id 
                AND pr.career_match_number = lr.max_match
            JOIN players p ON pr.player_id = p.player_id
            ORDER BY pr.elo_rating DESC
            LIMIT 10
        """)
        
        current_elo_rankings = cursor.fetchall()
    
    for i, player in enumerate(current_elo_rankings, 1):
        logger.info(f"  {i:2d}. {player['name']:25s} {player['current_elo']:7.1f}  "
                   f"(Last: {player['last_match_date']}, {player['total_matches']} matches)")
    
    # Method 2: Rolling Average ELO (last 50 matches)
    logger.info("\n📊 METHOD 2: ROLLING AVERAGE ELO (Last 50 Matches, Active Only)")
    logger.info("-" * 100)
    
    rolling_50 = calculate_rolling_average_elo(db, window_size=50, active_within_months=6)
    
    for i, player in enumerate(rolling_50[:10], 1):
        logger.info(f"  {i:2d}. {player['name']:25s} {player['avg_elo_recent']:7.1f}  "
                   f"(Current: {player['current_elo']:7.1f}, Peak: {player['peak_elo']:7.1f}, "
                   f"Last: {player['last_match_date']})")
    
    # Method 3: Peak ELO in 2024
    logger.info("\n🏆 METHOD 3: PEAK ELO IN 2024")
    logger.info("-" * 100)
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.name,
                MAX(pr.elo_rating) as peak_elo_2024,
                MAX(pr.date) as last_match_date
            FROM player_ratings pr
            JOIN players p ON pr.player_id = p.player_id
            WHERE pr.date >= '2024-01-01'
            GROUP BY p.player_id, p.name
            ORDER BY peak_elo_2024 DESC
            LIMIT 10
        """)
        
        peak_2024 = cursor.fetchall()
    
    for i, player in enumerate(peak_2024, 1):
        logger.info(f"  {i:2d}. {player['name']:25s} {player['peak_elo_2024']:7.1f}  "
                   f"(Last match: {player['last_match_date']})")
    
    # Analysis: Why rankings differ
    logger.info("\n" + "=" * 100)
    logger.info("🔍 ANALYSIS: WHY RANKINGS DIFFER")
    logger.info("=" * 100)
    
    # Find players who differ significantly between methods
    current_dict = {r['name']: (i+1, r['current_elo']) for i, r in enumerate(current_elo_rankings)}
    rolling_dict = {r['name']: (i+1, r['avg_elo_recent']) for i, r in enumerate(rolling_50[:10])}
    
    logger.info("\nPlayers ranked HIGHER in Rolling Avg vs Current ELO:")
    for name, (rolling_rank, rolling_elo) in rolling_dict.items():
        if name in current_dict:
            current_rank, current_elo = current_dict[name]
            if rolling_rank < current_rank:
                logger.info(f"  {name:25s}: #{rolling_rank} (avg {rolling_elo:.1f}) vs "
                           f"#{current_rank} (current {current_elo:.1f}) - "
                           f"Recent form better than last match")
    
    logger.info("\nPlayers ranked LOWER in Rolling Avg vs Current ELO:")
    for name, (rolling_rank, rolling_elo) in rolling_dict.items():
        if name in current_dict:
            current_rank, current_elo = current_dict[name]
            if rolling_rank > current_rank:
                logger.info(f"  {name:25s}: #{rolling_rank} (avg {rolling_elo:.1f}) vs "
                           f"#{current_rank} (current {current_elo:.1f}) - "
                           f"Last match better than average")
    
    logger.info("\nPlayers in Current ELO Top 10 but NOT in Rolling Avg Top 10 (likely inactive):")
    for name, (rank, elo) in current_dict.items():
        if name not in rolling_dict:
            logger.info(f"  {name:25s}: #{rank} in Current ELO ({elo:.1f}) - INACTIVE!")


def detailed_player_comparison(db, player_names):
    """Show detailed comparison for specific players"""
    
    logger.info("\n" + "=" * 100)
    logger.info("DETAILED PLAYER COMPARISON")
    logger.info("=" * 100)
    
    for player_name in player_names:
        with db.get_cursor() as cursor:
            cursor.execute("""
                WITH player_matches AS (
                    SELECT 
                        pr.elo_rating,
                        pr.date,
                        pr.career_match_number,
                        ROW_NUMBER() OVER (ORDER BY pr.career_match_number DESC) as recency
                    FROM player_ratings pr
                    JOIN players p ON pr.player_id = p.player_id
                    WHERE p.name = %s
                )
                SELECT 
                    MAX(elo_rating) FILTER (WHERE recency = 1) as current_elo,
                    AVG(elo_rating) FILTER (WHERE recency <= 20) as avg_last_20,
                    AVG(elo_rating) FILTER (WHERE recency <= 50) as avg_last_50,
                    AVG(elo_rating) FILTER (WHERE recency <= 100) as avg_last_100,
                    MAX(elo_rating) as peak_elo,
                    MIN(elo_rating) as lowest_elo,
                    MAX(date) as last_match,
                    COUNT(*) as total_matches
                FROM player_matches
            """, (player_name,))
            
            result = cursor.fetchone()
            
            if result:
                logger.info(f"\n{player_name.upper()}")
                logger.info("-" * 100)
                logger.info(f"  Current ELO (last match):     {result['current_elo']:7.1f}")
                logger.info(f"  Average last 20 matches:      {result['avg_last_20']:7.1f}")
                logger.info(f"  Average last 50 matches:      {result['avg_last_50']:7.1f}")
                logger.info(f"  Average last 100 matches:     {result['avg_last_100']:7.1f}")
                logger.info(f"  Peak ELO (career):            {result['peak_elo']:7.1f}")
                logger.info(f"  Lowest ELO (career):          {result['lowest_elo']:7.1f}")
                logger.info(f"  Last match:                   {result['last_match']}")
                logger.info(f"  Total matches:                {result['total_matches']}")
                
                # Analysis
                volatility = result['current_elo'] - result['avg_last_50']
                if abs(volatility) > 50:
                    if volatility > 0:
                        logger.info(f"  ⚠️  Recent spike: Current ELO is {volatility:.1f} points ABOVE 50-match average")
                    else:
                        logger.info(f"  ⚠️  Recent dip: Current ELO is {abs(volatility):.1f} points BELOW 50-match average")


def export_rolling_elo_rankings(db):
    """Export rolling average rankings to CSV"""
    
    logger.info("\n" + "=" * 100)
    logger.info("EXPORTING ROLLING AVERAGE RANKINGS")
    logger.info("=" * 100)
    
    from config import PROCESSED_DATA_DIR
    
    # Export different window sizes
    for window in [20, 50, 100]:
        rankings = calculate_rolling_average_elo(db, window_size=window, active_within_months=6)
        
        output_file = PROCESSED_DATA_DIR / f'rolling_avg_elo_{window}matches.csv'
        
        df = pd.DataFrame(rankings)
        df.to_csv(output_file, index=False)
        
        logger.info(f"✅ Exported rolling {window}-match average to: {output_file}")


def main():
    """Main execution"""
    db = DatabaseManager()
    
    # Compare all ranking methods
    compare_ranking_methods(db)
    
    # Detailed comparison for specific players
    detailed_player_comparison(db, [
        'Carlos Alcaraz',
        'Nick Kyrgios',
        'Jannik Sinner',
        'Novak Djokovic'
    ])
    
    # Export rankings
    export_rolling_elo_rankings(db)
    
    logger.info("\n" + "=" * 100)
    logger.info("✅ ANALYSIS COMPLETE")
    logger.info("=" * 100)


if __name__ == "__main__":
    main()

