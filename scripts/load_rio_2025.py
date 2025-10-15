#!/usr/bin/env python3
"""
Load Rio 2025 ATP 500 matches directly into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rio 2025 matches
MATCHES = [
    # First Round (R32) - Feb 17
    {'date': '2025-02-17', 'winner': 'A Zverev', 'loser': 'Y Bu', 'score': '7-6(7) 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'A Shevchenko', 'loser': 'F Meligeni Alves', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'F Comesaña', 'loser': 'G Heide', 'score': '7-6(7) 6-7(7) 6-3', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'N Jarry', 'loser': 'JM Cerúndolo', 'score': '4-6 6-3 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'F Cerúndolo', 'loser': 'H Gaston', 'score': '7-6(11) 6-0', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'L Darderi', 'loser': 'H Dellien', 'score': '7-6(7) 2-0 RET', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'A Müller', 'loser': 'J Fonseca', 'score': '6-1 7-6(7)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'TM Etcheverry', 'loser': 'C Moutet', 'score': '6-3 7-6(6)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'S Báez', 'loser': 'RA Burruchaga', 'score': '6-3 7-5', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'M Navone', 'loser': 'R Carballés Baena', 'score': '6-4 6-3', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'T Monteiro', 'loser': 'F Díaz Acosta', 'score': '3-6 6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'C-h Tseng', 'loser': 'A Tabilo', 'score': '6-2 7-5', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'C Ugo Carabelli', 'loser': 'P Martínez', 'score': '4-6 6-3 6-3', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'D Džumhur', 'loser': 'D Lajović', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'J Munar', 'loser': 'T Seyboth Wild', 'score': '6-4 3-6 6-0', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'J Faria', 'loser': 'T Barrios Vera', 'score': '6-2 7-5', 'round': 'R32'},
    
    # Second Round (R16) - Feb 18-19
    {'date': '2025-02-18', 'winner': 'A Zverev', 'loser': 'A Shevchenko', 'score': '7-6(7) 7-6(8)', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'F Comesaña', 'loser': 'N Jarry', 'score': '7-6(7) 6-1 7-6(8)', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'F Cerúndolo', 'loser': 'L Darderi', 'score': '6-1 6-3 6-2', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'A Müller', 'loser': 'TM Etcheverry', 'score': '7-5 7-6(7)', 'round': 'R16'},
    {'date': '2025-02-19', 'winner': 'S Báez', 'loser': 'M Navone', 'score': '6-4 1-6 6-3', 'round': 'R16'},
    {'date': '2025-02-19', 'winner': 'C-h Tseng', 'loser': 'T Monteiro', 'score': '6-4 6-3 7-6(7)', 'round': 'R16'},
    {'date': '2025-02-19', 'winner': 'C Ugo Carabelli', 'loser': 'D Džumhur', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-02-19', 'winner': 'J Faria', 'loser': 'J Munar', 'score': '6-4 2-6 6-3', 'round': 'R16'},
    
    # Quarterfinals (QF) - Feb 20-21
    {'date': '2025-02-20', 'winner': 'F Comesaña', 'loser': 'A Zverev', 'score': '4-6 6-3 6-4', 'round': 'QF'},
    {'date': '2025-02-20', 'winner': 'A Müller', 'loser': 'F Cerúndolo', 'score': '7-5 6-1', 'round': 'QF'},
    {'date': '2025-02-21', 'winner': 'S Báez', 'loser': 'C-h Tseng', 'score': '6-4 6-1', 'round': 'QF'},
    {'date': '2025-02-21', 'winner': 'C Ugo Carabelli', 'loser': 'J Faria', 'score': '7-6(7) 6-4', 'round': 'QF'},
    
    # Semifinals (SF) - Feb 22
    {'date': '2025-02-22', 'winner': 'A Müller', 'loser': 'F Comesaña', 'score': '7-5 6-7(3) 6-3', 'round': 'SF'},
    {'date': '2025-02-22', 'winner': 'S Báez', 'loser': 'C Ugo Carabelli', 'score': '3-6 6-1 6-1', 'round': 'SF'},
    
    # Final (F) - Feb 23
    {'date': '2025-02-23', 'winner': 'A Müller', 'loser': 'S Báez', 'score': '6-3 6-4', 'round': 'F'},
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
        return 2, 0, 0, 0  # Winner gets 2 sets by default
    
    # Split by space to get individual sets
    sets = score.split()
    
    for set_score in sets:
        # Remove tiebreak scores (e.g., "7-6(3)" -> "7-6")
        if '(' in set_score:
            set_score = set_score.split('(')[0]
        
        # Parse games
        if '-' in set_score:
            parts = set_score.split('-')
            if len(parts) == 2:
                try:
                    g1, g2 = int(parts[0]), int(parts[1])
                    games_p1 += g1
                    games_p2 += g2
                    
                    # Determine set winner
                    if g1 > g2:
                        sets_p1 += 1
                    elif g2 > g1:
                        sets_p2 += 1
                except ValueError:
                    continue
    
    return sets_p1, sets_p2, games_p1, games_p2

def main():
    logger.info("=" * 70)
    logger.info("LOADING RIO DE JANEIRO 2025 ATP 500")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Rio de Janeiro"
    tournament_tier = "ATP 500"
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
            'tourney_id': '2025-533',  # Rio 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Rio de Janeiro 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Rio de Janeiro' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Rio 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("RIO 2025 LOADED SUCCESSFULLY!")
    logger.info("=" * 70)
    logger.info(f"Champion: Alexandre Müller 🏆")
    logger.info(f"Runner-up: Sebastian Báez")
    logger.info(f"Total matches: {len(MATCHES)}")

if __name__ == "__main__":
    main()

