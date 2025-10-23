#!/usr/bin/env python3
"""
Script to fix the A de Minaur vs Alex de Minaur duplicate
Handles the winner constraint properly by updating in the right order
"""

import psycopg2

def fix_de_minaur_duplicate_constraint_fix():
    """Merge A de Minaur into Alex de Minaur, handling constraints properly"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    try:
        # Get player IDs
        cur.execute("SELECT player_id FROM players WHERE name = 'A de Minaur'")
        a_de_minaur_id = cur.fetchone()[0]
        
        cur.execute("SELECT player_id FROM players WHERE name = 'Alex de Minaur'")
        alex_de_minaur_id = cur.fetchone()[0]
        
        print(f"A de Minaur ID: {a_de_minaur_id}")
        print(f"Alex de Minaur ID: {alex_de_minaur_id}")
        
        # Check current stats
        cur.execute("""
            SELECT COUNT(*) as rating_count, 
                   MAX(glicko2_rating) as max_glicko2,
                   MAX(elo_rating) as max_elo
            FROM player_ratings 
            WHERE player_id = %s
        """, (a_de_minaur_id,))
        
        a_de_minaur_stats = cur.fetchone()
        print(f"A de Minaur stats: {a_de_minaur_stats[0]} ratings, max Glicko-2: {a_de_minaur_stats[1]}, max ELO: {a_de_minaur_stats[2]}")
        
        # Update winner_id FIRST to avoid constraint violations
        cur.execute("""
            UPDATE matches 
            SET winner_id = %s 
            WHERE winner_id = %s
        """, (alex_de_minaur_id, a_de_minaur_id))
        winner_updated = cur.rowcount
        print(f"Updated {winner_updated} matches (winner_id)")
        
        # Now update player1_id
        cur.execute("""
            UPDATE matches 
            SET player1_id = %s 
            WHERE player1_id = %s
        """, (alex_de_minaur_id, a_de_minaur_id))
        matches1_updated = cur.rowcount
        print(f"Updated {matches1_updated} matches (player1_id)")
        
        # Now update player2_id
        cur.execute("""
            UPDATE matches 
            SET player2_id = %s 
            WHERE player2_id = %s
        """, (alex_de_minaur_id, a_de_minaur_id))
        matches2_updated = cur.rowcount
        print(f"Updated {matches2_updated} matches (player2_id)")
        
        # Update player_ratings table
        cur.execute("""
            UPDATE player_ratings 
            SET player_id = %s 
            WHERE player_id = %s
        """, (alex_de_minaur_id, a_de_minaur_id))
        ratings_updated = cur.rowcount
        print(f"Updated {ratings_updated} player ratings")
        
        # Check for any remaining references
        cur.execute("""
            SELECT table_name, column_name 
            FROM information_schema.key_column_usage 
            WHERE referenced_table_name = 'players' 
            AND referenced_column_name = 'player_id'
            AND table_name NOT IN ('matches', 'player_ratings')
        """)
        
        other_refs = cur.fetchall()
        for table_name, column_name in other_refs:
            cur.execute(f"""
                UPDATE {table_name} 
                SET {column_name} = %s 
                WHERE {column_name} = %s
            """, (alex_de_minaur_id, a_de_minaur_id))
            updated_count = cur.rowcount
            if updated_count > 0:
                print(f"Updated {updated_count} records in {table_name}.{column_name}")
        
        # Verify no matches still reference the old player
        cur.execute("""
            SELECT COUNT(*) FROM matches 
            WHERE player1_id = %s OR player2_id = %s OR winner_id = %s
        """, (a_de_minaur_id, a_de_minaur_id, a_de_minaur_id))
        
        remaining_refs = cur.fetchone()[0]
        if remaining_refs > 0:
            print(f"⚠️  Warning: {remaining_refs} matches still reference A de Minaur")
            return
        
        # Now we can safely delete the duplicate player record
        cur.execute("DELETE FROM players WHERE player_id = %s", (a_de_minaur_id,))
        print(f"Deleted duplicate player record")
        
        conn.commit()
        print("✅ Successfully merged A de Minaur into Alex de Minaur")
        
        # Verify the merge
        cur.execute("""
            SELECT COUNT(*) as rating_count, 
                   MAX(glicko2_rating) as max_glicko2,
                   MAX(elo_rating) as max_elo
            FROM player_ratings 
            WHERE player_id = %s
        """, (alex_de_minaur_id,))
        
        final_stats = cur.fetchone()
        print(f"Final Alex de Minaur stats: {final_stats[0]} ratings, max Glicko-2: {final_stats[1]}, max ELO: {final_stats[2]}")
        
        # Check if A de Minaur still exists
        cur.execute("SELECT COUNT(*) FROM players WHERE name = 'A de Minaur'")
        plan_a_count = cur.fetchone()[0]
        print(f"A de Minaur records remaining: {plan_a_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_de_minaur_duplicate_constraint_fix()

