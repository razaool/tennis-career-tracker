#!/usr/bin/env python3
"""
Calculate supporting metrics for tennis ratings.

This script calculates contextual performance metrics:
1. Form Index - Rolling 20-match win rate (recent form)
2. Big Match Rating - Performance vs top-20 opponents
3. Tournament Success Score - Weighted title/finals performance

These metrics add context to raw TSR ratings.
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


def calculate_form_index(recent_results: deque, window_size: int = 20) -> float:
    """
    Calculate form index based on recent match results.
    
    Form Index = weighted win rate over last 20 matches
    - Win = 1.0
    - Loss = 0.0
    - More recent matches weighted slightly higher
    
    Args:
        recent_results: Deque of recent match results (1.0 = win, 0.0 = loss)
        window_size: Number of matches to consider
        
    Returns:
        Form index between 0 and 100
    """
    if not recent_results:
        return 50.0  # Neutral form
    
    results_list = list(recent_results)
    n = len(results_list)
    
    if n == 0:
        return 50.0
    
    # Apply recency weighting: more recent matches count slightly more
    weighted_sum = 0.0
    weight_sum = 0.0
    
    for i, result in enumerate(results_list):
        # Linear recency weight: most recent = 1.0, oldest = 0.5
        weight = 0.5 + (0.5 * i / (n - 1)) if n > 1 else 1.0
        weighted_sum += result * weight
        weight_sum += weight
    
    # Calculate weighted win rate and scale to 0-100
    if weight_sum > 0:
        win_rate = weighted_sum / weight_sum
        return win_rate * 100.0
    else:
        return 50.0


def calculate_big_match_rating(
    player_elo: float,
    opponent_elo: float,
    match_result: float,
    tournament_tier: str
) -> float:
    """
    Calculate big match rating component.
    
    Higher value = better performance against elite opponents
    
    Args:
        player_elo: Player's ELO rating
        opponent_elo: Opponent's ELO rating
        match_result: 1.0 for win, 0.0 for loss
        tournament_tier: Tournament tier for weighting
        
    Returns:
        Big match rating contribution
    """
    # Only count matches against elite opponents (ELO >= 2500)
    if opponent_elo < 2500:
        return None  # Not a "big match"
    
    # Expected score based on ELO difference
    expected = 1.0 / (1.0 + 10 ** ((opponent_elo - player_elo) / 400.0))
    
    # Performance vs expectation
    performance = match_result - expected
    
    # Weight by opponent strength
    opponent_factor = min(opponent_elo / 3000.0, 1.5)  # Cap at 1.5x
    
    # Weight by tournament importance
    tournament_weight = 1.0
    if tournament_tier and tournament_tier in TOURNAMENT_TIERS:
        tournament_weight = TOURNAMENT_TIERS[tournament_tier]['weight']
    
    # Big match rating contribution
    rating = performance * opponent_factor * tournament_weight * 100
    
    return rating


def calculate_tournament_success_score(
    tournament_results: list,
    date: datetime.date
) -> float:
    """
    Calculate tournament success score based on recent tournament finishes.
    
    Args:
        tournament_results: List of (tier, round, date) tuples
        date: Current date for recency weighting
        
    Returns:
        Tournament success score
    """
    if not tournament_results:
        return 0.0
    
    # Round values (higher = better finish)
    round_values = {
        'F': 100,  # Final
        'SF': 75,  # Semifinal
        'QF': 50,  # Quarterfinal
        'R16': 30,  # Round of 16
        'R32': 15,  # Round of 32
        'R64': 5,   # Round of 64
        'R128': 2,  # Round of 128
        'RR': 40,   # Round Robin
    }
    
    score = 0.0
    for tier, round_name, result_date in tournament_results:
        # Get round value
        round_value = round_values.get(round_name, 0)
        
        # Weight by tournament tier
        tier_weight = 1.0
        if tier and tier in TOURNAMENT_TIERS:
            tier_weight = TOURNAMENT_TIERS[tier]['weight']
        
        # Recency weight (decay over time)
        days_ago = (date - result_date).days
        recency_weight = 1.0 / (1.0 + days_ago / 365.0)  # Decay over 1 year
        
        score += round_value * tier_weight * recency_weight
    
    # Normalize to reasonable scale
    return min(score / 10.0, 100.0)


def calculate_supporting_metrics():
    """
    Calculate supporting metrics for all players.
    Populates form_index, big_match_rating, and tournament_success_score columns.
    """
    logger.info("="*70)
    logger.info("CALCULATING SUPPORTING METRICS")
    logger.info("="*70)
    logger.info("Metrics: Form Index, Big Match Rating, Tournament Success")
    
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
        
        player_ids = [row['player_id'] for row in cursor.fetchall()]
        total_players = len(player_ids)
    
    logger.info(f"Processing {total_players:,} players...")
    
    processed_players = 0
    total_updates = 0
    
    for player_id in player_ids:
        # Get all matches for this player
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    pr.rating_id,
                    pr.date,
                    pr.elo_rating as player_elo,
                    m.winner_id,
                    m.tournament_tier,
                    m.round,
                    m.player1_id,
                    m.player2_id,
                    -- Get opponent's ELO at that time
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
        
        # Track metrics for each match
        recent_results = deque(maxlen=20)  # Rolling window of 20 matches
        big_match_ratings = deque(maxlen=50)  # Track recent big match performance
        tournament_results = deque(maxlen=20)  # Track recent tournament finishes
        
        updates = []
        
        for match in matches:
            # Determine if player won
            is_winner = (match['winner_id'] == player_id)
            match_result = 1.0 if is_winner else 0.0
            
            # Update recent results
            recent_results.append(match_result)
            
            # Calculate form index
            form_index = calculate_form_index(recent_results)
            
            # Calculate big match rating
            opponent_elo = match['opponent_elo'] or 1500.0
            big_match_contribution = calculate_big_match_rating(
                match['player_elo'],
                opponent_elo,
                match_result,
                match['tournament_tier']
            )
            
            if big_match_contribution is not None:
                big_match_ratings.append(big_match_contribution)
            
            # Average big match rating over recent matches
            big_match_rating = (
                sum(big_match_ratings) / len(big_match_ratings)
                if big_match_ratings else 0.0
            )
            
            # Track tournament results (finals/semis/etc)
            if match['round'] in ['F', 'SF', 'QF', 'R16']:
                tournament_results.append((
                    match['tournament_tier'],
                    match['round'],
                    match['date']
                ))
            
            # Calculate tournament success score
            tournament_score = calculate_tournament_success_score(
                list(tournament_results),
                match['date']
            )
            
            # Prepare update
            updates.append({
                'rating_id': match['rating_id'],
                'form_index': form_index,
                'big_match_rating': big_match_rating,
                'tournament_success_score': tournament_score
            })
        
        # Batch update database
        if updates:
            _update_database_batch(db, updates)
            total_updates += len(updates)
        
        processed_players += 1
        
        # Progress logging
        if processed_players % 1000 == 0:
            progress = processed_players / total_players * 100
            logger.info(f"Processed {processed_players:,} / {total_players:,} players ({progress:.1f}%)")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("="*70)
    logger.info(f"✅ Supporting metrics calculation complete!")
    logger.info(f"✅ Processed {processed_players:,} players")
    logger.info(f"✅ Updated {total_updates:,} rating records")
    logger.info(f"Calculation took {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info("="*70)
    
    # Show sample metrics
    _show_metric_examples(db)


def _update_database_batch(db: DatabaseManager, updates: list):
    """Update supporting metrics in database."""
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


def _show_metric_examples(db: DatabaseManager):
    """Display metric examples for Big 3."""
    logger.info("\n" + "="*70)
    logger.info("METRIC EXAMPLES (Big 3 - Current Status):")
    logger.info("="*70)
    
    with db.get_cursor() as cursor:
        for player in ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer']:
            cursor.execute("""
                SELECT DISTINCT ON (pr.player_id)
                    pl.name,
                    pr.tsr_rating,
                    pr.form_index,
                    pr.big_match_rating,
                    pr.tournament_success_score,
                    pr.date
                FROM player_ratings pr
                JOIN players pl ON pr.player_id = pl.player_id
                WHERE pl.name = %s
                  AND pr.form_index IS NOT NULL
                ORDER BY pr.player_id, pr.date DESC
            """, (player,))
            
            result = cursor.fetchone()
            
            if result:
                logger.info(
                    f"{result['name']:<20} TSR: {result['tsr_rating']:>7.1f}  |  "
                    f"Form: {result['form_index']:>5.1f}  |  "
                    f"Big Match: {result['big_match_rating']:>+6.1f}  |  "
                    f"Tournament: {result['tournament_success_score']:>5.1f}"
                )


if __name__ == '__main__':
    calculate_supporting_metrics()
    
    logger.info("\n" + "="*70)
    logger.info("✅ SCRIPT 4 COMPLETE - Supporting metrics calculated!")
    logger.info("="*70)
    logger.info("\nPhase 2 is now complete! All rating metrics calculated.")
    logger.info("\nNext steps:")
    logger.info("  1. Re-export visualization data with all new metrics")
    logger.info("  2. Proceed to Phase 3: API Development")

