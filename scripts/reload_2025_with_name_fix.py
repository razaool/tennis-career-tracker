"""
Reload 2025 data with normalized player names

Reads 2025 CSVs, normalizes abbreviated names to full names, reloads to database
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DB_CONFIG

# Define tournament files to reload
TOURNAMENT_FILES = [
    'data/raw/masters_1000/miami_2025_parsed.csv',
    'data/raw/masters_1000/monte_carlo_2025_parsed.csv',
    'data/raw/masters_1000/rome_2025_parsed.csv',
    'data/raw/masters_1000/cincinnati_2025_parsed.csv',
    'data/raw/masters_1000/shanghai_2025_parsed.csv',
]


def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def get_player_name_mapping(conn):
    """Get mapping of abbreviated to full names from database"""
    print("\n📋 Loading player name mapping from database...")
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT player_id, name
            FROM players
            WHERE player_id < 28700  -- Only original players
            ORDER BY name
        """)
        players = cur.fetchall()
    
    # Create mapping: abbreviated → full name
    mapping = {}
    for p in players:
        name = p['name']
        # Create abbreviated version (First letter + last name)
        parts = name.split()
        if len(parts) >= 2:
            abbrev = parts[0][0] + ' ' + ' '.join(parts[1:])
            mapping[abbrev] = name
            
            # Also try with just last name
            abbrev_short = parts[0][0] + ' ' + parts[-1]
            if abbrev_short not in mapping:
                mapping[abbrev_short] = name
    
    print(f"   ✅ Created mapping for {len(mapping)} name variations")
    return mapping, {p['name']: p['player_id'] for p in players}


def normalize_name(abbrev_name, mapping):
    """Normalize abbreviated name to full name"""
    if abbrev_name in mapping:
        return mapping[abbrev_name]
    return abbrev_name  # Return as-is if no mapping found


def process_and_load_tournament(file_path, name_mapping, player_ids, conn):
    """Process a tournament CSV and load to database"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"   ⚠️  File not found: {file_path}")
        return 0
    
    print(f"\n📂 Processing: {file_path.name}")
    
    # Read CSV
    df = pd.read_csv(file_path)
    total_matches = len(df)
    print(f"   📊 {total_matches} matches to load")
    
    # Track progress
    loaded = 0
    skipped = 0
    
    with conn.cursor() as cur:
        for idx, row in df.iterrows():
            # Normalize player names (CSV has winner_name and loser_name)
            winner_abbrev = row['winner_name']
            loser_abbrev = row['loser_name']
            winner_full = normalize_name(winner_abbrev, name_mapping)
            loser_full = normalize_name(loser_abbrev, name_mapping)
            
            # Get player IDs
            winner_id = player_ids.get(winner_full)
            loser_id = player_ids.get(loser_full)
            
            if not winner_id or not loser_id:
                skipped += 1
                if skipped <= 3:  # Only show first few
                    print(f"   ⚠️  Skipped: {winner_abbrev} vs {loser_abbrev} (player not found)")
                continue
            
            # Assign player1/player2 (winner is player1 for simplicity)
            player1_id = winner_id
            player2_id = loser_id
            
            # Insert match
            try:
                # Determine surface from tournament name
                tournament = row['tournament_name']
                if 'Monte Carlo' in tournament or 'Rome' in tournament or 'Madrid' in tournament:
                    surface = 'clay'
                else:
                    surface = 'hard'
                
                cur.execute("""
                    INSERT INTO matches (
                        date, tournament_name, tournament_tier, surface, round,
                        best_of, player1_id, player2_id, winner_id, score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    row['date'],
                    tournament,
                    'Masters 1000',  # All these are Masters
                    surface,
                    row['round'],
                    3,  # Best of 3
                    player1_id,
                    player2_id,
                    winner_id,
                    row['score']
                ))
                loaded += 1
                
                # Show progress every 50 matches
                if (idx + 1) % 50 == 0:
                    print(f"   ⏳ Progress: {idx + 1}/{total_matches} matches ({loaded} loaded, {skipped} skipped)")
                
            except Exception as e:
                skipped += 1
                if skipped <= 3:
                    print(f"   ⚠️  Error loading match: {e}")
        
        conn.commit()
    
    print(f"   ✅ {loaded} matches loaded, {skipped} skipped")
    return loaded


def main():
    print("\n" + "="*70)
    print("🔄 [2/5] RELOADING 2025 DATA WITH NORMALIZED NAMES")
    print("="*70)
    
    conn = get_connection()
    
    try:
        # Get name mappings
        name_mapping, player_ids = get_player_name_mapping(conn)
        
        # Process each tournament
        total_loaded = 0
        for file_path in TOURNAMENT_FILES:
            loaded = process_and_load_tournament(file_path, name_mapping, player_ids, conn)
            total_loaded += loaded
        
        print("\n" + "="*70)
        print(f"✅ ✅ ✅ [2/5] RELOAD COMPLETE")
        print(f"   Total matches loaded: {total_loaded}")
        print("="*70)
        
        # Verify Alcaraz and Sinner
        print("\n📊 Verification:")
        with conn.cursor() as cur:
            for player_name in ['Carlos Alcaraz', 'Jannik Sinner']:
                cur.execute("""
                    SELECT COUNT(*) as match_count, MAX(date) as last_match
                    FROM matches
                    WHERE player1_id = (SELECT player_id FROM players WHERE name = %s)
                       OR player2_id = (SELECT player_id FROM players WHERE name = %s)
                """, (player_name, player_name))
                result = cur.fetchone()
                print(f"   {player_name}: {result['match_count']} total matches, last: {result['last_match']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

