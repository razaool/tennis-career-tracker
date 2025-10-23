#!/usr/bin/env python3
"""
Final script to fix the A de Minaur vs Alex de Minaur duplicate
Deletes the empty Alex de Minaur record and renames A de Minaur
"""

import psycopg2

def fix_de_minaur_final():
    """Delete empty Alex de Minaur and rename A de Minaur to Alex de Minaur"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    try:
        # Check current stats
        cur.execute("""
            SELECT p.name, p.player_id, COUNT(pr.rating_id) as rating_count, 
                   MAX(pr.glicko2_rating) as max_glicko2,
                   MAX(pr.elo_rating) as max_elo
            FROM players p
            LEFT JOIN player_ratings pr ON p.player_id = pr.player_id
            WHERE p.name IN ('A de Minaur', 'Alex de Minaur')
            GROUP BY p.name, p.player_id
            ORDER BY p.name
        """)
        
        current_stats = cur.fetchall()
        print("Current stats:")
        for stat in current_stats:
            print(f"  {stat[0]} (ID: {stat[1]}): {stat[2]} ratings, max Glicko-2: {stat[3]}, max ELO: {stat[4]}")
        
        # Find the empty Alex de Minaur record
        cur.execute("""
            SELECT player_id FROM players 
            WHERE name = 'Alex de Minaur' 
            AND player_id NOT IN (
                SELECT DISTINCT player_id FROM player_ratings 
                WHERE player_id IS NOT NULL
            )
        """)
        
        empty_alex_id = cur.fetchone()
        if empty_alex_id:
            empty_alex_id = empty_alex_id[0]
            print(f"Found empty Alex de Minaur record with ID: {empty_alex_id}")
            
            # Delete the empty Alex de Minaur record
            cur.execute("DELETE FROM players WHERE player_id = %s", (empty_alex_id,))
            print(f"Deleted empty Alex de Minaur record")
        else:
            print("No empty Alex de Minaur record found")
        
        # Now rename A de Minaur to Alex de Minaur
        cur.execute("UPDATE players SET name = 'Alex de Minaur' WHERE name = 'A de Minaur'")
        updated_rows = cur.rowcount
        print(f"Renamed {updated_rows} player record from 'A de Minaur' to 'Alex de Minaur'")
        
        conn.commit()
        print("✅ Successfully fixed the de Minaur duplicate")
        
        # Verify the change
        cur.execute("""
            SELECT p.name, COUNT(pr.rating_id) as rating_count, 
                   MAX(pr.glicko2_rating) as max_glicko2,
                   MAX(pr.elo_rating) as max_elo
            FROM players p
            LEFT JOIN player_ratings pr ON p.player_id = pr.player_id
            WHERE p.name LIKE '%de Minaur%'
            GROUP BY p.name, p.player_id
            ORDER BY p.name
        """)
        
        final_stats = cur.fetchall()
        print("Final stats:")
        for stat in final_stats:
            print(f"  {stat[0]}: {stat[1]} ratings, max Glicko-2: {stat[2]}, max ELO: {stat[3]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_de_minaur_final()

