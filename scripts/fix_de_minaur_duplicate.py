#!/usr/bin/env python3
"""
Script to fix the specific A de Minaur vs Alex de Minaur duplicate
"""

import psycopg2

def fix_de_minaur_duplicate():
    """Merge A de Minaur into Alex de Minaur"""
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
        
        # Check current ratings
        cur.execute("""
            SELECT COUNT(*) as rating_count, 
                   MAX(glicko2_rating) as max_glicko2,
                   MAX(elo_rating) as max_elo
            FROM player_ratings 
            WHERE player_id = %s
        """, (a_de_minaur_id,))
        
        a_de_minaur_stats = cur.fetchone()
        print(f"A de Minaur stats: {a_de_minaur_stats[0]} ratings, max Glicko-2: {a_de_minaur_stats[1]}, max ELO: {a_de_minaur_stats[2]}")
        
        cur.execute("""
            SELECT COUNT(*) as rating_count, 
                   MAX(glicko2_rating) as max_glicko2,
                   MAX(elo_rating) as max_elo
            FROM player_ratings 
            WHERE player_id = %s
        """, (alex_de_minaur_id,))
        
        alex_de_minaur_stats = cur.fetchone()
        print(f"Alex de Minaur stats: {alex_de_minaur_stats[0]} ratings, max Glicko-2: {alex_de_minaur_stats[1]}, max ELO: {alex_de_minaur_stats[2]}")
        
        # Update all ratings from A de Minaur to Alex de Minaur
        cur.execute("""
            UPDATE player_ratings 
            SET player_id = %s 
            WHERE player_id = %s
        """, (alex_de_minaur_id, a_de_minaur_id))
        
        updated_rows = cur.rowcount
        print(f"Updated {updated_rows} rating records")
        
        # Delete the duplicate player record
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
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_de_minaur_duplicate()

