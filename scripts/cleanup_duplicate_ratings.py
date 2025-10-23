#!/usr/bin/env python3
"""
Script to clean up duplicate rating entries for the same player on the same date
This is critical for fixing ranking system accuracy
"""

import psycopg2
from datetime import datetime

def cleanup_duplicate_ratings():
    """Remove duplicate rating entries, keeping only the most recent one per player per date"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    try:
        print("🔍 Analyzing duplicate rating entries...")
        
        # First, let's see the current state
        cur.execute("""
            SELECT 
                COUNT(*) as total_duplicate_dates,
                SUM(duplicate_count) as total_duplicate_entries
            FROM (
                SELECT 
                    pr.player_id,
                    pr.date,
                    COUNT(*) as duplicate_count
                FROM player_ratings pr
                WHERE pr.date >= '2025-01-01'
                GROUP BY pr.player_id, pr.date
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        
        before_stats = cur.fetchone()
        print(f"📊 BEFORE cleanup:")
        print(f"   - Duplicate dates: {before_stats[0]}")
        print(f"   - Total duplicate entries: {before_stats[1]}")
        
        # Get detailed info about duplicates
        cur.execute("""
            SELECT 
                p.name,
                pr.player_id,
                pr.date,
                COUNT(*) as duplicate_count,
                MIN(pr.glicko2_rating) as min_glicko2,
                MAX(pr.glicko2_rating) as max_glicko2,
                MAX(pr.glicko2_rating) - MIN(pr.glicko2_rating) as glicko2_range,
                MIN(pr.elo_rating) as min_elo,
                MAX(pr.elo_rating) as max_elo,
                MAX(pr.elo_rating) - MIN(pr.elo_rating) as elo_range
            FROM player_ratings pr
            JOIN players p ON pr.player_id = p.player_id
            WHERE pr.date >= '2025-01-01'
            GROUP BY p.name, pr.player_id, pr.date
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC, glicko2_range DESC
            LIMIT 10
        """)
        
        top_duplicates = cur.fetchall()
        print(f"\n🔍 Top 10 most problematic duplicates:")
        for dup in top_duplicates:
            print(f"   - {dup[0]} ({dup[2]}): {dup[3]} entries, Glicko-2 range: {dup[6]:.1f}, ELO range: {dup[8]:.1f}")
        
        print(f"\n🧹 Starting cleanup process...")
        
        # Create a backup table first
        print("📋 Creating backup table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS player_ratings_backup AS 
            SELECT * FROM player_ratings
        """)
        
        # Identify duplicates to remove
        print("🔍 Identifying duplicates to remove...")
        cur.execute("""
            WITH duplicate_ratings AS (
                SELECT 
                    rating_id,
                    player_id,
                    date,
                    ROW_NUMBER() OVER (
                        PARTITION BY player_id, date 
                        ORDER BY rating_id DESC
                    ) most_recent
                FROM player_ratings
                WHERE date >= '2025-01-01'
            )
            SELECT rating_id 
            FROM duplicate_ratings 
            WHERE most_recent > 1
        """)
        
        duplicate_ids = cur.fetchall()
        duplicate_count = len(duplicate_ids)
        print(f"📊 Found {duplicate_count} duplicate entries to remove")
        
        if duplicate_count == 0:
            print("✅ No duplicates found - system is clean!")
            return
        
        # Show some examples of what will be removed
        cur.execute("""
            WITH duplicate_ratings AS (
                SELECT 
                    rating_id,
                    player_id,
                    date,
                    ROW_NUMBER() OVER (
                        PARTITION BY player_id, date 
                        ORDER BY rating_id DESC
                    ) most_recent
                FROM player_ratings
                WHERE date >= '2025-01-01'
            ),
            to_remove AS (
                SELECT rating_id 
                FROM duplicate_ratings 
                WHERE most_recent > 1
            )
            SELECT 
                p.name,
                pr.date,
                pr.glicko2_rating,
                pr.elo_rating,
                tr.rating_id
            FROM to_remove tr
            JOIN player_ratings pr ON tr.rating_id = pr.rating_id
            JOIN players p ON pr.player_id = p.player_id
            ORDER BY p.name, pr.date
            LIMIT 10
        """)
        
        examples = cur.fetchall()
        print(f"\n📝 Examples of entries to be removed:")
        for ex in examples:
            print(f"   - {ex[0]} ({ex[1]}): Glicko-2: {ex[2]:.1f}, ELO: {ex[3]:.1f}")
        
        # Remove duplicates
        print(f"\n🗑️  Removing {duplicate_count} duplicate entries...")
        cur.execute("""
            WITH duplicate_ratings AS (
                SELECT 
                    rating_id,
                    player_id,
                    date,
                    ROW_NUMBER() OVER (
                        PARTITION BY player_id, date 
                        ORDER BY rating_id DESC
                    ) most_recent
                FROM player_ratings
                WHERE date >= '2025-01-01'
            )
            DELETE FROM player_ratings 
            WHERE rating_id IN (
                SELECT rating_id 
                FROM duplicate_ratings 
                WHERE most_recent > 1
            )
        """)
        
        deleted_count = cur.rowcount
        print(f"✅ Removed {deleted_count} duplicate entries")
        
        # Verify the cleanup
        print(f"\n🔍 Verifying cleanup...")
        cur.execute("""
            SELECT 
                COUNT(*) as total_duplicate_dates,
                SUM(duplicate_count) as total_duplicate_entries
            FROM (
                SELECT 
                    pr.player_id,
                    pr.date,
                    COUNT(*) as duplicate_count
                FROM player_ratings pr
                WHERE pr.date >= '2025-01-01'
                GROUP BY pr.player_id, pr.date
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        
        after_stats = cur.fetchone()
        print(f"📊 AFTER cleanup:")
        print(f"   - Duplicate dates: {after_stats[0]}")
        print(f"   - Total duplicate entries: {after_stats[1]}")
        
        # Show improvement
        if before_stats[0] > 0:
            improvement = ((before_stats[0] - after_stats[0]) / before_stats[0]) * 100
            print(f"🎉 Improvement: {improvement:.1f}% reduction in duplicate dates")
        
        # Check current rankings integrity
        print(f"\n🏆 Checking rankings integrity...")
        cur.execute("""
            WITH current_rankings AS (
                SELECT 
                    p.name,
                    pr.player_id,
                    pr.glicko2_rating,
                    ROW_NUMBER() OVER (ORDER BY pr.glicko2_rating DESC) as rank
                FROM player_ratings pr
                JOIN players p ON pr.player_id = p.player_id
                WHERE pr.date = (
                    SELECT MAX(date) 
                    FROM player_ratings pr2 
                    WHERE pr2.player_id = pr.player_id
                )
                AND pr.glicko2_rating IS NOT NULL
            )
            SELECT 
                COUNT(*) as total_players,
                COUNT(DISTINCT player_id) as unique_players,
                COUNT(*) - COUNT(DISTINCT player_id) as duplicates_in_rankings
            FROM current_rankings
        """)
        
        ranking_stats = cur.fetchone()
        print(f"📊 Rankings integrity:")
        print(f"   - Total ranking entries: {ranking_stats[0]}")
        print(f"   - Unique players: {ranking_stats[1]}")
        print(f"   - Duplicates in rankings: {ranking_stats[2]}")
        
        if ranking_stats[2] == 0:
            print("✅ Rankings are now clean - each player appears only once!")
        else:
            print("⚠️  Rankings still have duplicates - further investigation needed")
        
        # Commit the changes
        conn.commit()
        print(f"\n🎉 Cleanup completed successfully!")
        print(f"📋 Backup table 'player_ratings_backup' created for safety")
        
        # Add constraint to prevent future duplicates
        print(f"\n🔒 Adding constraint to prevent future duplicates...")
        try:
            cur.execute("""
                ALTER TABLE player_ratings 
                ADD CONSTRAINT unique_player_date_rating 
                UNIQUE (player_id, date)
            """)
            conn.commit()
            print("✅ Constraint added successfully")
        except Exception as e:
            print(f"⚠️  Could not add constraint: {e}")
            print("   (This might already exist or there might be other constraints)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

def verify_cleanup():
    """Verify that the cleanup was successful"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    try:
        print("\n🔍 Verification Report:")
        
        # Check for remaining duplicates
        cur.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT player_id, date, COUNT(*) 
                FROM player_ratings 
                WHERE date >= '2025-01-01'
                GROUP BY player_id, date 
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        
        remaining_duplicates = cur.fetchone()[0]
        print(f"📊 Remaining duplicates: {remaining_duplicates}")
        
        if remaining_duplicates == 0:
            print("✅ No duplicates found - cleanup successful!")
        else:
            print("⚠️  Some duplicates remain - may need manual review")
        
        # Check top 10 rankings
        cur.execute("""
            SELECT 
                p.name,
                pr.glicko2_rating,
                ROW_NUMBER() OVER (ORDER BY pr.glicko2_rating DESC) as rank
            FROM player_ratings pr
            JOIN players p ON pr.player_id = p.player_id
            WHERE pr.date = (
                SELECT MAX(date) 
                FROM player_ratings pr2 
                WHERE pr2.player_id = pr.player_id
            )
            AND pr.glicko2_rating IS NOT NULL
            ORDER BY pr.glicko2_rating DESC
            LIMIT 10
        """)
        
        top_10 = cur.fetchall()
        print(f"\n🏆 Top 10 rankings after cleanup:")
        for i, (name, rating, rank) in enumerate(top_10, 1):
            print(f"   {i:2d}. {name}: {rating:.1f}")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🧹 Tennis Rating System Cleanup Tool")
    print("=" * 50)
    
    cleanup_duplicate_ratings()
    verify_cleanup()
    
    print("\n" + "=" * 50)
    print("✅ Cleanup process completed!")
    print("📋 Check the backup table 'player_ratings_backup' if needed")
    print("🔒 Constraint added to prevent future duplicates")
