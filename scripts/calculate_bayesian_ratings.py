#!/usr/bin/env python3
"""
Calculate Bayesian hierarchical ratings (TSR - Tennis Skill Rating).

TSR = ELO + Uncertainty Estimates

Strategy:
1. Use existing ELO ratings as TSR (already accounts for opponent quality & tournaments)
2. Calculate uncertainty (Rating Deviation) based on:
   - Number of matches played (experience)
   - Recency of activity (rust factor)
   - ELO volatility (consistency)

This leverages our proven ELO system while adding Bayesian uncertainty estimates.
"""

import logging
from datetime import datetime, timedelta
import math
import numpy as np
import sys
sys.path.insert(0, '/Users/razaool/tennis-career-tracker')
from database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def calculate_uncertainty(
    match_count: int,
    days_since_last_match: int,
    elo_std_dev: float,
    recent_matches_count: int
) -> float:
    """
    Calculate Rating Deviation (uncertainty) for a player.
    
    Lower uncertainty = more confident in rating
    Higher uncertainty = less confident in rating
    
    Args:
        match_count: Total number of matches played
        days_since_last_match: Days since last match (inactivity)
        elo_std_dev: Standard deviation of ELO over recent matches
        recent_matches_count: Number of matches in recent window
        
    Returns:
        Uncertainty value (Rating Deviation)
    """
    # Base uncertainty starts high and decreases with experience
    # Using logarithmic decay: more matches = lower uncertainty
    if match_count == 0:
        experience_uncertainty = 350.0  # Maximum uncertainty
    else:
        # Uncertainty decreases logarithmically with matches
        # After 100 matches: ~100 uncertainty
        # After 1000 matches: ~50 uncertainty
        experience_uncertainty = 350.0 / (1 + math.log(match_count + 1) / 3)
    
    # Inactivity increases uncertainty
    # Rust builds up over time away from competition
    if days_since_last_match > 0:
        # Uncertainty grows with square root of time (Glicko formula)
        # ~1% increase per month of inactivity
        rating_periods = days_since_last_match / 30.0
        inactivity_factor = math.sqrt(1 + rating_periods * 0.01)
    else:
        inactivity_factor = 1.0
    
    # Performance consistency affects uncertainty
    # Volatile players have higher uncertainty
    if elo_std_dev > 0 and recent_matches_count >= 10:
        # Normalize std dev to uncertainty scale
        # High std dev (>200) = +50% uncertainty
        # Low std dev (<100) = normal uncertainty
        volatility_factor = 1.0 + (elo_std_dev / 400.0)
    else:
        volatility_factor = 1.0
    
    # Combine factors
    uncertainty = experience_uncertainty * inactivity_factor * volatility_factor
    
    # Cap uncertainty at reasonable bounds
    return min(max(uncertainty, 25.0), 350.0)


def calculate_bayesian_ratings():
    """
    Calculate TSR (Tennis Skill Rating) = ELO + Uncertainty Estimates.
    
    Populates:
    - tsr_rating: Copy of elo_rating (proven metric)
    - tsr_uncertainty: Bayesian confidence estimate
    - Surface-specific uncertainties
    """
    logger.info("="*70)
    logger.info("CALCULATING TSR (Tennis Skill Rating) WITH UNCERTAINTY")
    logger.info("="*70)
    logger.info("Strategy: TSR = ELO + Bayesian Uncertainty Estimates")
    
    db = DatabaseManager()
    start_time = datetime.now()
    
    # Get all player rating entries
    logger.info("Fetching all rating records...")
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                pr.rating_id,
                pr.player_id,
                pr.match_id,
                pr.date,
                pr.elo_rating,
                pr.elo_clay,
                pr.elo_grass,
                pr.elo_hard,
                pr.career_match_number
            FROM player_ratings pr
            ORDER BY pr.player_id, pr.date
        """)
        
        all_ratings = cursor.fetchall()
        total_records = len(all_ratings)
    
    logger.info(f"Processing {total_records:,} rating records...")
    
    # Track player statistics for uncertainty calculation
    player_stats = {}
    updates = []
    batch_size = 10000
    processed = 0
    
    for rating in all_ratings:
        player_id = rating['player_id']
        match_date = rating['date']
        elo = rating['elo_rating']
        match_num = rating['career_match_number'] or 0
        
        # Initialize player stats if needed
        if player_id not in player_stats:
            player_stats[player_id] = {
                'elos': [],
                'last_date': None,
                'match_count': 0
            }
        
        stats = player_stats[player_id]
        stats['elos'].append(elo)
        stats['match_count'] = match_num
        
        # Calculate days since last match
        if stats['last_date']:
            days_since_last = (match_date - stats['last_date']).days
        else:
            days_since_last = 0
        
        stats['last_date'] = match_date
        
        # Calculate ELO standard deviation over recent window
        recent_window = min(50, len(stats['elos']))
        if recent_window >= 10:
            recent_elos = stats['elos'][-recent_window:]
            elo_std = float(np.std(recent_elos))
        else:
            elo_std = 0.0
        
        # Calculate overall uncertainty
        uncertainty = calculate_uncertainty(
            match_count=match_num,
            days_since_last_match=days_since_last,
            elo_std_dev=elo_std,
            recent_matches_count=recent_window
        )
        
        # For surface uncertainties, use a simplified approach
        # (In a full implementation, we'd track surface-specific stats)
        # For now, base it on match count with higher uncertainty
        surface_uncertainty_factor = 1.2  # Surfaces have less data
        clay_uncertainty = uncertainty * surface_uncertainty_factor
        grass_uncertainty = uncertainty * surface_uncertainty_factor * 1.3  # Grass has least matches
        hard_uncertainty = uncertainty * surface_uncertainty_factor * 0.9  # Hard has most matches
        
        # Prepare update
        updates.append({
            'rating_id': rating['rating_id'],
            'tsr_rating': elo,  # TSR = ELO
            'tsr_uncertainty': uncertainty,
            'clay_uncertainty': clay_uncertainty,
            'grass_uncertainty': grass_uncertainty,
            'hard_uncertainty': hard_uncertainty
        })
        
        processed += 1
        
        # Batch update database
        if len(updates) >= batch_size:
            _update_database_batch(db, updates)
            updates = []
            
            if processed % 100000 == 0:
                progress = processed / total_records * 100
                logger.info(f"Processed {processed:,} / {total_records:,} ({progress:.1f}%)")
    
    # Final batch
    if updates:
        _update_database_batch(db, updates)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("="*70)
    logger.info(f"✅ TSR calculation complete!")
    logger.info(f"✅ Processed {total_records:,} rating records")
    logger.info(f"✅ Updated {len(player_stats):,} players")
    logger.info(f"Calculation took {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info("="*70)
    
    # Show top players
    _show_top_players(db)
    
    # Validate against ELO
    _validate_tsr_vs_elo(db)


def _update_database_batch(db: DatabaseManager, updates: list):
    """Update TSR ratings in database (batch update)."""
    with db.get_cursor() as cursor:
        for update in updates:
            cursor.execute("""
                UPDATE player_ratings
                SET 
                    tsr_rating = %s,
                    tsr_uncertainty = %s,
                    clay_uncertainty = %s,
                    grass_uncertainty = %s,
                    hard_uncertainty = %s
                WHERE rating_id = %s
            """, (
                update['tsr_rating'],
                update['tsr_uncertainty'],
                update['clay_uncertainty'],
                update['grass_uncertainty'],
                update['hard_uncertainty'],
                update['rating_id']
            ))


def _show_top_players(db: DatabaseManager):
    """Display top players by TSR rating."""
    logger.info("\n" + "="*70)
    logger.info("TOP 10 PLAYERS BY PEAK TSR RATING:")
    logger.info("="*70)
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                pl.name,
                MAX(pr.tsr_rating) as peak_tsr,
                AVG(pr.tsr_uncertainty) as avg_uncertainty,
                COUNT(*) as matches
            FROM player_ratings pr
            JOIN players pl ON pr.player_id = pl.player_id
            WHERE pr.tsr_rating IS NOT NULL
            GROUP BY pl.player_id, pl.name
            ORDER BY peak_tsr DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        for i, row in enumerate(results, 1):
            logger.info(
                f"{i:>3}. {row['name']:<30} "
                f"TSR: {row['peak_tsr']:>7.1f} ± {row['avg_uncertainty']:>5.1f}  "
                f"({row['matches']:,} matches)"
            )


def _validate_tsr_vs_elo(db: DatabaseManager):
    """Validate that TSR matches ELO (sanity check)."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATION: TSR vs ELO (Big 3)")
    logger.info("="*70)
    
    with db.get_cursor() as cursor:
        for player in ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer']:
            cursor.execute("""
                SELECT 
                    MAX(pr.tsr_rating) as peak_tsr,
                    MAX(pr.elo_rating) as peak_elo,
                    AVG(pr.tsr_uncertainty) as avg_uncertainty,
                    MIN(pr.tsr_uncertainty) as min_uncertainty
                FROM player_ratings pr
                JOIN players pl ON pr.player_id = pl.player_id
                WHERE pl.name = %s
            """, (player,))
            
            result = cursor.fetchone()
            
            match = "✅ MATCH" if abs(result['peak_tsr'] - result['peak_elo']) < 0.1 else "❌ MISMATCH"
            
            logger.info(
                f"{player:20} TSR: {result['peak_tsr']:7.1f}  |  "
                f"ELO: {result['peak_elo']:7.1f}  |  "
                f"Uncertainty: {result['avg_uncertainty']:5.1f} (min: {result['min_uncertainty']:5.1f})  {match}"
            )


if __name__ == '__main__':
    calculate_bayesian_ratings()
    
    logger.info("\n" + "="*70)
    logger.info("✅ SCRIPT 2 COMPLETE - TSR ratings with uncertainty calculated!")
    logger.info("="*70)
    logger.info("\nNext steps:")
    logger.info("  1. Run Script 3: python scripts/smooth_trajectories.py")
    logger.info("  2. Run Script 4: python scripts/calculate_supporting_metrics.py")
