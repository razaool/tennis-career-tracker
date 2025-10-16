#!/usr/bin/env python3
"""
Load Kitzbuhel 2025 ATP 250 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kitzbuhel 2025 ATP 250 matches
# Dates: July 28 - August 3, 2025
MATCHES = [
    # ROUND 1 (R32)
    {'date': '2025-07-28', 'winner': 'A Rinderknech', 'loser': 'F Bagnis', 'score': '7-6(7) 4-6 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'F Comesaña', 'loser': 'T Boyer', 'score': '6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'M Fucsovics', 'loser': 'J Schwaerzler', 'score': '6-2 2-6 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'N Gombos', 'loser': 'H Gaston', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'A Shevchenko', 'loser': 'D Galán', 'score': '2-6 6-3 6-4', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'F Misolic', 'loser': 'TM Etcheverry', 'score': '7-5 5-7 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'T Seyboth Wild', 'loser': 'J Engel', 'score': '7-5 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'T Tirante', 'loser': 'J Faria', 'score': '6-2 6-2', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'A Cazaux', 'loser': 'I Buse', 'score': '6-3 3-6 7-5', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'J-L Struff', 'loser': 'S Ofner', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'Y Hanfmann', 'loser': 'L Neumayer', 'score': '7-5 6-2', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'B Van De Zandschulp', 'loser': 'N Jarry', 'score': '6-4 4-6 6-3', 'round': 'R32'},
    
    # ROUND 2 (R16)
    {'date': '2025-07-29', 'winner': 'A Bublik', 'loser': 'T Tirante', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'Y Hanfmann', 'loser': 'S Báez', 'score': '5-7 6-3 7-5', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'J-L Struff', 'loser': 'P Martínez', 'score': '6-2 6-2', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'T Seyboth Wild', 'loser': 'R Bautista Agut', 'score': '7-5 7-5', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'A Rinderknech', 'loser': 'N Gombos', 'score': '6-7(3) 6-4 6-4', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'A Cazaux', 'loser': 'F Comesaña', 'score': '6-4 7-6(7)', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'A Shevchenko', 'loser': 'M Fucsovics', 'score': '7-5 6-4', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'B Van De Zandschulp', 'loser': 'F Misolic', 'score': '6-3 7-6(7)', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-07-31', 'winner': 'A Bublik', 'loser': 'A Shevchenko', 'score': '6-4 6-2', 'round': 'QF'},
    {'date': '2025-07-31', 'winner': 'A Rinderknech', 'loser': 'Y Hanfmann', 'score': '6-4 3-6 6-1', 'round': 'QF'},
    {'date': '2025-07-31', 'winner': 'B Van De Zandschulp', 'loser': 'T Seyboth Wild', 'score': '7-6(2) 6-2', 'round': 'QF'},
    {'date': '2025-07-31', 'winner': 'A Cazaux', 'loser': 'J-L Struff', 'score': '6-3 6-4', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-08-02', 'winner': 'A Bublik', 'loser': 'B Van De Zandschulp', 'score': '6-3 6-4', 'round': 'SF'},
    {'date': '2025-08-02', 'winner': 'A Cazaux', 'loser': 'A Rinderknech', 'score': '7-5 6-3', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-08-03', 'winner': 'A Bublik', 'loser': 'A Cazaux', 'score': '6-4 6-3', 'round': 'F'},
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
    logger.info("KITZBUHEL 2025 ATP 250")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Kitzbuhel"
    tournament_tier = "ATP 250"
    surface = "clay"
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
            'tourney_id': '2025-319',  # Kitzbuhel 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Kitzbuhel 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Kitzbuhel' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Kitzbuhel 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("KITZBUHEL 2025 LOADED SUCCESSFULLY!")
    logger.info("=" * 70)
    logger.info(f"Champion: Alexander Bublik 🏆")
    logger.info(f"Runner-up: Arthur Cazaux")
    logger.info(f"Final Score: 6-4 6-3")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: Y Hanfmann upset #2 seed S Báez 5-7 6-3 7-5 in R16!")

if __name__ == "__main__":
    main()

