#!/usr/bin/env python3
"""
Calculate supporting metrics using batch processing to avoid deadlocks.

Metrics:
1. Form Index - Recent 20-match win rate
2. Big Match Rating - Performance vs elite opponents  
3. Tournament Success Score - Tournament achievement metric

Strategy: Process players in batches to avoid database locks.
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
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def calculate_form_index(recent_results: list) -> float:
    """Calculate form index from recent match results."""
    if not recent_results:
        return 50.0
    
    # Simple win rate * 100
    wins = sum(recent_results)
    return (wins / len(recent_results)) * 100.0


def calculate_big_match_rating(player_elo: float, opponent_elo: float, won: bool) -> float:
    """Calculate big match performance."""
    if opponent_elo < 2500:
        return None  # Not a big match
    
    # Expected score
    expected = 1.0 / (1.0 + 10 ** ((opponent_elo - player_elo) / 400.0))
    actual = 1.0 if won else 0.0
    
    # Performance above/below expectation
    return (actual - expected) * 100


def get_tournament_score(tier: str, round_name: str) -> float:
    """Get score for tournament round."""
    round_values = {
        'F': 100, 'SF': 75, 'QF': 50, 'R16': 30,
        'R32': 15, 'R64': 5, 'R128': 2, 'RR': 40
    }
    
    round_score = round_values.get(round_name, 5)
    
    tier_weight = 1.0
    if tier and tier in TOURNAMENT_TIERS:
        tier_weight = TOURNAMENT_TIERS[tier]['weight']
    
    return round_score * tier_weight


def process_player_batch(db: DatabaseManager, player_ids: list) -> int:
    """Process a batch of players and calculate their metrics."""
    total_updates = 0
    
    for player_id in player_ids:
        # Get all matches for this player
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pr.rating_id,
                    pr.elo_rating as player_elo,
                    m.winner_id = pr.player_id as won,
                    m.tournament_tier,
                    m.round,
                    -- Get opponent ELO
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
            continue
        
        # Calculate metrics for each match
        recent_results = deque(maxlen=20)
        big_match_results = deque(maxlen=50)
        tournament_scores = deque(maxlen=20)
        
        updates = []
        
        for match in matches:
            won = match['won']
            opponent_elo = match['opponent_elo'] or 1500.0
            
            # 1. Form Index
            recent_results.append(1.0 if won else 0.0)
            form_index = calculate_form_index(list(recent_results))
            
            # 2. Big Match Rating
            big_match_score = calculate_big_match_rating(
                match['player_elo'],
                opponent_elo,
                won
            )
            
            if big_match_score is not None:
                big_match_results.append(big_match_score)
            
            big_match_rating = (
                sum(big_match_results) / len(big_match_results)
                if big_match_results else 0.0
            )
            
            # 3. Tournament Success
            tourn_score = get_tournament_score(
                match['tournament_tier'],
                match['round']
            )
            tournament_scores.append(tourn_score)
            
            tournament_success = (
                sum(tournament_scores) / len(tournament_scores)
                if tournament_scores else 0.0
            )
            
            updates.append({
                'rating_id': match['rating_id'],
                'form_index': form_index,
                'big_match_rating': big_match_rating,
                'tournament_success_score': tournament_success
            })
        
        # Batch update for this player
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
    
    return total_updates


def calculate_supporting_metrics_batch():
    """Calculate supporting metrics by processing players in batches."""
    logger.info("="*70)
    logger.info("CALCULATING SUPPORTING METRICS (Batch Processing)")
    logger.info("="*70)
    
    db = DatabaseManager()
    start_time = datetime.now()
    
    # Get all unique players
    logger.info("Fetching all players...")
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT player_id
            FROM player_ratings
            WHERE tsr_rating IS NOT NULL
            ORDER BY player_id
        """)
        
        all_player_ids = [row['player_id'] for row in cursor.fetchall()]
        total_players = len(all_player_ids)
    
    logger.info(f"Processing {total_players:,} players in batches...")
    
    # Process in batches
    batch_size = 100
    total_updates = 0
    processed_players = 0
    
    for i in range(0, total_players, batch_size):
        batch = all_player_ids[i:i+batch_size]
        
        # Process this batch
        updates = process_player_batch(db, batch)
        total_updates += updates
        processed_players += len(batch)
        
        # Progress logging
        if processed_players % 1000 == 0 or processed_players == total_players:
            progress = processed_players / total_players * 100
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = processed_players / elapsed if elapsed > 0 else 0
            remaining = (total_players - processed_players) / rate if rate > 0 else 0
            
            logger.info(
                f"Progress: {processed_players:,}/{total_players:,} players ({progress:.1f}%) | "
                f"Rate: {rate:.1f} players/sec | "
                f"Est. remaining: {remaining/60:.1f} min"
            )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("="*70)
    logger.info(f"✅ Supporting metrics calculation complete!")
    logger.info(f"✅ Processed {processed_players:,} players")
    logger.info(f"✅ Updated {total_updates:,} rating records")
    logger.info(f"Calculation took {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info("="*70)
    
    # Show sample results
    _show_metric_examples(db)


def _show_metric_examples(db: DatabaseManager):
    """Display metric examples for top players."""
    logger.info("\n" + "="*70)
    logger.info("METRIC EXAMPLES (Current Top Players):")
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
            LIMIT 20
        """)
        
        results = cursor.fetchall()
        
        if results:
            logger.info(f"\n{'Player':<25} {'TSR':<8} {'Form%':<8} {'BigMatch':<10} {'TournSucc':<10}")
            logger.info("-" * 70)
            
            for row in results:
                form = row['form_index'] if row['form_index'] else 0.0
                big_match = row['big_match_rating'] if row['big_match_rating'] else 0.0
                tourn = row['tournament_success_score'] if row['tournament_success_score'] else 0.0
                
                logger.info(
                    f"{row['name']:<25} {row['tsr_rating']:<8.1f} {form:<8.1f} "
                    f"{big_match:<10.1f} {tourn:<10.1f}"
                )
        else:
            logger.warning("No results found")


if __name__ == '__main__':
    try:
        calculate_supporting_metrics_batch()
        
        logger.info("\n" + "="*70)
        logger.info("✅ SUPPORTING METRICS COMPLETE!")
        logger.info("="*70)
        logger.info("\nMetrics calculated:")
        logger.info("  • form_index - Recent 20-match win rate (0-100%)")
        logger.info("  • big_match_rating - Performance vs elite opponents (±100)")
        logger.info("  • tournament_success_score - Tournament achievement score")
        logger.info("\n🎉 Phase 2 is now 100% complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

