"""
Generate comprehensive player rankings using three complementary metrics:
1. Current ELO - Form/momentum (last match)
2. Rolling Average ELO - Consistency (last 50 matches)
3. Peak ELO - Highest achievement (in time period)

Each metric tells a different story about player performance.
"""
import sys
from pathlib import Path
import csv
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from config import PROCESSED_DATA_DIR
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_current_elo_rankings(db, min_date=None, limit=50):
    """
    Current ELO Rankings - Shows current form/momentum.
    
    Pros: Reflects immediate form, useful for predictions
    Cons: Volatile, can be skewed by last match
    """
    with db.get_cursor() as cursor:
        query = """
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
                pr.elo_clay,
                pr.elo_grass,
                pr.elo_hard,
                pr.date as last_match_date,
                pr.career_match_number as total_matches
            FROM player_ratings pr
            JOIN latest_ratings lr ON pr.player_id = lr.player_id 
                AND pr.career_match_number = lr.max_match
            JOIN players p ON pr.player_id = p.player_id
            WHERE pr.elo_rating IS NOT NULL
        """
        
        if min_date:
            query += f" AND pr.date >= '{min_date}'"
        
        query += " ORDER BY pr.elo_rating DESC LIMIT %s"
        
        cursor.execute(query, (limit,))
        return cursor.fetchall()


def get_rolling_average_rankings(db, window_size=50, min_date=None, limit=50):
    """
    Rolling Average ELO Rankings - Shows consistency.
    
    Pros: Smooths volatility, rewards sustained performance
    Cons: Slower to react to form changes
    """
    with db.get_cursor() as cursor:
        date_filter = f"AND date >= '{min_date}'" if min_date else ""
        
        query = f"""
            WITH player_recent_matches AS (
                SELECT 
                    pr.player_id,
                    p.name,
                    pr.elo_rating,
                    pr.elo_clay,
                    pr.elo_grass,
                    pr.elo_hard,
                    pr.date,
                    pr.career_match_number,
                    ROW_NUMBER() OVER (
                        PARTITION BY pr.player_id 
                        ORDER BY pr.career_match_number DESC
                    ) as match_recency
                FROM player_ratings pr
                JOIN players p ON pr.player_id = p.player_id
                WHERE pr.elo_rating IS NOT NULL
            )
            SELECT 
                name,
                ROUND(AVG(elo_rating) FILTER (WHERE match_recency <= {window_size})::numeric, 2) as rolling_avg_elo,
                ROUND(AVG(elo_clay) FILTER (WHERE match_recency <= {window_size})::numeric, 2) as avg_elo_clay,
                ROUND(AVG(elo_grass) FILTER (WHERE match_recency <= {window_size})::numeric, 2) as avg_elo_grass,
                ROUND(AVG(elo_hard) FILTER (WHERE match_recency <= {window_size})::numeric, 2) as avg_elo_hard,
                MAX(elo_rating) FILTER (WHERE match_recency = 1) as current_elo,
                MAX(date) as last_match_date,
                COUNT(*) FILTER (WHERE match_recency <= {window_size}) as matches_in_window,
                MAX(career_match_number) as total_matches
            FROM player_recent_matches
            WHERE 1=1 {date_filter}
            GROUP BY player_id, name
            HAVING COUNT(*) FILTER (WHERE match_recency <= {window_size}) >= {min(10, window_size//5)}
            ORDER BY rolling_avg_elo DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        return cursor.fetchall()


def get_peak_elo_rankings(db, start_date=None, end_date=None, limit=50):
    """
    Peak ELO Rankings - Shows highest achievement in period.
    
    Pros: Rewards excellence, captures Grand Slam performances
    Cons: May not reflect current form
    """
    with db.get_cursor() as cursor:
        date_filter = ""
        if start_date and end_date:
            date_filter = f"AND pr.date BETWEEN '{start_date}' AND '{end_date}'"
        elif start_date:
            date_filter = f"AND pr.date >= '{start_date}'"
        
        query = f"""
            WITH peak_ratings AS (
                SELECT 
                    pr.player_id,
                    p.name,
                    MAX(pr.elo_rating) as peak_elo,
                    MAX(pr.elo_clay) as peak_elo_clay,
                    MAX(pr.elo_grass) as peak_elo_grass,
                    MAX(pr.elo_hard) as peak_elo_hard,
                    MAX(pr.date) as last_match_date,
                    MAX(pr.career_match_number) as total_matches
                FROM player_ratings pr
                JOIN players p ON pr.player_id = p.player_id
                WHERE pr.elo_rating IS NOT NULL {date_filter}
                GROUP BY pr.player_id, p.name
            ),
            peak_dates AS (
                SELECT 
                    pr.player_id,
                    pr.date as peak_date,
                    pr.career_match_number as peak_match_number
                FROM player_ratings pr
                WHERE pr.elo_rating IS NOT NULL {date_filter}
            )
            SELECT 
                pk.name,
                pk.peak_elo,
                pk.peak_elo_clay,
                pk.peak_elo_grass,
                pk.peak_elo_hard,
                MIN(pd.peak_date) as peak_date,
                MIN(pd.peak_match_number) as peak_match_number,
                pk.last_match_date,
                pk.total_matches
            FROM peak_ratings pk
            LEFT JOIN peak_dates pd ON pk.player_id = pd.player_id
            GROUP BY 
                pk.player_id, pk.name, pk.peak_elo, pk.peak_elo_clay, 
                pk.peak_elo_grass, pk.peak_elo_hard, pk.last_match_date, pk.total_matches
            ORDER BY pk.peak_elo DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        return cursor.fetchall()


def generate_combined_rankings(db, year=2024, active_months=6, window_size=50, top_n=20):
    """
    Generate comprehensive rankings showing all three metrics.
    """
    logger.info("=" * 120)
    logger.info(f"COMPREHENSIVE TENNIS RANKINGS - {year}")
    logger.info("=" * 120)
    
    # Date filters
    year_start = f"{year}-01-01"
    cutoff_date = (datetime.now() - timedelta(days=active_months * 30)).strftime('%Y-%m-%d')
    
    # Get all three rankings
    logger.info(f"\n📊 Fetching rankings (active since {cutoff_date})...")
    
    current_rankings = get_current_elo_rankings(db, min_date=cutoff_date, limit=top_n)
    rolling_rankings = get_rolling_average_rankings(db, window_size=window_size, min_date=cutoff_date, limit=top_n)
    peak_rankings = get_peak_elo_rankings(db, start_date=year_start, limit=top_n)
    
    # Create lookup dictionaries
    current_dict = {r['name']: r for r in current_rankings}
    rolling_dict = {r['name']: r for r in rolling_rankings}
    peak_dict = {r['name']: r for r in peak_rankings}
    
    # Get all unique players
    all_players = set(current_dict.keys()) | set(rolling_dict.keys()) | set(peak_dict.keys())
    
    # Combine data
    combined = []
    for player in all_players:
        current = current_dict.get(player, {})
        rolling = rolling_dict.get(player, {})
        peak = peak_dict.get(player, {})
        
        combined.append({
            'name': player,
            'current_elo': current.get('current_elo'),
            'rolling_avg_elo': rolling.get('rolling_avg_elo'),
            'peak_elo': peak.get('peak_elo'),
            'current_clay': current.get('elo_clay'),
            'current_grass': current.get('elo_grass'),
            'current_hard': current.get('elo_hard'),
            'avg_clay': rolling.get('avg_elo_clay'),
            'avg_grass': rolling.get('avg_elo_grass'),
            'avg_hard': rolling.get('avg_elo_hard'),
            'peak_clay': peak.get('peak_elo_clay'),
            'peak_grass': peak.get('peak_elo_grass'),
            'peak_hard': peak.get('peak_elo_hard'),
            'last_match_date': current.get('last_match_date') or rolling.get('last_match_date') or peak.get('last_match_date'),
            'total_matches': current.get('total_matches') or rolling.get('total_matches') or peak.get('total_matches'),
            'matches_in_window': rolling.get('matches_in_window'),
        })
    
    # Sort by rolling average (best overall metric)
    combined.sort(key=lambda x: x['rolling_avg_elo'] or 0, reverse=True)
    
    # Display rankings
    logger.info("\n" + "=" * 120)
    logger.info("TOP 20 RANKINGS - THREE METRICS COMPARISON")
    logger.info("=" * 120)
    logger.info(f"{'Rank':<5} {'Player':<25} {'Current':<10} {'Avg-{window_size}':<10} {'Peak {year}':<12} {'Last Match':<12} {'Matches':<8}")
    logger.info("-" * 120)
    
    for i, player in enumerate(combined[:top_n], 1):
        current_str = f"{player['current_elo']:.1f}" if player['current_elo'] else "N/A"
        rolling_str = f"{player['rolling_avg_elo']:.1f}" if player['rolling_avg_elo'] else "N/A"
        peak_str = f"{player['peak_elo']:.1f}" if player['peak_elo'] else "N/A"
        
        # Add indicators
        indicators = []
        if player['current_elo'] and player['rolling_avg_elo']:
            diff = float(player['current_elo']) - float(player['rolling_avg_elo'])
            if diff > 50:
                indicators.append("🔥")  # Hot streak
            elif diff < -50:
                indicators.append("❄️")  # Cold streak
        
        if player['peak_elo'] and player['rolling_avg_elo']:
            if float(player['peak_elo']) - float(player['rolling_avg_elo']) < 50:
                indicators.append("⭐")  # Near peak
        
        indicator_str = " ".join(indicators)
        
        logger.info(f"{i:<5} {player['name']:<25} {current_str:<10} {rolling_str:<10} {peak_str:<12} "
                   f"{player['last_match_date']:<12} {player['total_matches']:<8} {indicator_str}")
    
    # Export to CSV
    output_file = PROCESSED_DATA_DIR / f'comprehensive_rankings_{year}.csv'
    with open(output_file, 'w', newline='') as f:
        fieldnames = [
            'rank', 'name', 'current_elo', 'rolling_avg_elo', f'peak_elo_{year}',
            'current_clay', 'current_grass', 'current_hard',
            'avg_clay', 'avg_grass', 'avg_hard',
            'peak_clay', 'peak_grass', 'peak_hard',
            'last_match_date', 'total_matches', 'matches_in_window'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, player in enumerate(combined[:top_n], 1):
            row = {'rank': i, **player}
            row[f'peak_elo_{year}'] = row.pop('peak_elo')
            writer.writerow(row)
    
    logger.info(f"\n✅ Exported to: {output_file}")
    
    # Analysis
    logger.info("\n" + "=" * 120)
    logger.info("📈 INSIGHTS")
    logger.info("=" * 120)
    
    # Find players on hot/cold streaks
    hot_streaks = [p for p in combined if p['current_elo'] and p['rolling_avg_elo'] 
                   and float(p['current_elo']) - float(p['rolling_avg_elo']) > 50]
    cold_streaks = [p for p in combined if p['current_elo'] and p['rolling_avg_elo'] 
                    and float(p['rolling_avg_elo']) - float(p['current_elo']) > 50]
    near_peak = [p for p in combined if p['peak_elo'] and p['rolling_avg_elo'] 
                 and float(p['peak_elo']) - float(p['rolling_avg_elo']) < 50]
    
    if hot_streaks:
        logger.info("\n🔥 HOT STREAKS (Current ELO > 50 points above rolling avg):")
        for p in hot_streaks[:5]:
            diff = float(p['current_elo']) - float(p['rolling_avg_elo'])
            logger.info(f"   {p['name']:<25} Current: {p['current_elo']:.1f}  Avg: {p['rolling_avg_elo']:.1f}  (+{diff:.1f})")
    
    if cold_streaks:
        logger.info("\n❄️  COLD STREAKS (Current ELO > 50 points below rolling avg):")
        for p in cold_streaks[:5]:
            diff = float(p['rolling_avg_elo']) - float(p['current_elo'])
            logger.info(f"   {p['name']:<25} Current: {p['current_elo']:.1f}  Avg: {p['rolling_avg_elo']:.1f}  (-{diff:.1f})")
    
    if near_peak:
        logger.info(f"\n⭐ NEAR PEAK FORM (Within 50 points of {year} peak):")
        for p in near_peak[:5]:
            diff = float(p['peak_elo']) - float(p['rolling_avg_elo'])
            logger.info(f"   {p['name']:<25} Peak: {p['peak_elo']:.1f}  Current Avg: {p['rolling_avg_elo']:.1f}  (-{diff:.1f})")
    
    # Metric explanations
    logger.info("\n" + "=" * 120)
    logger.info("📋 METRIC EXPLANATIONS")
    logger.info("=" * 120)
    logger.info(f"""
1. CURRENT ELO (Form/Momentum):
   - Based on: Last match only
   - Shows: Immediate form and momentum
   - Use for: Match predictions, betting odds
   - Limitation: Volatile, can swing drastically

2. ROLLING AVG ELO (Consistency):
   - Based on: Average of last {window_size} matches
   - Shows: Sustained performance and consistency
   - Use for: Overall skill assessment, "who's better"
   - Limitation: Slower to react to form changes

3. PEAK ELO {year} (Achievement):
   - Based on: Highest rating in {year}
   - Shows: Best performance achieved this year
   - Use for: Year-end awards, career highlights
   - Limitation: May not reflect current ability

INDICATORS:
   🔥 = Hot streak (current > avg by 50+ points)
   ❄️  = Cold streak (current < avg by 50+ points)
   ⭐ = Near peak form (within 50 points of {year} peak)
    """)
    
    return combined


def compare_methods_for_players(db, player_names, window_size=50):
    """Compare all three methods for specific players"""
    
    logger.info("\n" + "=" * 120)
    logger.info("INDIVIDUAL PLAYER ANALYSIS")
    logger.info("=" * 120)
    
    for player_name in player_names:
        with db.get_cursor() as cursor:
            # Get comprehensive stats
            cursor.execute(f"""
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
                    ROUND(AVG(elo_rating) FILTER (WHERE recency <= 20)::numeric, 2) as avg_last_20,
                    ROUND(AVG(elo_rating) FILTER (WHERE recency <= {window_size})::numeric, 2) as avg_last_50,
                    MAX(elo_rating) as peak_elo_career,
                    MAX(elo_rating) FILTER (WHERE date >= '2024-01-01') as peak_elo_2024,
                    MIN(date) FILTER (WHERE date >= '2024-01-01') as first_2024_match,
                    MAX(date) as last_match,
                    COUNT(*) FILTER (WHERE date >= '2024-01-01') as matches_2024,
                    COUNT(*) as total_matches
                FROM player_matches
            """, (player_name,))
            
            result = cursor.fetchone()
            
            if result and result['current_elo']:
                logger.info(f"\n{player_name.upper()}")
                logger.info("-" * 120)
                logger.info(f"  {'Metric':<30} {'Value':<15} {'Context'}")
                logger.info(f"  {'-' * 30} {'-' * 15} {'-' * 50}")
                logger.info(f"  {'Current ELO (last match)':<30} {result['current_elo']:>7.1f}       Last match: {result['last_match']}")
                logger.info(f"  {'Rolling Avg (20 matches)':<30} {result['avg_last_20']:>7.1f}       Recent form")
                logger.info(f"  {'Rolling Avg ({window_size} matches)':<30} {result['avg_last_50']:>7.1f}       Sustained performance")
                logger.info(f"  {'Peak ELO (2024)':<30} {result['peak_elo_2024']:>7.1f}       Best in 2024")
                logger.info(f"  {'Peak ELO (career)':<30} {result['peak_elo_career']:>7.1f}       All-time best")
                logger.info(f"  {'Matches in 2024':<30} {result['matches_2024']:>7}         {result['first_2024_match']} to {result['last_match']}")
                logger.info(f"  {'Total career matches':<30} {result['total_matches']:>7}")
                
                # Interpretation
                if result['current_elo'] > result['avg_last_50']:
                    logger.info(f"\n  💡 {player_name} is on an upward trend (current > avg)")
                elif result['current_elo'] < result['avg_last_50']:
                    logger.info(f"\n  💡 {player_name} is in a rough patch (current < avg)")
                
                if result['avg_last_50'] >= result['peak_elo_2024'] * 0.95:
                    logger.info(f"  💡 {player_name} is near their 2024 peak form")


def main():
    """Main execution"""
    db = DatabaseManager()
    
    # Generate comprehensive 2024 rankings
    generate_combined_rankings(db, year=2024, active_months=6, window_size=50, top_n=20)
    
    # Detailed player analysis
    compare_methods_for_players(db, [
        'Jannik Sinner',
        'Carlos Alcaraz', 
        'Novak Djokovic',
        'Alexander Zverev',
        'Taylor Fritz',
        'Nick Kyrgios'
    ])
    
    logger.info("\n" + "=" * 120)
    logger.info("✅ COMPREHENSIVE RANKINGS COMPLETE")
    logger.info("=" * 120)


if __name__ == "__main__":
    main()

