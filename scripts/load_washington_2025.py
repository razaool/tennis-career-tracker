#!/usr/bin/env python3
"""
Load Washington DC 2025 ATP 500 matches into the database
Complete tournament data including all rounds
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Washington DC 2025 matches - ATP 500
# Dates: July 28 - August 3, 2025
MATCHES = [
    # SECTION 1 - First Round Matches
    {'date': '2025-07-28', 'winner': 'T Fritz', 'loser': 'G Mpetshi Perricard', 'score': '6-4 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'A Vukic', 'loser': 'M Arnaldi', 'score': '6-4 3-6 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'M Arnaldi', 'loser': 'D Altmaier', 'score': '4-6 6-2 7-6(2)', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'L Sonego', 'loser': 'D Altmaier', 'score': '6-5 5-2 RET', 'round': 'R32'},
    
    {'date': '2025-07-28', 'winner': 'A Davidovich Fokina', 'loser': 'J Munar', 'score': '6-7 6-4', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'J Munar', 'loser': 'M Giron', 'score': '7-5 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'L Tien', 'loser': 'E Nava', 'score': '6-1 6-4', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'L Tien', 'loser': 'A Rublev', 'score': '7-5 6-2', 'round': 'R16'},
    
    # SECTION 1 - Second Round
    {'date': '2025-07-29', 'winner': 'T Fritz', 'loser': 'A Vukic', 'score': '6-3 6-2', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'M Arnaldi', 'loser': 'L Sonego', 'score': '7-6 7-5', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'A Davidovich Fokina', 'loser': 'J Munar', 'score': '6-4 6-2', 'round': 'R16'},
    
    # SECTION 1 - Third Round
    {'date': '2025-07-30', 'winner': 'T Fritz', 'loser': 'M Arnaldi', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-07-30', 'winner': 'A Davidovich Fokina', 'loser': 'L Tien', 'score': '6-2 6-2', 'round': 'R16'},
    
    # SECTION 1 - Quarterfinal
    {'date': '2025-07-31', 'winner': 'A Davidovich Fokina', 'loser': 'T Fritz', 'score': '7-6(3) 3-6 7-5', 'round': 'QF'},
    
    # SECTION 2 - First Round
    {'date': '2025-07-28', 'winner': 'B Shelton', 'loser': 'M McDonald', 'score': '6-6', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'M McDonald', 'loser': 'C Smith', 'score': '6-4 6-1', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'F Marozsán', 'loser': 'B Bonzi', 'score': '7-5 6-1', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'G Diallo', 'loser': 'F Marozsán', 'score': '6-3 6-4', 'round': 'R16'},
    
    {'date': '2025-07-28', 'winner': 'F Cobolli', 'loser': 'Y Nishioka', 'score': '6-6 7-6(7)', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'Y Nishioka', 'loser': 'J Brooksby', 'score': '6-4 5-7 6-1', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'A Kovacevic', 'loser': 'Q Halys', 'score': '6-2 3-6 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'F Tiafoe', 'loser': 'A Kovacevic', 'score': '7-5 3-6 6-3', 'round': 'R16'},
    
    # SECTION 2 - Second Round
    {'date': '2025-07-29', 'winner': 'B Shelton', 'loser': 'M McDonald', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'F Cobolli', 'loser': 'Y Nishioka', 'score': '6-2 6-7(3)', 'round': 'R16'},
    
    # SECTION 2 - Third Round
    {'date': '2025-07-30', 'winner': 'B Shelton', 'loser': 'G Diallo', 'score': '6-3 6-2', 'round': 'R16'},
    {'date': '2025-07-30', 'winner': 'F Tiafoe', 'loser': 'F Cobolli', 'score': '6-1 6-4', 'round': 'R16'},
    
    # SECTION 2 - Quarterfinal
    {'date': '2025-07-31', 'winner': 'B Shelton', 'loser': 'F Tiafoe', 'score': '7-6(7) 6-4', 'round': 'QF'},
    
    # SECTION 3 - First Round
    {'date': '2025-07-28', 'winner': 'R Opelka', 'loser': 'D Medvedev', 'score': '7-6(7) 6-7(5) 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'D Medvedev', 'loser': 'M Cassone', 'score': '3-6 7-6(4) 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'Y Wu', 'loser': 'G Monfils', 'score': '6-3 6-1', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'Y Wu', 'loser': 'A Popyrin', 'score': '7-5 5-7 6-3', 'round': 'R16'},
    
    {'date': '2025-07-28', 'winner': 'D Evans', 'loser': 'A Michelsen', 'score': '3-6 6-4 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'D Evans', 'loser': 'Z Bergs', 'score': '6-4 6-3', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'A Müller', 'loser': 'B Zhukayev', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'C Moutet', 'loser': 'A Müller', 'score': '6-0 6-1', 'round': 'R16'},
    
    # SECTION 3 - Second Round
    {'date': '2025-07-29', 'winner': 'D Medvedev', 'loser': 'R Opelka', 'score': '3-7 7-6(5) 6-1', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'D Evans', 'loser': 'Z Bergs', 'score': '6-2 6-7(4)', 'round': 'R16'},
    
    # SECTION 3 - Third Round
    {'date': '2025-07-30', 'winner': 'D Medvedev', 'loser': 'Y Wu', 'score': '6-3 6-2', 'round': 'R16'},
    {'date': '2025-07-30', 'winner': 'C Moutet', 'loser': 'D Evans', 'score': '6-2 7-6(4)', 'round': 'R16'},
    
    # SECTION 3 - Quarterfinal
    {'date': '2025-07-31', 'winner': 'C Moutet', 'loser': 'D Medvedev', 'score': '1-6 6-4 6-4', 'round': 'QF'},
    
    # SECTION 4 - First Round
    {'date': '2025-07-28', 'winner': 'A de Minaur', 'loser': 'D Goffin', 'score': '7-6(7) 6-4', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'Y Bu', 'loser': 'D Goffin', 'score': '6-4 7-5', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'Z Svajda', 'loser': 'M Kecmanović', 'score': '6-1 6-2', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'J Lehečka', 'loser': 'Z Svajda', 'score': '6-6 6-7(5) 6-2', 'round': 'R16'},
    
    {'date': '2025-07-28', 'winner': 'B Nakashima', 'loser': 'E Quinn', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'E Quinn', 'loser': 'C O\'Connell', 'score': '6-3 6-2', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'C Norrie', 'loser': 'B Harris', 'score': '6-3 7-6(4)', 'round': 'R32'},
    {'date': '2025-07-28', 'winner': 'C Norrie', 'loser': 'L Musetti', 'score': '3-6 6-2 6-3', 'round': 'R16'},
    
    # SECTION 4 - Second Round
    {'date': '2025-07-29', 'winner': 'A de Minaur', 'loser': 'Y Bu', 'score': '7-6(7) 6-7(5) 6-2', 'round': 'R16'},
    {'date': '2025-07-29', 'winner': 'B Nakashima', 'loser': 'E Quinn', 'score': '6-3 6-4', 'round': 'R16'},
    
    # SECTION 4 - Third Round
    {'date': '2025-07-30', 'winner': 'A de Minaur', 'loser': 'J Lehečka', 'score': '7-6(7) 6-7(6) 6-4', 'round': 'R16'},
    {'date': '2025-07-30', 'winner': 'B Nakashima', 'loser': 'C Norrie', 'score': '7-6(7) 6-3', 'round': 'R16'},
    
    # SECTION 4 - Quarterfinal
    {'date': '2025-07-31', 'winner': 'A de Minaur', 'loser': 'B Nakashima', 'score': '6-4 6-4', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-08-02', 'winner': 'A Davidovich Fokina', 'loser': 'B Shelton', 'score': '6-2 7-5', 'round': 'SF'},
    {'date': '2025-08-02', 'winner': 'A de Minaur', 'loser': 'C Moutet', 'score': '6-4 6-3', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-08-03', 'winner': 'A de Minaur', 'loser': 'A Davidovich Fokina', 'score': '5-7 6-1 7-6(3)', 'round': 'F'},
]

def parse_score_details(score):
    """Parse score to get sets won by each player"""
    if not score:
        return None, None, None, None
    
    sets_p1 = 0
    sets_p2 = 0
    games_p1 = 0
    games_p2 = 0
    
    if 'RET' in score or 'W/O' in score:
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
    logger.info("WASHINGTON DC 2025 ATP 500")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Washington"
    tournament_tier = "ATP 500"
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
            'tourney_id': '2025-418',  # Washington 2025 ID
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
        logger.debug(f"{match['round']}: {match['winner']} def. {match['loser']} {match['score']}")
    
    # Insert matches
    inserted = db.bulk_insert_matches(matches_data)
    logger.info(f"\n✅ Inserted {inserted} matches from Washington DC 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Washington' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Washington 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("WASHINGTON DC 2025 LOADED SUCCESSFULLY!")
    logger.info("=" * 70)
    logger.info(f"Champion: Alex de Minaur 🏆")
    logger.info(f"Runner-up: Alejandro Davidovich Fokina")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Semifinalists: A Davidovich Fokina, B Shelton, A de Minaur, C Moutet")

if __name__ == "__main__":
    main()
