"""
Update tennis match data from December 18, 2024 onwards.

This script:
1. Downloads latest data from Tennis Abstract (if available)
2. Parses new matches
3. Updates the database
4. Recalculates ELO ratings for affected players
"""
import sys
from pathlib import Path
import requests
import logging
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from config import RAW_DATA_DIR
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_latest_data(year=2025):
    """
    Download latest match data from Tennis Abstract.
    
    Args:
        year: Year to download (default: 2025)
    
    Returns:
        Path to downloaded file, or None if not available
    """
    url = f"https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_{year}.csv"
    output_file = RAW_DATA_DIR / f"atp_matches_{year}.csv"
    
    logger.info(f"Checking for {year} data at: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            # Count lines (matches)
            with open(output_file, 'r') as f:
                line_count = sum(1 for _ in f) - 1  # Subtract header
            
            logger.info(f"✅ Downloaded {year} data: {line_count} matches")
            logger.info(f"   Saved to: {output_file}")
            return output_file
        
        elif response.status_code == 404:
            logger.warning(f"⚠️  {year} data not yet available on Tennis Abstract")
            logger.info(f"   URL: {url}")
            return None
        
        else:
            logger.error(f"❌ Unexpected status code: {response.status_code}")
            return None
    
    except requests.RequestException as e:
        logger.error(f"❌ Network error: {e}")
        return None


def check_last_match_in_db(db):
    """Check the most recent match date in the database"""
    with db.get_cursor() as cursor:
        cursor.execute("SELECT MAX(date) as last_date FROM matches")
        result = cursor.fetchone()
        return result['last_date'] if result else None


def get_match_count_after_date(db, date):
    """Count matches after a specific date in the database"""
    with db.get_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) as count FROM matches WHERE date > %s",
            (date,)
        )
        result = cursor.fetchone()
        return result['count'] if result else 0


def update_database_with_new_data(year=2025):
    """
    Update database with new match data.
    
    Args:
        year: Year to update
    
    Returns:
        Number of new matches added
    """
    db = DatabaseManager()
    
    # Check current state
    last_date = check_last_match_in_db(db)
    logger.info(f"📅 Current database last match: {last_date}")
    
    # Download new data
    data_file = download_latest_data(year)
    
    if not data_file:
        logger.warning(f"⚠️  No new data available for {year}")
        logger.info("\n" + "=" * 80)
        logger.info("ALTERNATIVE DATA SOURCES:")
        logger.info("=" * 80)
        logger.info("""
1. Tennis Abstract GitHub (automated):
   - Usually updated within 1-2 weeks of matches
   - URL: https://github.com/JeffSackmann/tennis_atp
   
2. Ultimate Tennis Statistics (manual download):
   - More up-to-date, but requires manual download
   - URL: https://www.ultimatetennisstatistics.com/
   - Export matches as CSV
   
3. ATP Official Website (manual scraping):
   - Most current data
   - URL: https://www.atptour.com/en/scores/results-archive
   - Requires web scraping (more complex)
   
4. Wait for Tennis Abstract to update:
   - Check back in a few days
   - They typically update monthly
        """)
        return 0
    
    # Parse and load new data
    logger.info(f"\n📊 Parsing {year} data...")
    
    try:
        # Use existing parse_and_load_data script
        result = subprocess.run(
            ['python3', 'scripts/parse_and_load_data.py', str(data_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            logger.info("✅ Successfully parsed and loaded new data")
            
            # Count new matches
            new_count = get_match_count_after_date(db, last_date)
            logger.info(f"📈 Added {new_count} new matches since {last_date}")
            
            return new_count
        else:
            logger.error(f"❌ Error parsing data: {result.stderr}")
            return 0
    
    except Exception as e:
        logger.error(f"❌ Error updating database: {e}")
        return 0


def recalculate_elo_ratings():
    """Recalculate ELO ratings after adding new matches"""
    logger.info("\n🔄 Recalculating ELO ratings...")
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/calculate_elo.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            logger.info("✅ ELO ratings recalculated successfully")
            return True
        else:
            logger.error(f"❌ Error recalculating ELO: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error running ELO calculation: {e}")
        return False


def regenerate_exports():
    """Regenerate all export files with updated data"""
    logger.info("\n📤 Regenerating export files...")
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/export_visualization_data.py'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            logger.info("✅ Export files regenerated successfully")
            return True
        else:
            logger.error(f"❌ Error regenerating exports: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error running export: {e}")
        return False


def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("TENNIS DATA UPDATE SCRIPT")
    logger.info("=" * 80)
    logger.info(f"Target: Get matches from December 18, 2024 to {datetime.now().strftime('%B %d, %Y')}")
    logger.info("=" * 80)
    
    # Step 1: Update database with new data
    new_matches = update_database_with_new_data(year=2025)
    
    if new_matches == 0:
        logger.info("\n⚠️  No new data to process. Exiting.")
        return
    
    # Step 2: Recalculate ELO ratings
    if not recalculate_elo_ratings():
        logger.error("❌ Failed to recalculate ELO ratings")
        return
    
    # Step 3: Regenerate exports
    if not regenerate_exports():
        logger.error("❌ Failed to regenerate exports")
        return
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("✅ UPDATE COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"New matches added: {new_matches}")
    logger.info("ELO ratings: Recalculated ✅")
    logger.info("Export files: Regenerated ✅")
    logger.info("\nYour data is now up to date!")


if __name__ == "__main__":
    main()

