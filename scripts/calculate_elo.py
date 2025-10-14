"""
Calculate ELO ratings for all tennis players based on match history.

This script processes all matches chronologically and calculates:
- Overall ELO rating
- Surface-specific ELO ratings (clay, grass, hard)

ELO ratings are stored in the player_ratings table.
"""
import sys
from pathlib import Path
from collections import defaultdict
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import INITIAL_ELO, BASE_K_FACTOR, TOURNAMENT_TIERS, SURFACES
from database.db_manager import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TennisELOCalculator:
    """Calculate ELO ratings for tennis players"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.initial_elo = INITIAL_ELO
        self.base_k = BASE_K_FACTOR
        
        # Store current ELO for each player (overall and by surface)
        self.player_elos = defaultdict(lambda: {
            'overall': self.initial_elo,
            'clay': self.initial_elo,
            'grass': self.initial_elo,
            'hard': self.initial_elo,
            'carpet': self.initial_elo
        })
        
        # Track career match number for each player
        self.career_match_count = defaultdict(int)
    
    def get_k_factor(self, tournament_tier):
        """
        Get K-factor based on tournament importance.
        Higher K = more rating change per match.
        """
        if not tournament_tier or tournament_tier not in TOURNAMENT_TIERS:
            return self.base_k
        
        tier_weight = TOURNAMENT_TIERS[tournament_tier]['weight']
        return self.base_k * tier_weight
    
    def calculate_expected_score(self, rating_a, rating_b):
        """
        Calculate expected score for player A.
        Returns probability between 0 and 1.
        """
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_elo(self, winner_elo, loser_elo, k_factor):
        """
        Update ELO ratings after a match.
        Returns (new_winner_elo, new_loser_elo)
        """
        expected_winner = self.calculate_expected_score(winner_elo, loser_elo)
        
        # Winner gets positive change, loser gets negative
        winner_new = winner_elo + k_factor * (1 - expected_winner)
        loser_new = loser_elo + k_factor * (0 - (1 - expected_winner))
        
        return winner_new, loser_new
    
    def process_match(self, match):
        """
        Process a single match and update ELO ratings.
        Returns rating data to store in database.
        """
        winner_id = match['winner_id']
        loser_id = match['player1_id'] if match['winner_id'] == match['player2_id'] else match['player2_id']
        surface = match['surface'] if match['surface'] in SURFACES else 'hard'
        tournament_tier = match['tournament_tier']
        
        # Get K-factor for this tournament
        k_factor = self.get_k_factor(tournament_tier)
        
        # Get current ELOs
        winner_overall = self.player_elos[winner_id]['overall']
        loser_overall = self.player_elos[loser_id]['overall']
        winner_surface = self.player_elos[winner_id][surface]
        loser_surface = self.player_elos[loser_id][surface]
        
        # Update overall ELO
        winner_overall_new, loser_overall_new = self.update_elo(
            winner_overall, loser_overall, k_factor
        )
        
        # Update surface-specific ELO
        winner_surface_new, loser_surface_new = self.update_elo(
            winner_surface, loser_surface, k_factor
        )
        
        # Store new ratings
        self.player_elos[winner_id]['overall'] = winner_overall_new
        self.player_elos[loser_id]['overall'] = loser_overall_new
        self.player_elos[winner_id][surface] = winner_surface_new
        self.player_elos[loser_id][surface] = loser_surface_new
        
        # Increment career match count
        self.career_match_count[winner_id] += 1
        self.career_match_count[loser_id] += 1
        
        # Prepare rating records for database
        winner_rating = {
            'player_id': winner_id,
            'match_id': match['match_id'],
            'date': match['date'],
            'career_match_number': self.career_match_count[winner_id],
            'elo_rating': round(winner_overall_new, 2),
            'elo_clay': round(self.player_elos[winner_id]['clay'], 2),
            'elo_grass': round(self.player_elos[winner_id]['grass'], 2),
            'elo_hard': round(self.player_elos[winner_id]['hard'], 2),
            'model_version': 'v1.0'
        }
        
        loser_rating = {
            'player_id': loser_id,
            'match_id': match['match_id'],
            'date': match['date'],
            'career_match_number': self.career_match_count[loser_id],
            'elo_rating': round(loser_overall_new, 2),
            'elo_clay': round(self.player_elos[loser_id]['clay'], 2),
            'elo_grass': round(self.player_elos[loser_id]['grass'], 2),
            'elo_hard': round(self.player_elos[loser_id]['hard'], 2),
            'model_version': 'v1.0'
        }
        
        return [winner_rating, loser_rating]
    
    def calculate_all_elos(self, batch_size=1000):
        """
        Process all matches and calculate ELO ratings.
        """
        logger.info("Starting ELO calculation for all matches...")
        
        # Get all matches ordered by date
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT match_id, date, player1_id, player2_id, winner_id,
                       surface, tournament_tier
                FROM matches
                ORDER BY date, match_id
            """)
            
            matches = cursor.fetchall()
            total_matches = len(matches)
            logger.info(f"Processing {total_matches:,} matches...")
        
        # Process matches in batches
        ratings_batch = []
        processed = 0
        
        for match in matches:
            # Process match and get rating updates
            rating_updates = self.process_match(match)
            ratings_batch.extend(rating_updates)
            
            # Insert batch when full
            if len(ratings_batch) >= batch_size:
                self._insert_ratings_batch(ratings_batch)
                processed += len(ratings_batch) // 2  # Divide by 2 (winner + loser)
                logger.info(f"Processed {processed:,} / {total_matches:,} matches "
                          f"({100 * processed / total_matches:.1f}%)")
                ratings_batch = []
        
        # Insert remaining ratings
        if ratings_batch:
            self._insert_ratings_batch(ratings_batch)
            processed += len(ratings_batch) // 2
        
        logger.info(f"✅ ELO calculation complete! Processed {processed:,} matches")
        logger.info(f"✅ Calculated ratings for {len(self.player_elos):,} players")
    
    def _insert_ratings_batch(self, ratings_batch):
        """Insert a batch of ratings into the database."""
        if not ratings_batch:
            return
        
        with self.db.get_cursor(dict_cursor=False) as cursor:
            insert_query = """
                INSERT INTO player_ratings (
                    player_id, match_id, date, career_match_number,
                    elo_rating, elo_clay, elo_grass, elo_hard, model_version
                ) VALUES (
                    %(player_id)s, %(match_id)s, %(date)s, %(career_match_number)s,
                    %(elo_rating)s, %(elo_clay)s, %(elo_grass)s, %(elo_hard)s,
                    %(model_version)s
                )
                ON CONFLICT (player_id, match_id) 
                DO UPDATE SET
                    elo_rating = EXCLUDED.elo_rating,
                    elo_clay = EXCLUDED.elo_clay,
                    elo_grass = EXCLUDED.elo_grass,
                    elo_hard = EXCLUDED.elo_hard,
                    model_version = EXCLUDED.model_version
            """
            
            cursor.executemany(insert_query, ratings_batch)
    
    def get_top_rated_players(self, n=10):
        """Get top N players by current ELO rating."""
        player_ratings = [
            (player_id, ratings['overall'], self.career_match_count[player_id])
            for player_id, ratings in self.player_elos.items()
        ]
        
        # Sort by ELO (descending)
        player_ratings.sort(key=lambda x: x[1], reverse=True)
        
        # Get player names
        with self.db.get_cursor() as cursor:
            top_players = []
            for player_id, elo, matches in player_ratings[:n]:
                cursor.execute(
                    "SELECT name FROM players WHERE player_id = %s",
                    (player_id,)
                )
                result = cursor.fetchone()
                if result:
                    top_players.append({
                        'name': result['name'],
                        'elo': round(elo, 1),
                        'matches': matches
                    })
        
        return top_players


def main():
    """Main execution function"""
    logger.info("=" * 70)
    logger.info("TENNIS ELO CALCULATOR - Script 1 of 5")
    logger.info("=" * 70)
    
    # Initialize database
    db = DatabaseManager()
    
    # Check if we already have ratings
    with db.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM player_ratings WHERE elo_rating IS NOT NULL")
        existing = cursor.fetchone()['count']
        
        if existing > 0:
            logger.warning(f"Found {existing:,} existing ELO ratings in database")
            response = input("Do you want to recalculate? This will overwrite existing data. (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Aborting. No changes made.")
                return
            logger.info("Recalculating all ELO ratings...")
    
    # Calculate ELO ratings
    calculator = TennisELOCalculator(db)
    
    start_time = datetime.now()
    calculator.calculate_all_elos(batch_size=1000)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Calculation took {duration:.1f} seconds ({duration/60:.1f} minutes)")
    
    # Show top players
    logger.info("\n" + "=" * 70)
    logger.info("TOP 10 PLAYERS BY CURRENT ELO RATING:")
    logger.info("=" * 70)
    
    top_players = calculator.get_top_rated_players(n=10)
    for i, player in enumerate(top_players, 1):
        logger.info(f"  {i:2d}. {player['name']:30s} ELO: {player['elo']:7.1f} ({player['matches']:,} matches)")
    
    # Verify database
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count FROM player_ratings WHERE elo_rating IS NOT NULL
        """)
        total_ratings = cursor.fetchone()['count']
        logger.info(f"\n✅ Stored {total_ratings:,} ELO ratings in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ SCRIPT 1 COMPLETE - ELO ratings calculated!")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("  1. Run Script 2: python scripts/calculate_bayesian_ratings.py")
    logger.info("  2. Run Script 3: python scripts/smooth_trajectories.py")
    logger.info("  3. Run Script 4: python scripts/calculate_supporting_metrics.py")
    logger.info("  4. Run Script 5: python scripts/update_career_stats.py")


if __name__ == "__main__":
    main()

