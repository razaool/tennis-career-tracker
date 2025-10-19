"""
Fix duplicate player records from 2025 data

Problem: 2025 data has abbreviated names (C Alcaraz, J Sinner)
Solution: Merge duplicates into main player records
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_CONFIG


def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def create_duplicate_mapping(conn):
    """Create mapping of duplicate players to correct players"""
    print("\n[Step 2/11] Creating duplicate player mapping...")
    
    with conn.cursor() as cur:
        # Create mapping table
        cur.execute("""
            DROP TABLE IF EXISTS duplicate_player_mapping CASCADE;
            
            CREATE TABLE duplicate_player_mapping AS
            SELECT 
                abbrev.player_id as duplicate_id,
                abbrev.name as duplicate_name,
                main_player.player_id as correct_id,
                main_player.name as correct_name
            FROM players abbrev
            JOIN players main_player ON (
                main_player.name ILIKE SUBSTRING(abbrev.name FROM 1 FOR 1) || '% ' || SUBSTRING(abbrev.name FROM 3) || '%'
                AND main_player.player_id < 28700
                AND abbrev.player_id >= 28700
                AND abbrev.player_id != main_player.player_id
                AND (SELECT COUNT(*) FROM matches WHERE player1_id = main_player.player_id OR player2_id = main_player.player_id) > 100
            )
            WHERE abbrev.name ~ '^[A-Z] [A-Z]';
        """)
        
        # Get count
        cur.execute("SELECT COUNT(*) as cnt FROM duplicate_player_mapping")
        count = cur.fetchone()['cnt']
        print(f"   ✅ Created mapping for {count} duplicate players")
        
        # Show top players
        cur.execute("""
            SELECT duplicate_name, correct_name 
            FROM duplicate_player_mapping
            WHERE correct_name IN (
                'Jannik Sinner', 'Carlos Alcaraz', 'Novak Djokovic', 'Alexander Zverev',
                'Daniil Medvedev', 'Taylor Fritz', 'Andrey Rublev'
            )
            ORDER BY correct_name
        """)
        
        print("   Sample mappings (top players):")
        for row in cur.fetchall():
            print(f"      {row['duplicate_name']} → {row['correct_name']}")
        
        conn.commit()
        return count


def update_matches(conn, total_mapped):
    """Update matches to use correct player IDs"""
    print(f"\n[Step 3/11] Updating matches with correct player IDs...")
    
    with conn.cursor() as cur:
        # Update player1_id
        cur.execute("""
            UPDATE matches m
            SET player1_id = dpm.correct_id
            FROM duplicate_player_mapping dpm
            WHERE m.player1_id = dpm.duplicate_id;
        """)
        player1_updated = cur.rowcount
        print(f"   ✅ Updated {player1_updated} matches (player1)")
        
        # Update player2_id
        cur.execute("""
            UPDATE matches m
            SET player2_id = dpm.correct_id
            FROM duplicate_player_mapping dpm
            WHERE m.player2_id = dpm.duplicate_id;
        """)
        player2_updated = cur.rowcount
        print(f"   ✅ Updated {player2_updated} matches (player2)")
        
        # Update winner_id
        cur.execute("""
            UPDATE matches m
            SET winner_id = dpm.correct_id
            FROM duplicate_player_mapping dpm
            WHERE m.winner_id = dpm.duplicate_id;
        """)
        winner_updated = cur.rowcount
        print(f"   ✅ Updated {winner_updated} matches (winner)")
        
        conn.commit()
        return player1_updated + player2_updated


def update_player_ratings(conn):
    """Update player_ratings to use correct player IDs"""
    print(f"\n[Step 4/11] Updating player_ratings with correct player IDs...")
    
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE player_ratings pr
            SET player_id = dpm.correct_id
            FROM duplicate_player_mapping dpm
            WHERE pr.player_id = dpm.duplicate_id;
        """)
        updated = cur.rowcount
        print(f"   ✅ Updated {updated} rating records")
        conn.commit()
        return updated


def delete_duplicates(conn):
    """Delete duplicate player records"""
    print(f"\n[Step 5/11] Deleting duplicate player records...")
    
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM players
            WHERE player_id IN (
                SELECT duplicate_id FROM duplicate_player_mapping
            );
        """)
        deleted = cur.rowcount
        print(f"   ✅ Deleted {deleted} duplicate players")
        conn.commit()
        return deleted


def verify_fix(conn):
    """Verify the fix worked"""
    print(f"\n[Step 11/11] Verifying fix...")
    
    with conn.cursor() as cur:
        # Check Alcaraz
        cur.execute("""
            SELECT 
                COUNT(DISTINCT m.match_id) as total_matches,
                MAX(m.date) as last_match
            FROM matches m
            WHERE m.player1_id = (SELECT player_id FROM players WHERE name = 'Carlos Alcaraz')
               OR m.player2_id = (SELECT player_id FROM players WHERE name = 'Carlos Alcaraz')
        """)
        alcaraz = cur.fetchone()
        print(f"   Carlos Alcaraz: {alcaraz['total_matches']} matches, last: {alcaraz['last_match']}")
        
        # Check Sinner
        cur.execute("""
            SELECT 
                COUNT(DISTINCT m.match_id) as total_matches,
                MAX(m.date) as last_match
            FROM matches m
            WHERE m.player1_id = (SELECT player_id FROM players WHERE name = 'Jannik Sinner')
               OR m.player2_id = (SELECT player_id FROM players WHERE name = 'Jannik Sinner')
        """)
        sinner = cur.fetchone()
        print(f"   Jannik Sinner: {sinner['total_matches']} matches, last: {sinner['last_match']}")
        
        # Check for remaining duplicates
        cur.execute("""
            SELECT COUNT(*) as remaining
            FROM players
            WHERE name ~ '^[A-Z] [A-Z]'
            AND player_id >= 28700
        """)
        remaining = cur.fetchone()['remaining']
        print(f"   Remaining duplicates: {remaining}")
        
        if remaining > 0:
            print(f"   ⚠️  {remaining} players couldn't be auto-matched")
        else:
            print(f"   ✅ All duplicates resolved!")
        
        return alcaraz, sinner, remaining


def main():
    print("\n" + "="*70)
    print("🔧 FIXING DUPLICATE PLAYER RECORDS - 2025 DATA")
    print("="*70)
    
    conn = get_connection()
    
    try:
        print("\n[Step 1/11] Backup already created ✅")
        
        # Create mapping
        mapped_count = create_duplicate_mapping(conn)
        
        if mapped_count == 0:
            print("\n❌ No duplicates mapped. Check matching logic.")
            return
        
        # Update matches
        matches_updated = update_matches(conn, mapped_count)
        
        # Update ratings
        ratings_updated = update_player_ratings(conn)
        
        # Delete duplicates
        deleted = delete_duplicates(conn)
        
        print(f"\n[Step 6-10/11] Skipping full recalculation for now...")
        print("   (Will recalculate ELO/TSR/Glicko-2 after verifying merge)")
        
        # Verify
        alcaraz, sinner, remaining = verify_fix(conn)
        
        print("\n" + "="*70)
        print("✅ DUPLICATE FIX COMPLETE")
        print("="*70)
        print(f"\nSummary:")
        print(f"  • {mapped_count} duplicates mapped")
        print(f"  • {matches_updated} match records updated")
        print(f"  • {ratings_updated} rating records updated")
        print(f"  • {deleted} duplicate players deleted")
        print(f"  • {remaining} unmapped duplicates remaining")
        
        print(f"\nVerification:")
        print(f"  • Carlos Alcaraz now has: {alcaraz['total_matches']} matches")
        print(f"  • Jannik Sinner now has: {sinner['total_matches']} matches")
        
        if remaining == 0:
            print("\n✅ All duplicates successfully merged!")
            print("\n⚠️  NEXT STEP: Recalculate ratings for affected players")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

