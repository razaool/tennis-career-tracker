#!/usr/bin/env python3
"""
Script to resolve duplicate player names with abbreviations
"""

import psycopg2
from difflib import SequenceMatcher
import re

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_surname(name):
    """Extract surname from full name"""
    parts = name.split()
    if len(parts) >= 2:
        return ' '.join(parts[1:])  # Everything after first name
    return name

def find_potential_duplicates():
    """Find potential duplicate players"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    # Get all players
    cur.execute("SELECT player_id, name FROM players ORDER BY name")
    players = cur.fetchall()
    
    potential_duplicates = []
    
    for i, (id1, name1) in enumerate(players):
        for j, (id2, name2) in enumerate(players[i+1:], i+1):
            # Skip if same player
            if id1 == id2:
                continue
                
            # Check for abbreviated patterns
            if is_abbreviated_match(name1, name2):
                surname1 = extract_surname(name1)
                surname2 = extract_surname(name2)
                
                # If surnames match, likely the same person
                if surname1 == surname2:
                    potential_duplicates.append({
                        'player1_id': id1,
                        'player1_name': name1,
                        'player2_id': id2,
                        'player2_name': name2,
                        'similarity': similarity(name1, name2)
                    })
    
    conn.close()
    return potential_duplicates

def is_abbreviated_match(name1, name2):
    """Check if one name is an abbreviation of another"""
    # Pattern: Single letter + space + surname
    abbreviated_pattern = r'^[A-Z]\s'
    
    name1_abbrev = bool(re.match(abbreviated_pattern, name1))
    name2_abbrev = bool(re.match(abbreviated_pattern, name2))
    
    # One should be abbreviated, one should be full
    return name1_abbrev != name2_abbrev

def merge_players(player1_id, player2_id, keep_name):
    """Merge two players, keeping the specified name"""
    conn = psycopg2.connect(
        host="localhost",
        database="tennis_tracker",
        user="postgres",
        password="postgres"
    )
    
    cur = conn.cursor()
    
    try:
        # Update all ratings to use the kept player ID
        cur.execute("""
            UPDATE player_ratings 
            SET player_id = %s 
            WHERE player_id = %s
        """, (player1_id, player2_id))
        
        # Update the kept player's name
        cur.execute("""
            UPDATE players 
            SET name = %s 
            WHERE player_id = %s
        """, (keep_name, player1_id))
        
        # Delete the duplicate player
        cur.execute("DELETE FROM players WHERE player_id = %s", (player2_id,))
        
        conn.commit()
        print(f"Successfully merged players, kept: {keep_name}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error merging players: {e}")
    
    finally:
        conn.close()

def main():
    print("Finding potential duplicate players...")
    duplicates = find_potential_duplicates()
    
    print(f"Found {len(duplicates)} potential duplicates:")
    for dup in duplicates:
        print(f"- {dup['player1_name']} (ID: {dup['player1_id']})")
        print(f"  {dup['player2_name']} (ID: {dup['player2_id']})")
        print(f"  Similarity: {dup['similarity']:.2f}")
        print()
    
    # For now, just show the results
    # In production, you'd want manual review before merging

if __name__ == "__main__":
    main()

