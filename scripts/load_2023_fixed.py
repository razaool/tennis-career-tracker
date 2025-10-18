#!/usr/bin/env python3
"""
Load 2023 data using the fixed parser
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.parse_and_load_data import TennisDataParser
from database.db_manager import DatabaseManager

print('='*100)
print('LOADING 2023 DATA WITH FIXED PARSER')
print('='*100)

db = DatabaseManager()
parser = TennisDataParser(db)

# Parse the 2023 file
print('\n▶️  Parsing atp_matches_2023.csv...')
file_path = Path('data/raw/tennis_atp/atp_matches_2023.csv')
matches_data = parser.parse_match_file(file_path)

print(f'✅ Parsed {len(matches_data)} matches')

# Insert into database
print(f'\n▶️  Inserting into database...')
inserted = db.bulk_insert_matches(matches_data)
print(f'✅ Inserted {inserted} matches (rest were duplicates/skipped)')

# Verify
print(f'\n📊 VERIFICATION:')
with db.get_cursor() as cursor:
    cursor.execute("SELECT COUNT(*) as cnt FROM matches WHERE EXTRACT(YEAR FROM date) = 2023")
    total = cursor.fetchone()['cnt']
    
    cursor.execute("""
        SELECT COUNT(*) as cnt FROM matches
        WHERE EXTRACT(YEAR FROM date) = 2023
          AND tournament_tier = 'Grand Slam'
          AND round = 'F'
    """)
    gs_finals = cursor.fetchone()['cnt']
    
    cursor.execute("""
        SELECT p.name, COUNT(*) as cnt
        FROM matches m
        JOIN players p ON (m.player1_id = p.player_id OR m.player2_id = p.player_id)
        WHERE EXTRACT(YEAR FROM m.date) = 2023
          AND p.name IN ('Carlos Alcaraz', 'Novak Djokovic', 'Jannik Sinner')
        GROUP BY p.name
        ORDER BY p.name
    """)
    players = cursor.fetchall()

print(f'   Total 2023 matches: {total:,}')
print(f'   Grand Slam finals: {gs_finals}')
print(f'\n   Top players:')
for p in players:
    print(f'     • {p["name"]}: {p["cnt"]} matches')

print('\n' + '='*100)
print('✅ 2023 DATA LOADED SUCCESSFULLY!')
print('='*100)

