#!/usr/bin/env python3
"""
Improved Form Index Calculation

Current form is too simple (just win rate). This improves it by considering:
1. Opponent Quality - Beating top players counts more
2. Match Importance - Tournament tier matters
3. Recency Weighting - Recent matches count more
4. Momentum - Win/loss streaks add bonus/penalty

Formula:
Form = (Base Win Rate × Opponent Quality × Tournament Weight × Recency Weight) + Momentum Bonus

Scale: 0-100 (with rare cases extending to 110 for exceptional hot streaks)
"""

import sys
sys.path.insert(0, '/Users/razaool/tennis-career-tracker')
from database.db_manager import DatabaseManager
from datetime import datetime

print("=" * 80)
print("IMPROVED FORM INDEX CALCULATION")
print("=" * 80)
print()
print("New form considers:")
print("  1. Opponent Quality (ELO-adjusted)")
print("  2. Tournament Importance (tier weighting)")
print("  3. Recency (exponential decay)")
print("  4. Momentum (win/loss streak bonuses)")
print()
print("=" * 80)

db = DatabaseManager()
start_time = datetime.now()

print("\n📊 Calculating improved form index...")
print("-" * 80)

with db.get_cursor() as cursor:
    # Get player count
    cursor.execute("SELECT COUNT(DISTINCT player_id) FROM player_ratings WHERE tsr_rating IS NOT NULL")
    result = cursor.fetchone()
    total_players = result['count'] if result else 0
    print(f"Total players to process: {total_players:,}")
    print()

# Calculate improved form
with db.get_cursor() as cursor:
    cursor.execute("""
        WITH match_data AS (
            -- Get match results with opponent quality and tournament tier
            SELECT 
                pr.rating_id,
                pr.player_id,
                pr.date,
                pr.match_id,
                pr.elo_rating as player_elo,
                CASE WHEN m.winner_id = pr.player_id THEN 1.0 ELSE 0.0 END as won,
                -- Get opponent's ELO
                CASE 
                    WHEN m.player1_id = pr.player_id THEN pr2.elo_rating
                    ELSE pr1.elo_rating
                END as opponent_elo,
                m.tournament_tier,
                ROW_NUMBER() OVER (PARTITION BY pr.player_id ORDER BY pr.date, pr.match_id) as match_num,
                COUNT(*) OVER (PARTITION BY pr.player_id) as total_matches
            FROM player_ratings pr
            JOIN matches m ON pr.match_id = m.match_id
            LEFT JOIN player_ratings pr1 ON m.match_id = pr1.match_id AND m.player1_id = pr1.player_id
            LEFT JOIN player_ratings pr2 ON m.match_id = pr2.match_id AND m.player2_id = pr2.player_id
            WHERE pr.tsr_rating IS NOT NULL
        ),
        recent_matches AS (
            -- Get last 20 matches for each rating
            SELECT 
                md.*,
                -- Tournament tier weight
                CASE 
                    WHEN tournament_tier = 'Grand Slam' THEN 1.3
                    WHEN tournament_tier = 'Masters 1000' THEN 1.2
                    WHEN tournament_tier = 'ATP 500' THEN 1.1
                    WHEN tournament_tier = 'ATP Finals' THEN 1.4
                    ELSE 1.0
                END as tier_weight,
                -- Opponent quality factor (1.0 = equal, >1.0 = stronger opponent, <1.0 = weaker)
                CASE 
                    WHEN opponent_elo IS NULL THEN 1.0
                    WHEN opponent_elo >= player_elo + 200 THEN 1.3  -- Much stronger
                    WHEN opponent_elo >= player_elo + 100 THEN 1.15 -- Stronger
                    WHEN opponent_elo >= player_elo - 100 THEN 1.0  -- Similar
                    WHEN opponent_elo >= player_elo - 200 THEN 0.9  -- Weaker
                    ELSE 0.8  -- Much weaker
                END as opponent_quality,
                -- Recency weight (exponential decay)
                -- Most recent match = 1.0, 20 matches ago = ~0.5
                POWER(0.965, total_matches - match_num) as recency_weight
            FROM match_data md
        ),
        form_calculation AS (
            SELECT 
                rating_id,
                player_id,
                match_num,
                -- Calculate weighted form
                SUM(won * opponent_quality * tier_weight * recency_weight) OVER (
                    PARTITION BY player_id
                    ORDER BY match_num
                    ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                ) / NULLIF(
                    SUM(opponent_quality * tier_weight * recency_weight) OVER (
                        PARTITION BY player_id
                        ORDER BY match_num
                        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                    ), 0
                ) as weighted_win_rate,
                -- Get last 5 results for momentum
                ARRAY_AGG(won) OVER (
                    PARTITION BY player_id
                    ORDER BY match_num
                    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
                ) as last_5_results,
                -- Count matches in window
                COUNT(*) OVER (
                    PARTITION BY player_id
                    ORDER BY match_num
                    ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                ) as matches_in_window
            FROM recent_matches
        ),
        final_form AS (
            SELECT 
                rating_id,
                -- Base form (0-100)
                weighted_win_rate * 100 as base_form,
                -- Momentum bonus
                CASE 
                    -- 5-match win streak: +10
                    WHEN ARRAY_LENGTH(last_5_results, 1) = 5 AND 
                         (SELECT SUM(x) FROM UNNEST(last_5_results) x) = 5 THEN 10.0
                    -- 4-win streak: +5
                    WHEN ARRAY_LENGTH(last_5_results, 1) >= 4 AND
                         (SELECT SUM(x) FROM UNNEST(last_5_results) x(val) WHERE x >= ARRAY_LENGTH(last_5_results, 1) - 3) = 4 THEN 5.0
                    -- 5-loss streak: -10
                    WHEN ARRAY_LENGTH(last_5_results, 1) = 5 AND
                         (SELECT SUM(x) FROM UNNEST(last_5_results) x) = 0 THEN -10.0
                    ELSE 0.0
                END as momentum_bonus,
                matches_in_window
            FROM form_calculation
        )
        UPDATE player_ratings pr
        SET form_index = GREATEST(0, LEAST(110, 
            COALESCE(ff.base_form + ff.momentum_bonus, 50.0)
        ))
        FROM final_form ff
        WHERE pr.rating_id = ff.rating_id
    """)
    
    updated = cursor.rowcount
    print(f"✅ Updated {updated:,} player ratings with improved form index")

duration = datetime.now() - start_time
print()
print("=" * 80)
print(f"✅ IMPROVED FORM INDEX COMPLETE")
print(f"⏱️  Total time: {duration}")
print("=" * 80)
print()
print("📊 Improvements:")
print("  • Opponent quality: Wins vs strong opponents count more")
print("  • Tournament tier: Grand Slams weighted 1.3x, Masters 1.2x")
print("  • Recency: Recent matches weighted more (exponential decay)")
print("  • Momentum: 5-win streak adds +10, 5-loss streak subtracts 10")
print("  • Scale: 0-110 (exceptional hot streaks can exceed 100)")
print()

