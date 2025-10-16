#!/usr/bin/env python3
"""
Load s-Hertogenbosch (Libema Open) 2025 ATP 250 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# s-Hertogenbosch (Libema Open) 2025 ATP 250 matches
# Dates: June 16-22, 2025
MATCHES = [
    # ROUND 1 (R32)
    {'date': '2025-06-16', 'winner': 'J Thompson', 'loser': 'A Kovacevic', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'N Borges', 'loser': 'N Basavareddy', 'score': '7-6(7) 6-2', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'N Jarry', 'loser': 'L Darderi', 'score': '5-7 6-4 7-6(7)', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'G Diallo', 'loser': 'A Vukic', 'score': '7-5 7-6(7)', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'O Virtanen', 'loser': 'TM Etcheverry', 'score': '7-6(8) 7-5', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'R Opelka', 'loser': 'J De Jong', 'score': '6-7(5) 7-6(7) 6-2', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'M McDonald', 'loser': 'M Bellucci', 'score': '6-1 6-7(4) 6-3', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'Z Bergs', 'loser': 'A Blockx', 'score': '6-3 1-6 7-6(7)', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'H Hurkacz', 'loser': 'R Bautista Agut', 'score': '7-6(7) 6-4', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'M Lajal', 'loser': 'L Djere', 'score': '6-2 6-4', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'D Evans', 'loser': 'R Hijikata', 'score': '3-6 6-4 6-3', 'round': 'R32'},
    {'date': '2025-06-16', 'winner': 'A Mannarino', 'loser': 'C O\'Connell', 'score': '6-1 6-3', 'round': 'R32'},
    
    # ROUND 2 (R16)
    {'date': '2025-06-17', 'winner': 'K Khachanov', 'loser': 'M McDonald', 'score': '6-3 5-7 7-6(4)', 'round': 'R16'},
    {'date': '2025-06-17', 'winner': 'G Diallo', 'loser': 'J Thompson', 'score': '4-6 6-1 7-5', 'round': 'R16'},
    {'date': '2025-06-17', 'winner': 'D Medvedev', 'loser': 'A Mannarino', 'score': '7-6(8) 6-4', 'round': 'R16'},
    {'date': '2025-06-17', 'winner': 'U Humbert', 'loser': 'D Evans', 'score': '7-5 6-3', 'round': 'R16'},
    {'date': '2025-06-17', 'winner': 'Z Bergs', 'loser': 'A Popyrin', 'score': '6-7(3) 6-2 7-6(3)', 'round': 'R16'},
    {'date': '2025-06-17', 'winner': 'M Lajal', 'loser': 'H Hurkacz', 'score': 'W/O', 'round': 'R16'},
    {'date': '2025-06-17', 'winner': 'N Borges', 'loser': 'O Virtanen', 'score': 'W/O', 'round': 'R16'},
    {'date': '2025-06-17', 'winner': 'R Opelka', 'loser': 'N Jarry', 'score': '7-6(7) 6-3', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-06-19', 'winner': 'R Opelka', 'loser': 'D Medvedev', 'score': '7-6(5) 7-6(5)', 'round': 'QF'},
    {'date': '2025-06-19', 'winner': 'U Humbert', 'loser': 'N Borges', 'score': '6-1 6-4', 'round': 'QF'},
    {'date': '2025-06-19', 'winner': 'G Diallo', 'loser': 'K Khachanov', 'score': '7-6(8) 6-4', 'round': 'QF'},
    {'date': '2025-06-19', 'winner': 'Z Bergs', 'loser': 'M Lajal', 'score': '7-6(7) 7-6(7)', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-06-21', 'winner': 'G Diallo', 'loser': 'U Humbert', 'score': '6-3 7-6(7)', 'round': 'SF'},
    {'date': '2025-06-21', 'winner': 'Z Bergs', 'loser': 'R Opelka', 'score': '6-1 6-4', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-06-22', 'winner': 'G Diallo', 'loser': 'Z Bergs', 'score': '7-5 7-6(10)', 'round': 'F'},
]

def parse_score_details(score):
    """Parse score to get sets won by each player"""
    if not score:
        return None, None, None, None
    
    sets_p1 = 0
    sets_p2 = 0
    games_p1 = 0
    games_p2 = 0
    
    if 'W/O' in score or 'RET' in score:
        return 2, 0, 0, 0
    
    sets = score.split()
    
    for set_score in sets:
        if '(' in set_score:
            set_score = set_score.split('(')[0]
        
        if '-' in set_score:
            parts = set_score.split('-')
            if len(parts) == 2:
                try:
                    g1, g2 = int(parts[0]), int(parts[1])
                    games_p1 += g1
                    games_p2 += g2
                    
                    if g1 > g2:
                        sets_p1 += 1
                    elif g2 > g1:
                        sets_p2 += 1
                except ValueError:
                    continue
    
    return sets_p1, sets_p2, games_p1, games_p2

def main():
    logger.info("=" * 70)
    logger.info("S-HERTOGENBOSCH (LIBEMA OPEN) 2025 ATP 250")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "s-Hertogenbosch"
    tournament_tier = "ATP 250"
    surface = "grass"
    best_of = 3
    
    matches_data = []
    
    for idx, match in enumerate(MATCHES, 1):
        # Get or create players
        winner_id = db.get_player_id(match['winner'])
        loser_id = db.get_player_id(match['loser'])
        
        # Parse score
        sets_w, sets_l, games_w, games_l = parse_score_details(match['score'])
        
        # Create match data with all required fields
        match_data = {
            'tourney_id': '2025-440',  # s-Hertogenbosch 2025 ID
            'match_num': idx,
            'date': date.fromisoformat(match['date']),
            'tournament_name': tournament_name,
            'tournament_tier': tournament_tier,
            'surface': surface,
            'round': match['round'],
            'best_of': best_of,
            'player1_id': winner_id,
            'player2_id': loser_id,
            'winner_id': winner_id,
            'player1_rank': None,
            'player2_rank': None,
            'player1_rank_points': None,
            'player2_rank_points': None,
            'score': match['score'],
            'player1_sets_won': sets_w,
            'player2_sets_won': sets_l,
            'player1_games_won': games_w,
            'player2_games_won': games_l,
            'player1_aces': None,
            'player2_aces': None,
            'player1_double_faults': None,
            'player2_double_faults': None,
            'player1_first_serve_pct': None,
            'player2_first_serve_pct': None,
        }
        
        matches_data.append(match_data)
    
    # Insert matches
    inserted = db.bulk_insert_matches(matches_data)
    logger.info(f"\n✅ Inserted {inserted} matches from s-Hertogenbosch 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 's-Hertogenbosch' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} s-Hertogenbosch 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("S-HERTOGENBOSCH 2025 LOADED SUCCESSFULLY!")
    logger.info("=" * 70)
    logger.info(f"Champion: Gabriel Diallo 🏆")
    logger.info(f"Runner-up: Zizou Bergs")
    logger.info(f"Final Score: 7-5 7-6(10)")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: R Opelka upset #1 seed D Medvedev 7-6(5) 7-6(5) in QF!")

if __name__ == "__main__":
    main()

