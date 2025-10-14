"""
Quick test script to verify database setup and data loading
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test database connection"""
    logger.info("Testing database connection...")
    try:
        db = DatabaseManager()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()['version']
            logger.info(f"✅ Connected to: {version[:50]}...")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def test_tables_exist():
    """Test that all required tables exist"""
    logger.info("\nTesting table existence...")
    db = DatabaseManager()
    required_tables = ['players', 'matches', 'player_ratings', 'player_career_stats', 'tournament_tiers']
    
    all_exist = True
    for table in required_tables:
        exists = db.table_exists(table)
        status = "✅" if exists else "❌"
        logger.info(f"  {status} {table}")
        if not exists:
            all_exist = False
    
    return all_exist


def test_data_loaded():
    """Test that data has been loaded"""
    logger.info("\nTesting data loading...")
    db = DatabaseManager()
    stats = db.get_database_stats()
    
    issues = []
    
    # Check players
    if stats.get('players', 0) == 0:
        logger.warning("  ⚠️  No players loaded")
        issues.append("No players")
    else:
        logger.info(f"  ✅ {stats['players']:,} players loaded")
    
    # Check matches
    if stats.get('matches', 0) == 0:
        logger.warning("  ⚠️  No matches loaded")
        issues.append("No matches")
    else:
        logger.info(f"  ✅ {stats['matches']:,} matches loaded")
    
    # Check tournament tiers
    with db.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM tournament_tiers")
        tier_count = cursor.fetchone()['count']
        if tier_count > 0:
            logger.info(f"  ✅ {tier_count} tournament tiers configured")
        else:
            logger.warning("  ⚠️  No tournament tiers")
            issues.append("No tournament tiers")
    
    return len(issues) == 0, issues


def test_sample_queries():
    """Test some sample queries"""
    logger.info("\nTesting sample queries...")
    db = DatabaseManager()
    
    try:
        # Get top 5 players by match count
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT p.name, COUNT(m.match_id) as match_count
                FROM players p
                LEFT JOIN matches m ON (p.player_id = m.player1_id OR p.player_id = m.player2_id)
                GROUP BY p.player_id, p.name
                ORDER BY match_count DESC
                LIMIT 5
            """)
            results = cursor.fetchall()
            
            if results and results[0]['match_count'] > 0:
                logger.info("  ✅ Top 5 players by match count:")
                for i, row in enumerate(results, 1):
                    logger.info(f"      {i}. {row['name']}: {row['match_count']} matches")
            else:
                logger.warning("  ⚠️  No match data found")
                return False
        
        # Get match count by surface
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT surface, COUNT(*) as count
                FROM matches
                GROUP BY surface
                ORDER BY count DESC
            """)
            results = cursor.fetchall()
            
            if results:
                logger.info("\n  ✅ Matches by surface:")
                for row in results:
                    logger.info(f"      {row['surface']}: {row['count']:,} matches")
            else:
                logger.warning("  ⚠️  No surface data found")
                return False
        
        # Get match count by tournament tier
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT tournament_tier, COUNT(*) as count
                FROM matches
                WHERE tournament_tier IS NOT NULL
                GROUP BY tournament_tier
                ORDER BY count DESC
            """)
            results = cursor.fetchall()
            
            if results:
                logger.info("\n  ✅ Matches by tournament tier:")
                for row in results:
                    logger.info(f"      {row['tournament_tier']}: {row['count']:,} matches")
            else:
                logger.warning("  ⚠️  No tournament tier data found")
                return False
        
        return True
    
    except Exception as e:
        logger.error(f"  ❌ Query failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("=" * 70)
    logger.info("TENNIS CAREER TRACKER - SETUP VERIFICATION")
    logger.info("=" * 70)
    
    results = []
    
    # Test 1: Database Connection
    results.append(("Database Connection", test_database_connection()))
    
    # Test 2: Tables Exist
    results.append(("Tables Exist", test_tables_exist()))
    
    # Test 3: Data Loaded
    data_loaded, issues = test_data_loaded()
    results.append(("Data Loaded", data_loaded))
    
    # Test 4: Sample Queries
    if data_loaded:
        results.append(("Sample Queries", test_sample_queries()))
    else:
        logger.warning("\nSkipping query tests - no data loaded")
        logger.info("Run: python scripts/setup_all.py")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status} - {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Your setup is complete.")
        logger.info("\nNext steps:")
        logger.info("  1. Implement rating calculations (Phase 2)")
        logger.info("  2. Build the API (Phase 3)")
        logger.info("  3. Create the frontend (Phase 4)")
    else:
        logger.info("\n⚠️  Some tests failed. Please check the errors above.")
        if not data_loaded:
            logger.info("\nTo load data, run:")
            logger.info("  python scripts/setup_all.py")
    
    logger.info("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

