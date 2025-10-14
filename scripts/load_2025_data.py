"""
Load only the 2025 converted data into the database.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from parse_and_load_data import TennisDataParser
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Load only 2025 data"""
    logger.info("=" * 70)
    logger.info("LOADING 2025 MATCH DATA")
    logger.info("=" * 70)
    
    # Initialize
    db = DatabaseManager()
    parser = TennisDataParser(db)
    
    # Load the converted 2025 file
    file_path = Path('/Users/razaool/tennis-career-tracker/data/raw/atp_matches_2025_converted.csv')
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return
    
    logger.info(f"\nLoading: {file_path.name}")
    
    try:
        matches_data = parser.parse_match_file(file_path)
        
        if matches_data:
            inserted = db.bulk_insert_matches(matches_data)
            logger.info(f"✅ Inserted {inserted} matches from 2025")
        else:
            logger.warning("No matches to insert")
    
    except Exception as e:
        logger.error(f"Error loading 2025 data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Show stats
    logger.info("\n" + "=" * 70)
    logger.info("DATABASE SUMMARY")
    logger.info("=" * 70)
    stats = db.get_database_stats()
    for table, count in stats.items():
        logger.info(f"  {table}: {count:,} rows")
    
    # Check latest matches
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT date, tournament_name, COUNT(*) as match_count
            FROM matches
            WHERE date >= '2025-01-01'
            GROUP BY date, tournament_name
            ORDER BY date DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()
        
        if recent:
            logger.info("\n" + "=" * 70)
            logger.info("RECENT 2025 MATCHES:")
            logger.info("=" * 70)
            for r in recent:
                logger.info(f"  {r['date']}: {r['tournament_name']} ({r['match_count']} matches)")
    
    logger.info("\n✅ 2025 DATA LOADED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

