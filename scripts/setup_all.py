"""
Complete setup script - runs everything in order:
1. Initialize database
2. Download Tennis Abstract data
3. Parse and load data into database
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import init_database
from scripts.download_tennis_data import TennisDataDownloader
from scripts.parse_and_load_data import TennisDataParser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_complete_setup(start_year=2000, end_year=2024):
    """
    Run complete setup process
    
    Args:
        start_year: Start year for data loading (default 2000)
        end_year: End year for data loading (default 2024)
    """
    logger.info("=" * 70)
    logger.info("TENNIS CAREER TRACKER - COMPLETE SETUP")
    logger.info("=" * 70)
    
    # Step 1: Initialize Database
    logger.info("\n📊 STEP 1: Initializing Database...")
    logger.info("-" * 70)
    try:
        db = init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False
    
    # Step 2: Download Data
    logger.info("\n📥 STEP 2: Downloading Tennis Abstract Data...")
    logger.info("-" * 70)
    try:
        downloader = TennisDataDownloader()
        downloader.download_repo('atp')
        logger.info("✅ Data download complete")
    except Exception as e:
        logger.error(f"❌ Data download failed: {e}")
        return False
    
    # Step 3: Parse and Load Data
    logger.info("\n🔄 STEP 3: Parsing and Loading Data...")
    logger.info("-" * 70)
    logger.info(f"Loading matches from {start_year} to {end_year}...")
    try:
        parser = TennisDataParser(db)
        total_matches = parser.load_atp_data(start_year=start_year, end_year=end_year)
        parser.update_player_metadata()
        logger.info(f"✅ Loaded {total_matches:,} matches")
    except Exception as e:
        logger.error(f"❌ Data loading failed: {e}")
        return False
    
    # Final Summary
    logger.info("\n" + "=" * 70)
    logger.info("📈 SETUP COMPLETE - DATABASE SUMMARY")
    logger.info("=" * 70)
    
    stats = db.get_database_stats()
    for table, count in stats.items():
        emoji = "✅" if count > 0 else "⚠️"
        logger.info(f"  {emoji} {table}: {count:,} rows")
    
    logger.info("\n" + "=" * 70)
    logger.info("🎾 Tennis Career Tracker is ready!")
    logger.info("=" * 70)
    logger.info("\nNext steps:")
    logger.info("  1. Run Bayesian ELO calculations: python scripts/calculate_ratings.py")
    logger.info("  2. Start the API server: uvicorn api.main:app --reload")
    logger.info("  3. Build visualizations in the frontend")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Tennis Career Tracker database')
    parser.add_argument('--start-year', type=int, default=2000, help='Start year for data (default: 2000)')
    parser.add_argument('--end-year', type=int, default=2024, help='End year for data (default: 2024)')
    parser.add_argument('--all-years', action='store_true', help='Load all available historical data')
    
    args = parser.parse_args()
    
    start_year = None if args.all_years else args.start_year
    end_year = None if args.all_years else args.end_year
    
    success = run_complete_setup(start_year=start_year, end_year=end_year)
    
    sys.exit(0 if success else 1)

