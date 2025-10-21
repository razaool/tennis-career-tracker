#!/usr/bin/env python3
"""
Calculate supporting metrics with detailed progress reporting.
"""

import logging
from datetime import datetime
from collections import deque
import sys
sys.path.insert(0, '/Users/razaool/tennis-career-tracker')
from database.db_manager import DatabaseManager
from config import TOURNAMENT_TIERS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def calculate_supporting_metrics_with_progress():
    """Calculate supporting metrics with detailed progress."""
    print("=" * 80)
    print("CALCULATING SUPPORTING METRICS")
    print("=" * 80)
    
    db = DatabaseManager()
    start_time = datetime.now()
    
    # Get all unique players
    print("\n📊 Step 1: Fetching players from database...")
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT player_id
            FROM player_ratings
            WHERE tsr_rating IS NOT NULL
            ORDER BY player_id
        """)
        
        all_player_ids = [row['player_id'] for row in cursor.fetchall()]
        total_players = len(all_player_ids)
    
    print(f"✅ Found {total_players:,} players to process\n")
    
    # Process players one by one with progress
    print("📊 Step 2: Calculating metrics for each player...")
    print("=" * 80)
    
    total_updates = 0
    processed_players = 0
    
    for player_id in all_player_ids:
        # Get all matches for this player
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pr.rating_id,
                    pr.elo_rating as player_elo,
                    m.winner_id = pr.player_id as won,
                    m.tournament_tier,
                    m.round,
                    (SELECT pr2.elo_rating 
                     FROM player_ratings pr2 
                     WHERE pr2.match_id = m.match_id 
                       AND pr2.player_id != pr.player_id 
                     LIMIT 1) as opponent_elo
                FROM player_ratings pr
                JOIN matches m ON pr.match_id = m.match_id
                WHERE pr.player_id = %s
                  AND pr.tsr_rating IS NOT NULL
                ORDER BY pr.date, m.match_id
            """, (player_id,))
            
            matches = cursor.fetchall()
        
        if not matches:
            processed_players += 1
            continue
        
        # Calculate metrics
        recent_results = deque(maxlen=20)
        big_match_results = deque(maxlen=50)
        tournament_scores = deque(maxlen=20)
        
        updates = []
        
        for match in matches:
            won = match['won']
            opponent_elo = match['opponent_elo'] or 1500.0
            
            # Form Index
            recent_results.append(1.0 if won else 0.0)
            form_index = (sum(recent_results) / len(recent_results)) * 100.0 if recent_results else 50.0
            
            # Big Match Rating
            if opponent_elo >= 2300:
                expected = 1.0 / (1.0 + 10 ** ((opponent_elo - match['player_elo']) / 400.0))
                actual = 1.0 if won else 0.0
                big_match_results.append((actual - expected) * 100)
            
            big_match_rating = sum(big_match_results) / len(big_match_results) if big_match_results else 0.0
            
            # Tournament Success
            round_values = {'F': 100, 'SF': 75, 'QF': 50, 'R16': 30, 'R32': 15, 'R64': 5, 'R128': 2, 'RR': 40}
            round_score = round_values.get(match['round'], 5)
            tier_weight = TOURNAMENT_TIERS.get(match['tournament_tier'], {}).get('weight', 1.0)
            tournament_scores.append(round_score * tier_weight)
            
            tournament_success = sum(tournament_scores) / len(tournament_scores) if tournament_scores else 0.0
            
            updates.append({
                'rating_id': match['rating_id'],
                'form_index': form_index,
                'big_match_rating': big_match_rating,
                'tournament_success_score': tournament_success
            })
        
        # Update database for this player
        if updates:
            with db.get_cursor() as cursor:
                for update in updates:
                    cursor.execute("""
                        UPDATE player_ratings
                        SET 
                            form_index = %s,
                            big_match_rating = %s,
                            tournament_success_score = %s
                        WHERE rating_id = %s
                    """, (
                        update['form_index'],
                        update['big_match_rating'],
                        update['tournament_success_score'],
                        update['rating_id']
                    ))
            
            total_updates += len(updates)
        
        processed_players += 1
        
        # Progress reporting every 100 players
        if processed_players % 100 == 0:
            progress_pct = (processed_players / total_players) * 100
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = processed_players / elapsed if elapsed > 0 else 0
            remaining = (total_players - processed_players) / rate if rate > 0 else 0
            
            print(f"[{processed_players:>6,}/{total_players:>6,}] "
                  f"{progress_pct:>6.2f}% | "
                  f"Rate: {rate:>6.1f} players/sec | "
                  f"Updates: {total_updates:>8,} | "
                  f"ETA: {remaining/60:>5.1f} min")
    
    # Final update
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("=" * 80)
    print(f"✅ COMPLETE!")
    print(f"   Processed: {processed_players:,} players")
    print(f"   Updated: {total_updates:,} records")
    print(f"   Time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"   Rate: {processed_players/duration:.1f} players/sec")
    print("=" * 80)
    
    # Show examples
    print("\n📊 Sample Results (Top 10 Current Players):")
    print("-" * 80)
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH latest_ratings AS (
                SELECT DISTINCT ON (pr.player_id)
                    pl.name,
                    pr.tsr_rating,
                    pr.form_index,
                    pr.big_match_rating,
                    pr.tournament_success_score
                FROM player_ratings pr
                JOIN players pl ON pr.player_id = pl.player_id
                WHERE pr.form_index IS NOT NULL
                  AND pr.date >= CURRENT_DATE - INTERVAL '6 months'
                ORDER BY pr.player_id, pr.date DESC
            )
            SELECT *
            FROM latest_ratings
            ORDER BY tsr_rating DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        print(f"{'Player':<25} {'TSR':<8} {'Form%':<8} {'BigMatch':<10} {'TournSucc':<10}")
        print("-" * 80)
        
        for row in results:
            print(f"{row['name']:<25} {row['tsr_rating']:<8.1f} "
                  f"{row['form_index']:<8.1f} {row['big_match_rating']:<10.1f} "
                  f"{row['tournament_success_score']:<10.1f}")
    
    print("\n" + "=" * 80)
    print("🎉 SUPPORTING METRICS COMPLETE - PHASE 2 NOW 100% DONE!")
    print("=" * 80)


if __name__ == '__main__':
    try:
        calculate_supporting_metrics_with_progress()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

