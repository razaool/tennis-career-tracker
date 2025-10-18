"""
Parse Tennis Abstract CSV files and load into PostgreSQL database
Handles ATP match data with proper tournament tier mapping
"""
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path to import config and db_manager
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import RAW_DATA_DIR, TOURNAMENT_TIERS, SURFACES
from database.db_manager import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TennisDataParser:
    """Parse and load Tennis Abstract data into database"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.raw_data_dir = RAW_DATA_DIR
        self.player_cache = {}  # Cache player IDs to avoid repeated lookups
    
    def map_tournament_tier(self, tourney_level, tourney_name):
        """
        Map Tennis Abstract tournament level to our tier system
        
        Tennis Abstract levels:
        - G = Grand Slam
        - M = Masters 1000
        - A = ATP 500
        - D = Davis Cup
        - F = Tour Finals
        """
        tier_mapping = {
            'G': 'Grand Slam',
            'F': 'ATP Finals',
            'M': 'Masters 1000',
            'A': 'ATP 500',
            'D': 'Davis Cup',
            'O': 'Olympics',
        }
        
        # Direct mapping
        if tourney_level in tier_mapping:
            return tier_mapping[tourney_level]
        
        # Fallback: try to infer from tournament name
        if tourney_name:
            name_lower = tourney_name.lower()
            if 'grand slam' in name_lower or any(slam in name_lower for slam in ['wimbledon', 'roland garros', 'us open', 'australian open']):
                return 'Grand Slam'
            elif 'masters' in name_lower:
                return 'Masters 1000'
            elif 'finals' in name_lower:
                return 'ATP Finals'
            elif 'challenger' in name_lower:
                return 'Challenger'
            elif 'davis cup' in name_lower:
                return 'Davis Cup'
            elif 'olympics' in name_lower:
                return 'Olympics'
        
        # Default to ATP 250 for unknown
        return 'ATP 250'
    
    def get_or_create_player(self, player_name):
        """Get player ID, creating if necessary (with caching)"""
        if not player_name or pd.isna(player_name):
            return None
        
        if player_name in self.player_cache:
            return self.player_cache[player_name]
        
        player_id = self.db.get_player_id(player_name)
        self.player_cache[player_name] = player_id
        return player_id
    
    def parse_score_details(self, score):
        """
        Parse score string to extract sets won and total games
        Returns: (sets_p1, sets_p2, games_p1, games_p2)
        """
        if not score or pd.isna(score):
            return None, None, None, None
        
        try:
            sets_p1 = 0
            sets_p2 = 0
            games_p1 = 0
            games_p2 = 0
            
            # Split by space to get individual sets
            sets = score.split()
            
            for set_score in sets:
                # Remove tiebreak scores (e.g., "7-6(3)" -> "7-6")
                if '(' in set_score:
                    set_score = set_score.split('(')[0]
                
                # Parse games
                if '-' in set_score:
                    parts = set_score.split('-')
                    if len(parts) == 2:
                        try:
                            g1, g2 = int(parts[0]), int(parts[1])
                            games_p1 += g1
                            games_p2 += g2
                            
                            # Determine set winner
                            if g1 > g2:
                                sets_p1 += 1
                            elif g2 > g1:
                                sets_p2 += 1
                        except ValueError:
                            continue
            
            return sets_p1, sets_p2, games_p1, games_p2
        
        except Exception as e:
            logger.debug(f"Error parsing score '{score}': {e}")
            return None, None, None, None
    
    def parse_match_file(self, file_path):
        """Parse a single Tennis Abstract match CSV file"""
        logger.info(f"Parsing {file_path.name}...")
        
        try:
            # Read CSV with Tennis Abstract schema
            df = pd.read_csv(file_path, low_memory=False)
            logger.info(f"  Loaded {len(df)} matches from {file_path.name}")
            
            # Show column names for debugging
            logger.debug(f"  Columns: {df.columns.tolist()}")
            
            matches_data = []
            
            for idx, row in df.iterrows():
                # Get player IDs
                winner_name = row.get('winner_name')
                loser_name = row.get('loser_name')
                
                if pd.isna(winner_name) or pd.isna(loser_name):
                    continue
                
                winner_id = self.get_or_create_player(winner_name)
                loser_id = self.get_or_create_player(loser_name)
                
                if not winner_id or not loser_id:
                    continue
                
                # Parse date
                try:
                    match_date = pd.to_datetime(str(row.get('tourney_date')), format='%Y%m%d').date()
                except:
                    continue
                
                # Determine tournament tier
                tourney_level = row.get('tourney_level', '')
                tourney_name = row.get('tourney_name', '')
                tournament_tier = self.map_tournament_tier(tourney_level, tourney_name)
                
                # Parse surface
                surface_raw = row.get('surface', '')
                if pd.isna(surface_raw) or not surface_raw:
                    surface = 'hard'  # Default for missing/NaN
                else:
                    surface = str(surface_raw).lower()
                    if surface not in SURFACES:
                        surface = 'hard'  # Default
                
                # Parse score
                score = row.get('score', '')
                sets_w, sets_l, games_w, games_l = self.parse_score_details(score)
                
                # Best of 3 or 5 (Grand Slams are best of 5)
                best_of = 5 if tournament_tier == 'Grand Slam' else 3
                
                # Build match data
                match_data = {
                    'tourney_id': row.get('tourney_id'),
                    'match_num': row.get('match_num'),
                    'date': match_date,
                    'tournament_name': tourney_name,
                    'tournament_tier': tournament_tier,
                    'surface': surface,
                    'round': row.get('round', ''),
                    'best_of': best_of,
                    'player1_id': winner_id,
                    'player2_id': loser_id,
                    'winner_id': winner_id,
                    'player1_rank': self._safe_int(row.get('winner_rank')),
                    'player2_rank': self._safe_int(row.get('loser_rank')),
                    'player1_rank_points': self._safe_int(row.get('winner_rank_points')),
                    'player2_rank_points': self._safe_int(row.get('loser_rank_points')),
                    'score': score,
                    'player1_sets_won': sets_w,
                    'player2_sets_won': sets_l,
                    'player1_games_won': games_w,
                    'player2_games_won': games_l,
                    'player1_aces': self._safe_int(row.get('w_ace')),
                    'player2_aces': self._safe_int(row.get('l_ace')),
                    'player1_double_faults': self._safe_int(row.get('w_df')),
                    'player2_double_faults': self._safe_int(row.get('l_df')),
                    'player1_first_serve_pct': self._safe_float(row.get('w_1stIn'), row.get('w_svpt')),
                    'player2_first_serve_pct': self._safe_float(row.get('l_1stIn'), row.get('l_svpt')),
                }
                
                matches_data.append(match_data)
            
            return matches_data
        
        except Exception as e:
            logger.error(f"Error parsing {file_path.name}: {e}")
            return []
    
    def _safe_int(self, value):
        """Safely convert to int, return None if invalid"""
        try:
            return int(value) if not pd.isna(value) else None
        except:
            return None
    
    def _safe_float(self, numerator, denominator):
        """Safely calculate percentage"""
        try:
            if pd.isna(numerator) or pd.isna(denominator):
                return None
            num = float(numerator)
            denom = float(denominator)
            if denom > 0:
                return num / denom
        except:
            return None
        return None
    
    def load_atp_data(self, start_year=None, end_year=None):
        """
        Load ATP match data into database
        
        Args:
            start_year: Start year (inclusive), None for all
            end_year: End year (inclusive), None for all
        """
        atp_data_dir = self.raw_data_dir / "tennis_atp"
        
        if not atp_data_dir.exists():
            raise FileNotFoundError(f"ATP data directory not found: {atp_data_dir}")
        
        # Get all match files
        match_files = sorted(atp_data_dir.glob("atp_matches_*.csv"))
        
        if not match_files:
            raise FileNotFoundError(f"No ATP match files found in {atp_data_dir}")
        
        # Filter by year range
        if start_year or end_year:
            filtered_files = []
            for f in match_files:
                year_str = f.stem.split('_')[-1]
                if year_str.isdigit():
                    year = int(year_str)
                    if (not start_year or year >= start_year) and (not end_year or year <= end_year):
                        filtered_files.append(f)
            match_files = filtered_files
        
        logger.info(f"Loading {len(match_files)} match files into database...")
        
        total_matches = 0
        for match_file in match_files:
            matches_data = self.parse_match_file(match_file)
            
            if matches_data:
                inserted = self.db.bulk_insert_matches(matches_data)
                total_matches += inserted
        
        logger.info(f"✅ Successfully loaded {total_matches} matches")
        logger.info(f"✅ Loaded {len(self.player_cache)} players")
        
        return total_matches
    
    def update_player_metadata(self):
        """Update player metadata from Tennis Abstract player file"""
        atp_data_dir = self.raw_data_dir / "tennis_atp"
        player_file = atp_data_dir / "atp_players.csv"
        
        if not player_file.exists():
            logger.warning(f"Player metadata file not found: {player_file}")
            return
        
        logger.info("Updating player metadata...")
        
        df = pd.read_csv(player_file)
        
        with self.db.get_cursor(dict_cursor=False) as cursor:
            for _, row in df.iterrows():
                player_name = f"{row.get('name_first', '')} {row.get('name_last', '')}".strip()
                
                if not player_name:
                    continue
                
                # Get DOB
                dob = None
                if not pd.isna(row.get('dob')):
                    try:
                        dob = pd.to_datetime(str(int(row.get('dob'))), format='%Y%m%d').date()
                    except:
                        pass
                
                # Update player record
                cursor.execute("""
                    UPDATE players 
                    SET date_of_birth = %s,
                        country = %s,
                        hand = %s,
                        height_cm = %s
                    WHERE name = %s
                """, (
                    dob,
                    row.get('ioc'),
                    row.get('hand'),
                    self._safe_int(row.get('height')),
                    player_name
                ))
        
        logger.info("✅ Player metadata updated")


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Tennis Data Parser and Loader")
    logger.info("=" * 60)
    
    # Initialize database
    db = DatabaseManager()
    parser = TennisDataParser(db)
    
    # Parse and load data
    # Start with recent years for faster testing (2000-2024)
    # Remove year filters to load all historical data
    start_year = 2000
    end_year = 2024
    
    logger.info(f"\nLoading matches from {start_year} to {end_year}...")
    total_matches = parser.load_atp_data(start_year=start_year, end_year=end_year)
    
    # Update player metadata
    parser.update_player_metadata()
    
    # Show final stats
    logger.info("\n" + "=" * 60)
    logger.info("Database Summary")
    logger.info("=" * 60)
    stats = db.get_database_stats()
    for table, count in stats.items():
        logger.info(f"  {table}: {count:,} rows")
    
    logger.info("\n✅ Data loading complete!")


if __name__ == "__main__":
    main()

