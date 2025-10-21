#!/usr/bin/env python3
"""
Calculate supporting metrics - FAST VERSION with immediate progress.
"""

import logging
from datetime import datetime
from collections import deque
import sys
sys.path.insert(0, '/Users/razaool/tennis-career-tracker')
from database.db_manager import DatabaseManager
from config import TOURNAMENT_TIERS

print("=" * 80)
print("SUPPORTING METRICS - FAST CALCULATION")
print("=" * 80)
print("\nStarting calculation...")
print("This will process 25,815 players")
print("=" * 80)

db = DatabaseManager()
start_time = datetime.now()

# Get all unique players
print("\n📊 Fetching player list...")
with db.get_cursor() as cursor:
    cursor.execute("""
        SELECT DISTINCT player_id
        FROM player_ratings
        WHERE tsr_rating IS NOT NULL
        ORDER BY player_id
    """)
    
    all_player_ids = [row['player_id'] for row in cursor.fetchall()]
    total_players = len(all_player_ids)

print(f"✅ Found {total_players:,} players\n")
print("Starting processing...")
print(f"{'Progress':<12} {'Players':<20} {'Rate':<20} {'Updates':<15} {'ETA':<15}")
print("-" * 80)

total_updates = 0
processed_players = 0

for player_id in all_player_ids:
    # Get matches for this player
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                pr.rating_id,
                pr.elo_rating,
                m.winner_id = pr.player_id as won,
                m.tournament_tier,
                m.round,
                COALESCE((SELECT pr2.elo_rating 
                          FROM player_ratings pr2 
                          WHERE pr2.match_id = m.match_id 
                            AND pr2.player_id != pr.player_id 
                          LIMIT 1), 1500.0) as opponent_elo
            FROM player_ratings pr
            JOIN matches m ON pr.match_id = m.match_id
            WHERE pr.player_id = %s
              AND pr.tsr_rating IS NOT NULL
            ORDER BY pr.date
        """, (player_id,))
        
        matches = cursor.fetchall()
    
    if not matches:
        processed_players += 1
        continue
    
    # Calculate metrics
    recent_results = deque(maxlen=20)
    big_match_results = deque(maxlen=50)
    tournament_scores = deque(maxlen=20)
    
    for match in matches:
        won = match['won']
        player_elo = match['elo_rating']
        opponent_elo = match['opponent_elo']
        
        # 1. Form Index
        recent_results.append(1.0 if won else 0.0)
        form_index = (sum(recent_results) / len(recent_results)) * 100.0
        
        # 2. Big Match Rating
        if opponent_elo >= 2300:
            expected = 1.0 / (1.0 + 10 ** ((opponent_elo - player_elo) / 400.0))
            actual = 1.0 if won else 0.0
            big_match_results.append((actual - expected) * 100)
        
        big_match_rating = sum(big_match_results) / len(big_match_results) if big_match_results else 0.0
        
        # 3. Tournament Success
        round_values = {'F': 100, 'SF': 75, 'QF': 50, 'R16': 30, 'R32': 15, 'R64': 5, 'R128': 2, 'RR': 40}
        round_score = round_values.get(match['round'], 5)
        tier_weight = TOURNAMENT_TIERS.get(match['tournament_tier'], {}).get('weight', 1.0)
        tournament_scores.append(round_score * tier_weight)
        
        tournament_success = sum(tournament_scores) / len(tournament_scores) if tournament_scores else 0.0
        
        # Update immediately (one at a time to avoid locks)
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE player_ratings
                SET 
                    form_index = %s,
                    big_match_rating = %s,
                    tournament_success_score = %s
                WHERE rating_id = %s
            """, (form_index, big_match_rating, tournament_success, match['rating_id']))
        
        total_updates += 1
    
    processed_players += 1
    
    # Progress every 50 players
    if processed_players % 50 == 0 or processed_players == total_players:
        progress_pct = (processed_players / total_players) * 100
        elapsed = (datetime.now() - start_time).total_seconds()
        rate = processed_players / elapsed if elapsed > 0 else 0
        remaining_sec = (total_players - processed_players) / rate if rate > 0 else 0
        
        print(f"{progress_pct:>6.2f}%      "
              f"{processed_players:>6,}/{total_players:<6,}    "
              f"{rate:>5.1f} players/sec    "
              f"{total_updates:>10,}        "
              f"{remaining_sec/60:>5.1f} min")

# Final summary
end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print("=" * 80)
print("✅ CALCULATION COMPLETE!")
print("=" * 80)
print(f"Players processed:  {processed_players:,}")
print(f"Records updated:    {total_updates:,}")
print(f"Total time:         {duration:.1f} seconds ({duration/60:.1f} minutes)")
print(f"Average rate:       {processed_players/duration:.1f} players/sec")
print(f"Average per player: {duration/processed_players:.2f} sec")
print("=" * 80)

# Show sample results
print("\n📊 Sample Results (Top 15 Active Players):")
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
        LIMIT 15
    """)
    
    results = cursor.fetchall()
    
    print(f"{'Player':<25} {'TSR':<8} {'Form%':<8} {'BigMatch':<10} {'TournSucc':<10}")
    print("-" * 80)
    
    for row in results:
        print(f"{row['name']:<25} {row['tsr_rating']:<8.1f} "
              f"{row['form_index']:<8.1f} {row['big_match_rating']:<10.1f} "
              f"{row['tournament_success_score']:<10.1f}")

print("\n" + "=" * 80)
print("🎉 PHASE 2 - 100% COMPLETE!")
print("=" * 80)

