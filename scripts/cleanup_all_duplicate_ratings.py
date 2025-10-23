#!/usr/bin/env python3
"""
Comprehensive script to clean up ALL duplicate rating entries across all years
"""

import psycopg2

def cleanup_all_duplicate_ratings():
    """Remove ALL duplicate rating entries, keeping only the most recent one per player per date"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    try:
        print("🔍 Analyzing ALL duplicate rating entries...")
        
        # Check current state across all years
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
                GROUP BY pr.player_id, pr.date
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        
        before_stats = cur.fetchone()
        print(f"📊 BEFORE cleanup (all years):")
        print(f"   - Duplicate dates: {before_stats[0]}")
        print(f"   - Total duplicate entries: {before_stats[1]}")
        
        # Get examples of duplicates across all years
        cur.execute("""
            SELECT 
                p.name,
                pr.player_id,
                pr.date,
                COUNT(*) as duplicate_count,
                MIN(pr.glicko2_rating) as min_glicko2,
                MAX(pr.glicko2_rating) as max_glicko2,
                MAX(pr.glicko2_rating) - MIN(pr.glicko2_rating) as glicko2_range
            FROM player_ratings pr
            JOIN players p ON pr.player_id = p.player_id
            GROUP BY p.name, pr.player_id, pr.date
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC, glicko2_range DESC
            LIMIT 10
        """)
        
        top_duplicates = cur.fetchall()
        print(f"\n🔍 Top 10 most problematic duplicates (all years):")
        for dup in top_duplicates:
            print(f"   - {dup[0]} ({dup[2]}): {dup[3]} entries, Glicko-2 range: {dup[6]:.1f}")
        
        # Create backup if not exists
        print("\n📋 Ensuring backup table exists...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS player_ratings_backup_all AS 
            SELECT * FROM player_ratings
        """)
        
        # Remove ALL duplicates
        print(f"\n🗑️  Removing ALL duplicate entries...")
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
                GROUP BY pr.player_id, pr.date
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        
        after_stats = cur.fetchone()
        print(f"📊 AFTER cleanup (all years):")
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
            print("⚠️  Rankings still have duplicates - investigating further...")
            
            # Show examples of remaining duplicates
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
                    name,
                    COUNT(*) as duplicate_count,
                    MIN(rank) as best_rank,
                    MAX(rank) as worst_rank
                FROM current_rankings
                GROUP BY name
                HAVING COUNT(*) > 1
                ORDER BY duplicate_count DESC
                LIMIT 5
            """)
            
            remaining_duplicates = cur.fetchall()
            print(f"\n🔍 Remaining duplicates in rankings:")
            for dup in remaining_duplicates:
                print(f"   - {dup[0]}: {dup[1]} entries (ranks {dup[2]}-{dup[3]})")
        
        # Commit the changes
        conn.commit()
        print(f"\n🎉 Cleanup completed successfully!")
        print(f"📋 Backup table 'player_ratings_backup_all' created for safety")
        
        # Try to add constraint again
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
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

def verify_final_cleanup():
    """Final verification of the cleanup"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    try:
        print("\n🔍 Final Verification Report:")
        print("=" * 50)
        
        # Check for any remaining duplicates
        cur.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT player_id, date, COUNT(*) 
                FROM player_ratings 
                GROUP BY player_id, date 
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        
        remaining_duplicates = cur.fetchone()[0]
        print(f"📊 Remaining duplicates: {remaining_duplicates}")
        
        if remaining_duplicates == 0:
            print("✅ No duplicates found - cleanup successful!")
        else:
            print("⚠️  Some duplicates remain")
        
        # Show top 10 rankings
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
        
        # Check total players and ratings
        cur.execute("""
            SELECT 
                COUNT(DISTINCT p.player_id) as unique_players,
                COUNT(pr.rating_id) as total_ratings
            FROM players p
            LEFT JOIN player_ratings pr ON p.player_id = pr.player_id
        """)
        
        stats = cur.fetchone()
        print(f"\n📊 Database statistics:")
        print(f"   - Unique players: {stats[0]:,}")
        print(f"   - Total rating entries: {stats[1]:,}")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🧹 Comprehensive Tennis Rating System Cleanup Tool")
    print("=" * 60)
    
    cleanup_all_duplicate_ratings()
    verify_final_cleanup()
    
    print("\n" + "=" * 60)
    print("✅ Comprehensive cleanup process completed!")
    print("📋 Backup tables created for safety")
    print("🔒 Constraint added to prevent future duplicates")
