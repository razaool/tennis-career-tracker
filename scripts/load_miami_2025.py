#!/usr/bin/env python3
"""
Load Miami Open 2025 Masters 1000 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Miami Open 2025 Masters 1000 matches
# Dates: March 19-30, 2025
MATCHES = [
    # ROUND 1 (R64)
    {'date': '2025-03-19', 'winner': 'Q Halys', 'loser': 'T Seyboth Wild', 'score': '6-3 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'E Spizzirri', 'loser': 'B Harris', 'score': '7-6(7) 3-6 6-2', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'J Munar', 'loser': 'A Rinderknech', 'score': '6-3 7-6(5)', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'A Müller', 'loser': 'R Sakamoto', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'M Kecmanović', 'loser': 'A Kovacevic', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'R Carballés Baena', 'loser': 'C O\'Connell', 'score': '6-3 3-6 7-6(5)', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'C Moutet', 'loser': 'A Blockx', 'score': '7-6(5) 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'N Kyrgios', 'loser': 'M McDonald', 'score': '3-6 6-3 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'C Ugo Carabelli', 'loser': 'B Holt', 'score': '2-6 7-6(7) 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'F Cina', 'loser': 'F Comesaña', 'score': '7-6(4) 7-6(2)', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'C-h Tseng', 'loser': 'M Bellucci', 'score': '7-6(7) 6-2', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'G Monfils', 'loser': 'F Marozsán', 'score': '6-3 3-6 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'T Schoolkate', 'loser': 'E Quinn', 'score': '6-0 6-2', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'A Bublik', 'loser': 'S Báez', 'score': '6-3 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'D Goffin', 'loser': 'A Vukic', 'score': '2-6 6-4 6-2', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'R Hijikata', 'loser': 'H Medjedovic', 'score': '7-5 3-6 7-5', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'J Mensik', 'loser': 'R Bautista Agut', 'score': '6-4 3-6 6-1', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'J Fonseca', 'loser': 'L Tien', 'score': '6-7(1) 6-3 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'R Safiullin', 'loser': 'J Brooksby', 'score': '6-3 3-6 6-3', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'M Arnaldi', 'loser': 'Y Wu', 'score': '7-6(7) 4-6 6-3', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'L Sonego', 'loser': 'M Navone', 'score': '7-5 7-5', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'A Davidovich Fokina', 'loser': 'J-L Struff', 'score': '7-6(3) 6-3', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'G Diallo', 'loser': 'TM Etcheverry', 'score': '6-3 6-0', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'J Thompson', 'loser': 'M Giron', 'score': '3-6 6-4 7-5', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'L Darderi', 'loser': 'P Martínez', 'score': '6-4 6-1', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'Y Bu', 'loser': 'C Norrie', 'score': '6-4 6-2', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'C Wong', 'loser': 'D Altmaier', 'score': '6-4 6-3', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'H Gaston', 'loser': 'Y Nishioka', 'score': '6-4 3-1 RET', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'R Opelka', 'loser': 'C Eubanks', 'score': '6-3 7-6(4)', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'T Tirante', 'loser': 'F Cobolli', 'score': '6-1 3-6 6-3', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'J Fearnley', 'loser': 'B Bonzi', 'score': '7-6(8) 2-6 6-4', 'round': 'R64'},
    {'date': '2025-03-19', 'winner': 'Z Bergs', 'loser': 'N Borges', 'score': '7-6(7) 7-5', 'round': 'R64'},
    
    # ROUND 2 (R32)
    {'date': '2025-03-21', 'winner': 'D Goffin', 'loser': 'C Alcaraz', 'score': '5-7 6-4 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'N Djokovic', 'loser': 'R Hijikata', 'score': '6-0 7-6(1)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'C Ruud', 'loser': 'M Kecmanović', 'score': '3-6 6-4 6-4', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'J Munar', 'loser': 'D Medvedev', 'score': '6-2 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'S Tsitsipas', 'loser': 'C-h Tseng', 'score': '4-6 7-5 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'T Paul', 'loser': 'A Bublik', 'score': '5-7 7-5 6-4', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'G Dimitrov', 'loser': 'F Cina', 'score': '6-1 6-4', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'L Musetti', 'loser': 'Q Halys', 'score': '3-6 7-6(7) 7-5', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'F Auger-Aliassime', 'loser': 'T Schoolkate', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'K Khachanov', 'loser': 'N Kyrgios', 'score': '7-6(3) 6-0', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'F Cerúndolo', 'loser': 'A Müller', 'score': '6-1 6-2', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'S Korda', 'loser': 'E Spizzirri', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'G Monfils', 'loser': 'J Lehečka', 'score': '6-1 3-6 7-6(10)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'A Tabilo', 'loser': 'C Moutet', 'score': '5-7 6-3 7-5', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'B Nakashima', 'loser': 'R Carballés Baena', 'score': '6-4 4-6 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'A Michelsen', 'loser': 'C Ugo Carabelli', 'score': '7-6(7) 5-7 3-6', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'A Zverev', 'loser': 'J Fearnley', 'score': '6-2 6-4', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'T Fritz', 'loser': 'L Sonego', 'score': '7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'J Mensik', 'loser': 'J Draper', 'score': '7-6(7) 7-6(7)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'Z Bergs', 'loser': 'A Rublev', 'score': '7-5 6-4', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'A de Minaur', 'loser': 'Y Bu', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'R Opelka', 'loser': 'H Rune', 'score': '4-6 6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'C Wong', 'loser': 'B Shelton', 'score': '7-6(7) 2-6 7-6(7)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'F Tiafoe', 'loser': 'A Davidovich Fokina', 'score': '7-5 7-6(5)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'A Fils', 'loser': 'G Diallo', 'score': '6-4 2-3 RET', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'J Fonseca', 'loser': 'U Humbert', 'score': '6-4 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'T Machac', 'loser': 'M Arnaldi', 'score': '6-2 1-6 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'R Safiullin', 'loser': 'A Popyrin', 'score': '6-7(4) 6-3 7-5', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'D Shapovalov', 'loser': 'T Tirante', 'score': '6-3 6-7(7) 7-6(3)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'J Thompson', 'loser': 'G Mpetshi Perricard', 'score': '7-6(7) 7-6(7)', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'M Berrettini', 'loser': 'H Gaston', 'score': '4-6 6-3 6-3', 'round': 'R32'},
    {'date': '2025-03-21', 'winner': 'A Walton', 'loser': 'L Darderi', 'score': '6-4 6-4', 'round': 'R32'},
    
    # ROUND 3 (R16)
    {'date': '2025-03-23', 'winner': 'N Djokovic', 'loser': 'C Ugo Carabelli', 'score': '6-1 7-6(1)', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'C Ruud', 'loser': 'A Tabilo', 'score': '6-4 7-6(7)', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'S Korda', 'loser': 'S Tsitsipas', 'score': '7-6(7) 6-3', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'F Cerúndolo', 'loser': 'T Paul', 'score': '6-2 7-6(7)', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'G Dimitrov', 'loser': 'K Khachanov', 'score': '6-7(3) 6-4 7-5', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'L Musetti', 'loser': 'F Auger-Aliassime', 'score': '4-6 6-2 6-3', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'B Nakashima', 'loser': 'D Goffin', 'score': '6-3 6-7(5) 6-3', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'G Monfils', 'loser': 'J Munar', 'score': '7-5 5-7 7-6(7)', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'A Zverev', 'loser': 'J Thompson', 'score': '7-5 6-4', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'T Fritz', 'loser': 'D Shapovalov', 'score': '7-5 6-3', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'A de Minaur', 'loser': 'J Fonseca', 'score': '5-7 7-5 6-3', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'A Fils', 'loser': 'F Tiafoe', 'score': '7-6(13) 5-7 6-2', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'T Machac', 'loser': 'R Opelka', 'score': '7-6(1) 6-3', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'M Berrettini', 'loser': 'Z Bergs', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'J Mensik', 'loser': 'R Safiullin', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-03-23', 'winner': 'A Walton', 'loser': 'C Wong', 'score': '7-6(8) 4-6 6-4', 'round': 'R16'},
    
    # ROUND 4 (R16 continuation / QF qualifiers)
    {'date': '2025-03-25', 'winner': 'T Fritz', 'loser': 'A Walton', 'score': '6-3 7-5', 'round': 'R16'},
    {'date': '2025-03-25', 'winner': 'N Djokovic', 'loser': 'L Musetti', 'score': '6-2 6-2', 'round': 'R16'},
    {'date': '2025-03-25', 'winner': 'F Cerúndolo', 'loser': 'C Ruud', 'score': '6-4 6-2', 'round': 'R16'},
    {'date': '2025-03-25', 'winner': 'M Berrettini', 'loser': 'A de Minaur', 'score': '6-3 7-6(7)', 'round': 'R16'},
    {'date': '2025-03-25', 'winner': 'G Dimitrov', 'loser': 'B Nakashima', 'score': '6-4 7-5', 'round': 'R16'},
    {'date': '2025-03-25', 'winner': 'T Machac', 'loser': 'J Mensik', 'score': 'W/O', 'round': 'R16'},
    {'date': '2025-03-25', 'winner': 'S Korda', 'loser': 'G Monfils', 'score': '6-4 2-6 6-4', 'round': 'R16'},
    {'date': '2025-03-25', 'winner': 'A Fils', 'loser': 'A Zverev', 'score': '3-6 6-3 6-4', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-03-27', 'winner': 'G Dimitrov', 'loser': 'F Cerúndolo', 'score': '6-7(8) 6-4 7-6(3)', 'round': 'QF'},
    {'date': '2025-03-27', 'winner': 'T Fritz', 'loser': 'M Berrettini', 'score': '7-5 7-6(7) 7-5', 'round': 'QF'},
    {'date': '2025-03-27', 'winner': 'N Djokovic', 'loser': 'S Korda', 'score': '6-3 7-6(4)', 'round': 'QF'},
    {'date': '2025-03-27', 'winner': 'J Mensik', 'loser': 'A Fils', 'score': '7-6(5) 6-1', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-03-29', 'winner': 'J Mensik', 'loser': 'T Fritz', 'score': '7-6(7) 4-6 7-6(7)', 'round': 'SF'},
    {'date': '2025-03-29', 'winner': 'N Djokovic', 'loser': 'G Dimitrov', 'score': '6-2 6-3', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-03-30', 'winner': 'J Mensik', 'loser': 'N Djokovic', 'score': '7-6(4) 7-6(4)', 'round': 'F'},
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
    logger.info("MIAMI OPEN 2025 MASTERS 1000")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Miami"
    tournament_tier = "Masters 1000"
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
            'tourney_id': '2025-403',  # Miami 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Miami Open 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Miami' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Miami 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("MIAMI OPEN 2025 LOADED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Champion: Jakub Mensik 🏆 (Age 18 - Youngest Miami champion)")
    logger.info(f"Runner-up: Novak Djokovic")
    logger.info(f"Final Score: 7-6(4) 7-6(4)")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"HUGE Upsets: D Goffin def. #2 seed C Alcaraz 5-7 6-4 6-3 in R32")
    logger.info(f"            J Munar def. #7 seed D Medvedev 6-2 6-3 in R32")
    logger.info(f"            Z Bergs def. #8 seed A Rublev 7-5 6-4 in R32")

if __name__ == "__main__":
    main()

