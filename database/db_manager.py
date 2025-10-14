"""
Database connection and management utilities
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging
from pathlib import Path

from config import DB_CONFIG, DATABASE_URL, BASE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.config = DB_CONFIG
        self.engine = create_engine(DATABASE_URL, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_connection(self):
        """Get a raw psycopg2 connection"""
        return psycopg2.connect(**self.config)
    
    @contextmanager
    def get_cursor(self, dict_cursor=True):
        """Context manager for database cursor"""
        conn = self.get_connection()
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    @contextmanager
    def get_session(self):
        """Context manager for SQLAlchemy session"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()
    
    def create_database(self):
        """Create the database if it doesn't exist"""
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            password=self.config['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        try:
            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                (self.config['database'],)
            )
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.config['database']}")
                logger.info(f"Created database: {self.config['database']}")
            else:
                logger.info(f"Database {self.config['database']} already exists")
        
        finally:
            cursor.close()
            conn.close()
    
    def execute_schema(self, schema_file='database/schema.sql'):
        """Execute SQL schema file"""
        schema_path = BASE_DIR / schema_file
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute(schema_sql)
            logger.info("Database schema created successfully")
    
    def reset_database(self):
        """Drop and recreate all tables"""
        logger.warning("Resetting database - all data will be lost!")
        self.execute_schema()
    
    def table_exists(self, table_name):
        """Check if a table exists"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            return cursor.fetchone()['exists']
    
    def get_table_count(self, table_name):
        """Get row count for a table"""
        with self.get_cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            return cursor.fetchone()['count']
    
    def get_player_id(self, player_name):
        """Get or create player ID"""
        with self.get_cursor() as cursor:
            # Try to find existing player
            cursor.execute(
                "SELECT player_id FROM players WHERE name = %s",
                (player_name,)
            )
            result = cursor.fetchone()
            
            if result:
                return result['player_id']
            
            # Create new player
            cursor.execute(
                "INSERT INTO players (name) VALUES (%s) RETURNING player_id",
                (player_name,)
            )
            return cursor.fetchone()['player_id']
    
    def bulk_insert_matches(self, matches_data):
        """Bulk insert match data"""
        if not matches_data:
            return 0
        
        with self.get_cursor(dict_cursor=False) as cursor:
            # Prepare insert query
            insert_query = """
                INSERT INTO matches (
                    tourney_id, match_num, date, tournament_name, tournament_tier,
                    surface, round, best_of, player1_id, player2_id, winner_id,
                    player1_rank, player2_rank, player1_rank_points, player2_rank_points,
                    score, player1_sets_won, player2_sets_won, 
                    player1_games_won, player2_games_won,
                    player1_aces, player2_aces, player1_double_faults, player2_double_faults,
                    player1_first_serve_pct, player2_first_serve_pct
                ) VALUES (
                    %(tourney_id)s, %(match_num)s, %(date)s, %(tournament_name)s, 
                    %(tournament_tier)s, %(surface)s, %(round)s, %(best_of)s,
                    %(player1_id)s, %(player2_id)s, %(winner_id)s,
                    %(player1_rank)s, %(player2_rank)s, 
                    %(player1_rank_points)s, %(player2_rank_points)s,
                    %(score)s, %(player1_sets_won)s, %(player2_sets_won)s,
                    %(player1_games_won)s, %(player2_games_won)s,
                    %(player1_aces)s, %(player2_aces)s, 
                    %(player1_double_faults)s, %(player2_double_faults)s,
                    %(player1_first_serve_pct)s, %(player2_first_serve_pct)s
                )
                ON CONFLICT DO NOTHING
            """
            
            cursor.executemany(insert_query, matches_data)
            inserted_count = cursor.rowcount
            logger.info(f"Inserted {inserted_count} matches")
            return inserted_count
    
    def get_database_stats(self):
        """Get statistics about the database"""
        stats = {}
        tables = ['players', 'matches', 'player_ratings', 'player_career_stats']
        
        for table in tables:
            if self.table_exists(table):
                stats[table] = self.get_table_count(table)
            else:
                stats[table] = 0
        
        return stats


def init_database():
    """Initialize database - create DB and schema"""
    db = DatabaseManager()
    
    logger.info("Initializing database...")
    db.create_database()
    
    # Check if tables exist
    if not db.table_exists('players'):
        logger.info("Creating database schema...")
        db.execute_schema()
    else:
        logger.info("Database schema already exists")
    
    # Print stats
    stats = db.get_database_stats()
    logger.info(f"Database stats: {stats}")
    
    return db


if __name__ == "__main__":
    # Test database setup
    db = init_database()
    print("\n✅ Database initialized successfully!")
    print(f"\nCurrent database stats:")
    for table, count in db.get_database_stats().items():
        print(f"  {table}: {count} rows")

