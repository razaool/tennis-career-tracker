#!/usr/bin/env python3
"""
Load Buenos Aires 2025 ATP 250 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Buenos Aires 2025 ATP 250 matches
# Dates: February 17-23, 2025
MATCHES = [
    # TOP HALF - Section 1 - First Round
    {'date': '2025-02-17', 'winner': 'D Lajović', 'loser': 'R Carballés Baena', 'score': '7-6(10) 7-5', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'JM Cerúndolo', 'loser': 'RA Burruchaga', 'score': '7-6(4) 5-7 7-5', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'F Cerúndolo', 'loser': 'L Darderi', 'score': '6-4 6-4', 'round': 'R32'},
    
    # TOP HALF - Section 2 - First Round
    {'date': '2025-02-17', 'winner': 'C Moutet', 'loser': 'S Nagal', 'score': '7-5 6-2', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'P Martínez', 'loser': 'D Džumhur', 'score': '0-6 6-2 7-6(3)', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'D Schwartzman', 'loser': 'N Jarry', 'score': '7-6(12) 4-6 6-3', 'round': 'R32'},
    
    # BOTTOM HALF - Section 3 - First Round
    {'date': '2025-02-17', 'winner': 'S Báez', 'loser': 'C Ugo Carabelli', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'T Seyboth Wild', 'loser': 'F Díaz Acosta', 'score': '3-6 6-2 6-3', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'L Djere', 'loser': 'A Müller', 'score': '6-3 6-3', 'round': 'R32'},
    
    # BOTTOM HALF - Section 4 - First Round
    {'date': '2025-02-17', 'winner': 'J Fonseca', 'loser': 'TM Etcheverry', 'score': '6-3 6-3', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'F Coria', 'loser': 'H Gaston', 'score': '6-3 6-2', 'round': 'R32'},
    {'date': '2025-02-17', 'winner': 'M Navone', 'loser': 'F Comesaña', 'score': '6-4 6-4', 'round': 'R32'},
    
    # Second Round (R16)
    {'date': '2025-02-18', 'winner': 'A Zverev', 'loser': 'D Lajović', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'F Cerúndolo', 'loser': 'JM Cerúndolo', 'score': '6-2 6-3', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'L Musetti', 'loser': 'C Moutet', 'score': '6-2 6-3', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'P Martínez', 'loser': 'D Schwartzman', 'score': '6-2 6-2', 'round': 'R16'},
    
    {'date': '2025-02-18', 'winner': 'T Seyboth Wild', 'loser': 'S Báez', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'L Djere', 'loser': 'A Tabilo', 'score': '2-6 6-1 7-6(2)', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'J Fonseca', 'loser': 'F Coria', 'score': '2-6 6-4 6-2', 'round': 'R16'},
    {'date': '2025-02-18', 'winner': 'M Navone', 'loser': 'H Rune', 'score': '6-1 7-6(2)', 'round': 'R16'},
    
    # Quarterfinals
    {'date': '2025-02-20', 'winner': 'F Cerúndolo', 'loser': 'A Zverev', 'score': '3-6 6-3 6-2', 'round': 'QF'},
    {'date': '2025-02-20', 'winner': 'P Martínez', 'loser': 'L Musetti', 'score': 'W/O', 'round': 'QF'},
    {'date': '2025-02-20', 'winner': 'L Djere', 'loser': 'T Seyboth Wild', 'score': '7-6(3) 6-3', 'round': 'QF'},
    {'date': '2025-02-20', 'winner': 'J Fonseca', 'loser': 'M Navone', 'score': '3-6 6-4 7-5', 'round': 'QF'},
    
    # Semifinals
    {'date': '2025-02-22', 'winner': 'F Cerúndolo', 'loser': 'P Martínez', 'score': 'W/O', 'round': 'SF'},
    {'date': '2025-02-22', 'winner': 'J Fonseca', 'loser': 'L Djere', 'score': '7-6(3) 5-7 6-1', 'round': 'SF'},
    
    # Final
    {'date': '2025-02-23', 'winner': 'J Fonseca', 'loser': 'F Cerúndolo', 'score': '6-4 7-6(1)', 'round': 'F'},
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
    logger.info("BUENOS AIRES 2025 ATP 250")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Buenos Aires"
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
            'tourney_id': '2025-506',  # Buenos Aires 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Buenos Aires 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Buenos Aires' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Buenos Aires 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("BUENOS AIRES 2025 LOADED SUCCESSFULLY!")
    logger.info("=" * 70)
    logger.info(f"Champion: João Fonseca 🏆")
    logger.info(f"Runner-up: Francisco Cerúndolo")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: Fonseca def. #1 seed Zverev's conqueror F Cerúndolo in final!")

if __name__ == "__main__":
    main()
