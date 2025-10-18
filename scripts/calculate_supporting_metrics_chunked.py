#!/usr/bin/env python3
"""
Calculate supporting metrics in chunks with real-time progress updates.
"""

import sys
sys.path.insert(0, '/Users/razaool/tennis-career-tracker')
from database.db_manager import DatabaseManager
from datetime import datetime

print("=" * 80)
print("SUPPORTING METRICS - CHUNKED PROCESSING WITH PROGRESS")
print("=" * 80)

db = DatabaseManager()
start_time = datetime.now()

# Get all players
print("\n📊 Fetching players...")
with db.get_cursor() as cursor:
    cursor.execute("""
        SELECT DISTINCT player_id
        FROM player_ratings
        WHERE tsr_rating IS NOT NULL
        ORDER BY player_id
    """)
    
    all_player_ids = [row['player_id'] for row in cursor.fetchall()]
    total_players = len(all_player_ids)

print(f"✅ Found {total_players:,} players")
print(f"\nProcessing in chunks of 50 players...")
print(f"Progress updates every 50 players\n")
print("=" * 80)
print(f"{'Chunk':<8} {'Players':<20} {'Progress':<12} {'Rate':<15} {'ETA':<12} {'Time':<10}")
print("=" * 80)

# Process in chunks
chunk_size = 50
total_processed = 0
chunk_num = 0

for i in range(0, total_players, chunk_size):
    chunk_num += 1
    chunk_start = datetime.now()
    
    # Get this chunk of player IDs
    chunk_ids = all_player_ids[i:i+chunk_size]
    
    # Process each metric separately for this chunk
    # METRIC 1: Form Index
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH match_results AS (
                SELECT 
                    pr.rating_id,
                    pr.player_id,
                    CASE WHEN m.winner_id = pr.player_id THEN 1.0 ELSE 0.0 END as won,
                    ROW_NUMBER() OVER (PARTITION BY pr.player_id ORDER BY pr.date, pr.match_id) as match_num
                FROM player_ratings pr
                JOIN matches m ON pr.match_id = m.match_id
                WHERE pr.tsr_rating IS NOT NULL
                    AND pr.player_id = ANY(%s)
            )
            UPDATE player_ratings pr
            SET form_index = subq.form_index
            FROM (
                SELECT 
                    rating_id,
                    AVG(won) OVER (
                        PARTITION BY player_id 
                        ORDER BY match_num
                        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                    ) * 100 as form_index
                FROM match_results
            ) subq
            WHERE pr.rating_id = subq.rating_id
        """, (chunk_ids,))
    
    # METRIC 2: Big Match Rating
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH opponent_data AS (
                SELECT 
                    pr1.rating_id,
                    pr1.player_id,
                    pr1.elo_rating as player_elo,
                    pr2.elo_rating as opponent_elo,
                    CASE WHEN m.winner_id = pr1.player_id THEN 1.0 ELSE 0.0 END as won,
                    ROW_NUMBER() OVER (PARTITION BY pr1.player_id ORDER BY pr1.date, pr1.match_id) as match_num
                FROM player_ratings pr1
                JOIN matches m ON pr1.match_id = m.match_id
                JOIN player_ratings pr2 ON pr2.match_id = m.match_id AND pr2.player_id != pr1.player_id
                WHERE pr1.tsr_rating IS NOT NULL
                    AND pr1.player_id = ANY(%s)
                    AND pr2.elo_rating >= 2500
            )
            UPDATE player_ratings pr
            SET big_match_rating = subq.big_match_rating
            FROM (
                SELECT 
                    rating_id,
                    AVG((won - (1.0 / (1.0 + POWER(10, (opponent_elo - player_elo) / 400.0)))) * 100) OVER (
                        PARTITION BY player_id 
                        ORDER BY match_num
                        ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
                    ) as big_match_rating
                FROM opponent_data
            ) subq
            WHERE pr.rating_id = subq.rating_id
        """, (chunk_ids,))
    
    # METRIC 3: Tournament Success
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH tournament_points AS (
                SELECT 
                    pr.rating_id,
                    pr.player_id,
                    ROW_NUMBER() OVER (PARTITION BY pr.player_id ORDER BY pr.date, pr.match_id) as match_num,
                    CASE m.round
                        WHEN 'F' THEN 100 WHEN 'SF' THEN 75 WHEN 'QF' THEN 50
                        WHEN 'R16' THEN 30 WHEN 'R32' THEN 15 WHEN 'R64' THEN 5
                        WHEN 'R128' THEN 2 WHEN 'RR' THEN 40 ELSE 5
                    END * 
                    CASE m.tournament_tier
                        WHEN 'Grand Slam' THEN 2.0 WHEN 'Masters 1000' THEN 1.5
                        WHEN 'Masters' THEN 1.5 WHEN 'ATP Finals' THEN 1.8
                        WHEN 'ATP 500' THEN 1.2 WHEN 'Olympics' THEN 1.6
                        ELSE 1.0
                    END as points
                FROM player_ratings pr
                JOIN matches m ON pr.match_id = m.match_id
                WHERE pr.tsr_rating IS NOT NULL
                    AND pr.player_id = ANY(%s)
            )
            UPDATE player_ratings pr
            SET tournament_success_score = subq.tournament_success_score
            FROM (
                SELECT 
                    rating_id,
                    AVG(points) OVER (
                        PARTITION BY player_id 
                        ORDER BY match_num
                        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                    ) as tournament_success_score
                FROM tournament_points
            ) subq
            WHERE pr.rating_id = subq.rating_id
        """, (chunk_ids,))
    
    # Progress update
    total_processed += len(chunk_ids)
    progress_pct = (total_processed / total_players) * 100
    elapsed_total = (datetime.now() - start_time).total_seconds()
    chunk_time = (datetime.now() - chunk_start).total_seconds()
    rate = total_processed / elapsed_total if elapsed_total > 0 else 0
    remaining = (total_players - total_processed) / rate if rate > 0 else 0
    
    print(f"#{chunk_num:<7} {total_processed:>6,}/{total_players:<6,}   "
          f"{progress_pct:>6.2f}%      "
          f"{rate:>5.1f} pl/sec      "
          f"{remaining/60:>5.1f} min    "
          f"{chunk_time:>5.1f}s")

# Final summary
total_duration = (datetime.now() - start_time).total_seconds()

print("=" * 80)
print("✅ CALCULATION COMPLETE!")
print("=" * 80)
print(f"Players processed:  {total_processed:,}")
print(f"Total time:         {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
print(f"Average rate:       {total_processed/total_duration:.1f} players/second")
print("=" * 80)

# Show final examples
print("\n🎯 Top 10 Players with All Metrics:")
print("-" * 80)

with db.get_cursor() as cursor:
    cursor.execute("""
        WITH latest_ratings AS (
            SELECT DISTINCT ON (pr.player_id)
                pl.name,
                pr.tsr_rating,
                pr.tsr_uncertainty,
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
print("🎉 PHASE 2 - 100% COMPLETE!")
print("=" * 80)

