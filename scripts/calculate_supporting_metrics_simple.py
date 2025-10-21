#!/usr/bin/env python3
"""
Calculate supporting metrics - SIMPLIFIED VERSION.

This calculates three key metrics:
1. Form Index - Recent win rate (last 20 matches)
2. Big Match Rating - Performance vs elite opponents
3. Tournament Success Score - Recent tournament achievements

Optimized for speed and efficiency.
"""

import logging
from datetime import datetime
from collections import deque
import sys
sys.path.insert(0, '/Users/razaool/tennis-career-tracker')
from database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def calculate_supporting_metrics_simple():
    """
    Calculate supporting metrics using a simplified, faster approach.
    """
    logger.info("="*70)
    logger.info("CALCULATING SUPPORTING METRICS (Simplified)")
    logger.info("="*70)
    
    db = DatabaseManager()
    start_time = datetime.now()
    
    # Strategy: Calculate metrics directly in SQL for speed
    logger.info("Calculating Form Index (20-match rolling win rate)...")
    
    # Form Index: Use SQL window function for efficiency
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH match_results AS (
                SELECT 
                    pr.rating_id,
                    pr.player_id,
                    pr.date,
                    CASE 
                        WHEN m.winner_id = pr.player_id THEN 1.0
                        ELSE 0.0
                    END as won,
                    ROW_NUMBER() OVER (PARTITION BY pr.player_id ORDER BY pr.date) as match_num
                FROM player_ratings pr
                JOIN matches m ON pr.match_id = m.match_id
                WHERE pr.tsr_rating IS NOT NULL
            ),
            rolling_form AS (
                SELECT 
                    rating_id,
                    player_id,
                    date,
                    AVG(won) OVER (
                        PARTITION BY player_id 
                        ORDER BY date 
                        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                    ) * 100 as form_index
                FROM match_results
            )
            UPDATE player_ratings pr
            SET form_index = rf.form_index
            FROM rolling_form rf
            WHERE pr.rating_id = rf.rating_id
        """)
        
        updated = cursor.rowcount
        logger.info(f"✅ Form Index calculated for {updated:,} records")
    
    # Big Match Rating: Simplified approach
    logger.info("\nCalculating Big Match Rating (vs elite opponents)...")
    
    with db.get_cursor() as cursor:
        # Get elite opponent matches and calculate performance
        cursor.execute("""
            WITH opponent_ratings AS (
                SELECT 
                    pr1.rating_id,
                    pr1.player_id,
                    pr1.elo_rating as player_elo,
                    pr2.elo_rating as opponent_elo,
                    CASE WHEN m.winner_id = pr1.player_id THEN 1.0 ELSE 0.0 END as won,
                    m.tournament_tier
                FROM player_ratings pr1
                JOIN matches m ON pr1.match_id = m.match_id
                JOIN player_ratings pr2 ON pr2.match_id = m.match_id 
                    AND pr2.player_id != pr1.player_id
                WHERE pr1.tsr_rating IS NOT NULL
                    AND pr2.elo_rating >= 2300  -- Elite opponents only
            ),
            big_match_performance AS (
                SELECT 
                    rating_id,
                    player_id,
                    -- Expected score based on ELO
                    1.0 / (1.0 + POWER(10, (opponent_elo - player_elo) / 400.0)) as expected,
                    won as actual
                FROM opponent_ratings
            ),
            rolling_big_match AS (
                SELECT 
                    rating_id,
                    player_id,
                    AVG((actual - expected) * 100) OVER (
                        PARTITION BY player_id 
                        ORDER BY rating_id
                        ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
                    ) as big_match_rating
                FROM big_match_performance
            )
            UPDATE player_ratings pr
            SET big_match_rating = rbm.big_match_rating
            FROM rolling_big_match rbm
            WHERE pr.rating_id = rbm.rating_id
        """)
        
        updated = cursor.rowcount
        logger.info(f"✅ Big Match Rating calculated for {updated:,} records")
    
    # Tournament Success: Simplified scoring
    logger.info("\nCalculating Tournament Success Score...")
    
    with db.get_cursor() as cursor:
        # Score based on tournament tier and round reached
        cursor.execute("""
            WITH tournament_scores AS (
                SELECT 
                    pr.rating_id,
                    pr.player_id,
                    pr.date,
                    CASE m.round
                        WHEN 'F' THEN 100
                        WHEN 'SF' THEN 75
                        WHEN 'QF' THEN 50
                        WHEN 'R16' THEN 30
                        WHEN 'R32' THEN 15
                        ELSE 5
                    END * 
                    CASE m.tournament_tier
                        WHEN 'Grand Slam' THEN 2.0
                        WHEN 'Masters 1000' THEN 1.5
                        WHEN 'ATP 500' THEN 1.2
                        ELSE 1.0
                    END as round_score
                FROM player_ratings pr
                JOIN matches m ON pr.match_id = m.match_id
                WHERE pr.tsr_rating IS NOT NULL
            ),
            rolling_tournament AS (
                SELECT 
                    rating_id,
                    player_id,
                    AVG(round_score) OVER (
                        PARTITION BY player_id 
                        ORDER BY date
                        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                    ) as tournament_success_score
                FROM tournament_scores
            )
            UPDATE player_ratings pr
            SET tournament_success_score = rt.tournament_success_score
            FROM rolling_tournament rt
            WHERE pr.rating_id = rt.rating_id
        """)
        
        updated = cursor.rowcount
        logger.info(f"✅ Tournament Success Score calculated for {updated:,} records")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("="*70)
    logger.info(f"✅ Supporting metrics calculation complete!")
    logger.info(f"Calculation took {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info("="*70)
    
    # Show sample results
    _show_metric_examples(db)


def _show_metric_examples(db: DatabaseManager):
    """Display metric examples for current top players."""
    logger.info("\n" + "="*70)
    logger.info("METRIC EXAMPLES (Current Active Players):")
    logger.info("="*70)
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH latest_ratings AS (
                SELECT DISTINCT ON (pr.player_id)
                    pl.name,
                    pr.tsr_rating,
                    pr.form_index,
                    pr.big_match_rating,
                    pr.tournament_success_score,
                    pr.date
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
        
        if results:
            logger.info(f"\n{'Player':<25} {'TSR':<8} {'Form':<8} {'Big Match':<12} {'Tournament':<12}")
            logger.info("-" * 70)
            
            for row in results:
                form = row['form_index'] if row['form_index'] else 0.0
                big_match = row['big_match_rating'] if row['big_match_rating'] else 0.0
                tourn = row['tournament_success_score'] if row['tournament_success_score'] else 0.0
                
                logger.info(
                    f"{row['name']:<25} {row['tsr_rating']:<8.1f} {form:<8.1f} "
                    f"{big_match:<12.1f} {tourn:<12.1f}"
                )
        else:
            logger.warning("No results found - metrics may still be calculating")


if __name__ == '__main__':
    try:
        calculate_supporting_metrics_simple()
        
        logger.info("\n" + "="*70)
        logger.info("✅ SCRIPT COMPLETE - Supporting metrics calculated!")
        logger.info("="*70)
        logger.info("\nMetrics added:")
        logger.info("  • form_index - Recent 20-match win rate (0-100)")
        logger.info("  • big_match_rating - Performance vs elite opponents")
        logger.info("  • tournament_success_score - Tournament achievement score")
        logger.info("\nPhase 2 is now 100% complete!")
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        import traceback
        traceback.print_exc()

