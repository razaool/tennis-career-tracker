#!/usr/bin/env python3
"""
Load Delray Beach 2025 ATP 250 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Delray Beach 2025 ATP 250 matches
# Dates: February 17-23, 2025
MATCHES = [
    # ROUND 1 (R32)
    {'date': '2025-02-17', 'winner': 'B Nakashima', 'loser': 'J Trotter', 'score': '7-6(7) 6-1', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'M Kecmanović', 'loser': 'B Gojo', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'M Mmoh', 'loser': 'A Shevchenko', 'score': '7-5 7-6(5)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'E Quinn', 'loser': 'T Boyer', 'score': '6-2 7-6(5) 7-6(7)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'C Norrie', 'loser': 'Z Svajda', 'score': '7-5 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'A Davidovich Fokina', 'loser': 'T Daniel', 'score': '6-2 7-6(2)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'A Rinderknech', 'loser': 'D Popko', 'score': '6-2 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'R Opelka', 'loser': 'C Eubanks', 'score': '6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'M McDonald', 'loser': 'K Nishikori', 'score': '7-6(4) 4-6 7-5', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'Y Bu', 'loser': 'R Hijikata', 'score': '6-2 6-0', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'Y Nishioka', 'loser': 'A Vukic', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'L Tien', 'loser': 'A Walton', 'score': '6-4 6-3', 'round': 'R32'},
    
    # ROUND 2 (R16)
    {'date': '2025-02-18', 'winner': 'M Mmoh', 'loser': 'A Michelsen', 'score': '7-6(10) 0-3 RET', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'M Giron', 'loser': 'E Quinn', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'M Kecmanović', 'loser': 'Y Nishioka', 'score': 'W/O', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'C Norrie', 'loser': 'A Rinderknech', 'score': '7-6(11) 6-2', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'T Fritz', 'loser': 'Y Bu', 'score': '7-6(7) 6-2', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'M Arnaldi', 'loser': 'L Tien', 'score': '7-6(7) 4-6 7-6(7)', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'B Nakashima', 'loser': 'R Opelka', 'score': '3-6 7-5 6-2', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'A Davidovich Fokina', 'loser': 'M McDonald', 'score': '6-2 5-7 6-0', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-02-20', 'winner': 'A Davidovich Fokina', 'loser': 'T Fritz', 'score': '7-6(4) 7-6(5)', 'round': 'QF'},
    {'date': '2025-02-20', 'winner': 'A Michelsen', 'loser': 'C Norrie', 'score': '7-6(3) 7-5', 'round': 'QF'},
    {'date': '2025-02-20', 'winner': 'M Arnaldi', 'loser': 'B Nakashima', 'score': '7-6(7) 6-2', 'round': 'QF'},
    {'date': '2025-02-20', 'winner': 'M Kecmanović', 'loser': 'M Giron', 'score': '2-6 6-4 6-2', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-02-22', 'winner': 'M Kecmanović', 'loser': 'A Michelsen', 'score': '7-6(3) 6-3', 'round': 'SF'},
    {'date': '2025-02-22', 'winner': 'A Davidovich Fokina', 'loser': 'M Arnaldi', 'score': '6-4 6-4', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-02-23', 'winner': 'M Kecmanović', 'loser': 'A Davidovich Fokina', 'score': '3-6 6-1 7-5', 'round': 'F'},
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
    logger.info("DELRAY BEACH 2025 ATP 250")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Delray Beach"
    tournament_tier = "ATP 250"
    surface = "hard"
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
            'tourney_id': '2025-499',  # Delray Beach 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Delray Beach 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Delray Beach' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Delray Beach 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("DELRAY BEACH 2025 LOADED SUCCESSFULLY!")
    logger.info("=" * 70)
    logger.info(f"Champion: Miomir Kecmanović 🏆")
    logger.info(f"Runner-up: Alejandro Davidovich Fokina")
    logger.info(f"Final Score: 3-6 6-1 7-5")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: ADF upset #1 seed T Fritz 7-6(4) 7-6(5) in QF!")

if __name__ == "__main__":
    main()

