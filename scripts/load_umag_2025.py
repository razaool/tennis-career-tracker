#!/usr/bin/env python3
"""
Load Umag 2025 ATP 250 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Umag 2025 ATP 250 matches
# Dates: July 21-27, 2025
MATCHES = [
    # ROUND 1 (R32)
    {'date': '2025-07-21', 'winner': 'V Kopriva', 'loser': 'R Collignon', 'score': '3-6 6-4 6-3', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'F Passaro', 'loser': 'M Dodig', 'score': '4-6 6-1 6-2', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'M Navone', 'loser': 'T Barrios Vera', 'score': '6-1 6-2', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'N Basilashvili', 'loser': 'R Carballés Baena', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'P Llamas Ruiz', 'loser': 'K Majchrzak', 'score': '6-2 6-4', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'S Wawrinka', 'loser': 'A Guillen Meza', 'score': '6-4 6-1', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'T Droguet', 'loser': 'C Garin', 'score': '6-3 6-3', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'T Atmane', 'loser': 'D Lajović', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'C-h Tseng', 'loser': 'G Zeppieri', 'score': '7-5 6-4', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'C Taberner', 'loser': 'P-H Herbert', 'score': '6-4 7-6(7)', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'D Prizmic', 'loser': 'E Moller', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-07-21', 'winner': 'J De Jong', 'loser': 'M Poljicak', 'score': '6-3 6-3', 'round': 'R32'},
    
    # ROUND 2 (R16)
    {'date': '2025-07-22', 'winner': 'C Ugo Carabelli', 'loser': 'F Passaro', 'score': '6-7(5) 6-2 6-3', 'round': 'R16'},
    {'date': '2025-07-22', 'winner': 'P Llamas Ruiz', 'loser': 'T Atmane', 'score': '6-3 6-3', 'round': 'R16'},
    {'date': '2025-07-22', 'winner': 'C Taberner', 'loser': 'F Cerúndolo', 'score': '6-7(2) 6-4 7-5', 'round': 'R16'},
    {'date': '2025-07-22', 'winner': 'L Darderi', 'loser': 'C-h Tseng', 'score': '7-5 6-0', 'round': 'R16'},
    {'date': '2025-07-22', 'winner': 'D Džumhur', 'loser': 'S Wawrinka', 'score': '6-4 7-5', 'round': 'R16'},
    {'date': '2025-07-22', 'winner': 'J De Jong', 'loser': 'M Navone', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-07-22', 'winner': 'T Droguet', 'loser': 'V Kopriva', 'score': '6-2 6-3', 'round': 'R16'},
    {'date': '2025-07-22', 'winner': 'D Prizmic', 'loser': 'N Basilashvili', 'score': '2-6 6-3 6-2', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-07-24', 'winner': 'L Darderi', 'loser': 'D Prizmic', 'score': '1-6 6-2 6-3', 'round': 'QF'},
    {'date': '2025-07-24', 'winner': 'C Ugo Carabelli', 'loser': 'P Llamas Ruiz', 'score': '6-4 5-2 RET', 'round': 'QF'},
    {'date': '2025-07-24', 'winner': 'D Džumhur', 'loser': 'T Droguet', 'score': '3-6 7-5 6-2', 'round': 'QF'},
    {'date': '2025-07-24', 'winner': 'C Taberner', 'loser': 'J De Jong', 'score': '7-5 6-3', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-07-26', 'winner': 'L Darderi', 'loser': 'C Ugo Carabelli', 'score': '7-6(8) 6-3', 'round': 'SF'},
    {'date': '2025-07-26', 'winner': 'C Taberner', 'loser': 'D Džumhur', 'score': '6-2 6-1', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-07-27', 'winner': 'L Darderi', 'loser': 'C Taberner', 'score': '6-3 6-3', 'round': 'F'},
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
    logger.info("UMAG 2025 ATP 250")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Umag"
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
            'tourney_id': '2025-439',  # Umag 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Umag 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Umag' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Umag 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("UMAG 2025 LOADED SUCCESSFULLY!")
    logger.info("=" * 70)
    logger.info(f"Champion: Luciano Darderi 🏆")
    logger.info(f"Runner-up: Carlos Taberner")
    logger.info(f"Final Score: 6-3 6-3")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: C Taberner upset #1 seed F Cerúndolo 6-7(2) 6-4 7-5 in R16!")

if __name__ == "__main__":
    main()

