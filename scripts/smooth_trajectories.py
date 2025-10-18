#!/usr/bin/env python3
"""
Smooth career trajectories using moving averages and spline interpolation.

This script creates smoothed TSR curves for cleaner visualizations by:
1. Applying rolling averages to reduce noise
2. Using spline interpolation for smooth curves
3. Populating tsr_smoothed column in player_ratings table

Smoothed curves are essential for professional-looking career progression charts.
"""

import logging
from datetime import datetime
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.ndimage import uniform_filter1d
import sys
sys.path.insert(0, '/Users/razaool/tennis-career-tracker')
from database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


def smooth_player_trajectory(tsr_values: np.array, window_size: int = 20) -> np.array:
    """
    Smooth a player's TSR trajectory using a combination of techniques.
    
    Args:
        tsr_values: Array of TSR ratings over time
        window_size: Size of moving average window
        
    Returns:
        Smoothed TSR values
    """
    if len(tsr_values) < 5:
        # Not enough data to smooth
        return tsr_values
    
    # Apply rolling average for initial smoothing
    # This reduces noise while preserving overall shape
    if len(tsr_values) >= window_size:
        # Use uniform filter for rolling average
        smoothed = uniform_filter1d(tsr_values, size=window_size, mode='nearest')
    else:
        # For shorter sequences, use smaller window
        window = min(5, len(tsr_values))
        smoothed = uniform_filter1d(tsr_values, size=window, mode='nearest')
    
    # Apply spline interpolation for additional smoothness
    # Only apply if we have enough points
    if len(smoothed) >= 10:
        try:
            # Create x-axis (match numbers)
            x = np.arange(len(smoothed))
            
            # Fit smoothing spline with moderate smoothing factor
            # s parameter controls smoothness (higher = smoother)
            s_factor = len(smoothed) * 10  # Adaptive smoothing
            spline = UnivariateSpline(x, smoothed, s=s_factor, k=3)
            
            # Generate smoothed values
            smoothed = spline(x)
            
        except Exception as e:
            # If spline fails, just use rolling average
            logger.debug(f"Spline interpolation failed: {e}, using rolling average only")
    
    return smoothed


def calculate_smoothed_trajectories():
    """
    Calculate smooth trajectories for all players.
    Populates tsr_smoothed column in player_ratings table.
    """
    logger.info("="*70)
    logger.info("SMOOTHING CAREER TRAJECTORIES")
    logger.info("="*70)
    logger.info("Method: Rolling Average + Spline Interpolation")
    
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
        # Get all ratings for this player in chronological order
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    rating_id,
                    tsr_rating,
                    career_match_number
                FROM player_ratings
                WHERE player_id = %s
                  AND tsr_rating IS NOT NULL
                ORDER BY date, match_id
            """, (player_id,))
            
            ratings = cursor.fetchall()
        
        if not ratings:
            continue
        
        # Extract TSR values
        rating_ids = [r['rating_id'] for r in ratings]
        tsr_values = np.array([r['tsr_rating'] for r in ratings], dtype=float)
        
        # Smooth the trajectory
        smoothed_values = smooth_player_trajectory(tsr_values)
        
        # Update database
        updates = []
        for rating_id, smoothed_tsr in zip(rating_ids, smoothed_values):
            updates.append({
                'rating_id': rating_id,
                'tsr_smoothed': float(smoothed_tsr)
            })
        
        # Batch update
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
    logger.info(f"✅ Trajectory smoothing complete!")
    logger.info(f"✅ Processed {processed_players:,} players")
    logger.info(f"✅ Updated {total_updates:,} rating records")
    logger.info(f"Calculation took {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info("="*70)
    
    # Show sample smoothed trajectories
    _show_smoothing_examples(db)


def _update_database_batch(db: DatabaseManager, updates: list):
    """Update smoothed TSR values in database."""
    with db.get_cursor() as cursor:
        for update in updates:
            cursor.execute("""
                UPDATE player_ratings
                SET tsr_smoothed = %s
                WHERE rating_id = %s
            """, (
                update['tsr_smoothed'],
                update['rating_id']
            ))


def _show_smoothing_examples(db: DatabaseManager):
    """Display smoothing examples for Big 3."""
    logger.info("\n" + "="*70)
    logger.info("SMOOTHING EXAMPLES (Big 3):")
    logger.info("="*70)
    
    with db.get_cursor() as cursor:
        for player in ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer']:
            cursor.execute("""
                SELECT 
                    pl.name,
                    COUNT(*) as total_ratings,
                    AVG(ABS(pr.tsr_rating - pr.tsr_smoothed)) as avg_smoothing,
                    MAX(ABS(pr.tsr_rating - pr.tsr_smoothed)) as max_smoothing
                FROM player_ratings pr
                JOIN players pl ON pr.player_id = pl.player_id
                WHERE pl.name = %s
                  AND pr.tsr_smoothed IS NOT NULL
                GROUP BY pl.name
            """, (player,))
            
            result = cursor.fetchone()
            
            if result:
                logger.info(
                    f"{result['name']:<20} "
                    f"Ratings: {result['total_ratings']:>5,}  |  "
                    f"Avg smoothing: {result['avg_smoothing']:>5.1f}  |  "
                    f"Max smoothing: {result['max_smoothing']:>6.1f}"
                )
    
    # Show sample trajectory comparison
    logger.info("\n" + "="*70)
    logger.info("SAMPLE: Novak Djokovic - Last 10 matches")
    logger.info("="*70)
    logger.info(f"{'Match':<10} {'Original TSR':<15} {'Smoothed TSR':<15} {'Difference':<12}")
    logger.info("-" * 70)
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                pr.career_match_number,
                pr.tsr_rating,
                pr.tsr_smoothed
            FROM player_ratings pr
            JOIN players pl ON pr.player_id = pl.player_id
            WHERE pl.name = 'Novak Djokovic'
              AND pr.tsr_smoothed IS NOT NULL
            ORDER BY pr.date DESC, pr.match_id DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        for row in reversed(results):
            diff = row['tsr_rating'] - row['tsr_smoothed']
            logger.info(
                f"{row['career_match_number']:<10} "
                f"{row['tsr_rating']:<15.1f} "
                f"{row['tsr_smoothed']:<15.1f} "
                f"{diff:>+7.1f}"
            )


if __name__ == '__main__':
    calculate_smoothed_trajectories()
    
    logger.info("\n" + "="*70)
    logger.info("✅ SCRIPT 3 COMPLETE - Career trajectories smoothed!")
    logger.info("="*70)
    logger.info("\nNext steps:")
    logger.info("  1. Run Script 4: python scripts/calculate_supporting_metrics.py")
    logger.info("  2. Re-export visualization data with TSR + smoothed curves")

