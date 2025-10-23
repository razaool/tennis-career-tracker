#!/usr/bin/env python3
"""
Simple script to just rename A de Minaur to Alex de Minaur
"""

import psycopg2

def simple_name_fix():
    """Simply rename A de Minaur to Alex de Minaur"""
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
            SELECT p.name, COUNT(pr.rating_id) as rating_count, 
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
            print(f"  {stat[0]}: {stat[1]} ratings, max Glicko-2: {stat[2]}, max ELO: {stat[3]}")
        
        # Simply rename A de Minaur to Alex de Minaur
        cur.execute("UPDATE players SET name = 'Alex de Minaur' WHERE name = 'A de Minaur'")
        updated_rows = cur.rowcount
        print(f"Updated {updated_rows} player record")
        
        conn.commit()
        print("✅ Successfully renamed A de Minaur to Alex de Minaur")
        
        # Verify the change
        cur.execute("""
            SELECT name, COUNT(*) as count
            FROM players 
            WHERE name LIKE '%de Minaur%'
            GROUP BY name
        """)
        
        final_stats = cur.fetchall()
        print("Final stats:")
        for stat in final_stats:
            print(f"  {stat[0]}: {stat[1]} records")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    simple_name_fix()

