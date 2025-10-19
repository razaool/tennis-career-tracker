"""
Database connection and utilities
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
from .config import settings


class Database:
    """Database connection manager"""
    
    @staticmethod
    @contextmanager
    def get_connection() -> Generator:
        """
        Context manager for database connections
        
        Usage:
            with Database.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM players")
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD if settings.DB_PASSWORD else None,
                cursor_factory=RealDictCursor  # Return dict instead of tuples
            )
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def execute_query(query: str, params: tuple = None) -> list:
        """
        Execute a query and return results as list of dicts
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of dictionaries (one per row)
        """
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
    
    @staticmethod
    def execute_one(query: str, params: tuple = None) -> dict:
        """
        Execute a query and return single result
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Dictionary or None
        """
        with Database.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()
    
    @staticmethod
    def test_connection() -> bool:
        """Test database connection"""
        try:
            with Database.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False


# Dependency for FastAPI routes
def get_db():
    """Dependency to get database connection in FastAPI routes"""
    with Database.get_connection() as conn:
        yield conn

