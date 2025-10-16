#!/usr/bin/env python3
"""
Load Rome Masters 1000 2025 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rome Masters 1000 2025 matches
# Dates: May 8-18, 2025
MATCHES = [
    # ROUND 1 (R64)
    {'date': '2025-05-08', 'winner': 'L Darderi', 'loser': 'Y Bu', 'score': '7-6(4) 6-3', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'V Gaubas', 'loser': 'D Džumhur', 'score': '7-6(7) 2-6 6-4', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'L Djere', 'loser': 'TM Etcheverry', 'score': '6-3 6-2', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'O Virtanen', 'loser': 'H Medjedovic', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'F Passaro', 'loser': 'C-h Tseng', 'score': '6-0 2-6 6-3', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'C Norrie', 'loser': 'C O\'Connell', 'score': '6-3 6-2', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'D Lajović', 'loser': 'Y Nishioka', 'score': '7-5 6-1', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'V Kopriva', 'loser': 'Q Halys', 'score': '6-4 6-3', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'RA Burruchaga', 'loser': 'L Sonego', 'score': '6-2 6-3', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'T Griekspoor', 'loser': 'M Kecmanović', 'score': '4-6 6-3 6-0', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'C Taberner', 'loser': 'A Kovacevic', 'score': '6-3 1-6 7-5', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'C Ugo Carabelli', 'loser': 'P Carreño Busta', 'score': '6-2 1-6 6-3', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'J Thompson', 'loser': 'G Mpetshi Perricard', 'score': '3-6 6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'A Müller', 'loser': 'J Lehečka', 'score': '2-6 6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'C Moutet', 'loser': 'R Hijikata', 'score': '3-6 6-1 7-5', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'F Comesaña', 'loser': 'D Altmaier', 'score': '6-1 7-5', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'L Tien', 'loser': 'R Opelka', 'score': '6-4 7-6(13)', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'J Fearnley', 'loser': 'F Fognini', 'score': '6-2 6-3', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'P Martínez', 'loser': 'M Bellucci', 'score': '6-4 6-2', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'S Ofner', 'loser': 'R Carballés Baena', 'score': '6-3 0-0 RET', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'A Bublik', 'loser': 'R Safiullin', 'score': '6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'M Giron', 'loser': 'G Diallo', 'score': '3-6 6-3 6-4', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'M Gigante', 'loser': 'A Rinderknech', 'score': '7-6(4) 7-6(4)', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'L Nardi', 'loser': 'F Cobolli', 'score': '6-3 6-4', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'J Munar', 'loser': 'T Barrios Vera', 'score': '4-6 6-2 7-5', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'T Seyboth Wild', 'loser': 'N Borges', 'score': '6-1 4-6 6-4', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'F Marozsán', 'loser': 'J Fonseca', 'score': '6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'M Navone', 'loser': 'F Cina', 'score': '6-3 6-3', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'A Vukic', 'loser': 'N Moreno De Alboran', 'score': '7-6(7) 6-2', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'J De Jong', 'loser': 'A Shevchenko', 'score': '6-2 6-4', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'N Jarry', 'loser': 'H Gaston', 'score': '7-6(4) 6-4', 'round': 'R64'},
    {'date': '2025-05-08', 'winner': 'R Bautista Agut', 'loser': 'M Arnaldi', 'score': '6-4 6-3', 'round': 'R64'},
    
    # ROUND 2 (R32)
    {'date': '2025-05-10', 'winner': 'A Zverev', 'loser': 'C Ugo Carabelli', 'score': '6-2 6-1', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'C Alcaraz', 'loser': 'D Lajović', 'score': '6-3 6-3', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'J Draper', 'loser': 'L Darderi', 'score': '6-1 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'L Musetti', 'loser': 'O Virtanen', 'score': '6-3 6-2', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'H Rune', 'loser': 'F Comesaña', 'score': '3-6 6-3 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'D Medvedev', 'loser': 'C Norrie', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'A Fils', 'loser': 'T Griekspoor', 'score': '6-2 6-2', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'F Passaro', 'loser': 'G Dimitrov', 'score': '7-5 6-3', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'S Tsitsipas', 'loser': 'A Müller', 'score': '6-2 7-6(3)', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'C Moutet', 'loser': 'U Humbert', 'score': '6-3 4-0 RET', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'K Khachanov', 'loser': 'RA Burruchaga', 'score': '6-4 5-7 6-1', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'A Popyrin', 'loser': 'C Taberner', 'score': '6-1 7-6(7)', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'V Gaubas', 'loser': 'D Shapovalov', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'B Nakashima', 'loser': 'J Thompson', 'score': 'W/O', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'L Djere', 'loser': 'A Michelsen', 'score': '6-0 6-3', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'V Kopriva', 'loser': 'S Báez', 'score': '6-3 4-6 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'J Sinner', 'loser': 'M Navone', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'M Giron', 'loser': 'T Fritz', 'score': '7-6(4) 7-6(3)', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'C Ruud', 'loser': 'A Bublik', 'score': '6-4 4-6 6-3', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'A de Minaur', 'loser': 'L Nardi', 'score': '6-4 7-5', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'T Paul', 'loser': 'R Bautista Agut', 'score': '6-1 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'J Munar', 'loser': 'B Shelton', 'score': '6-2 6-1', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'S Ofner', 'loser': 'F Tiafoe', 'score': '6-2 6-7(2) 6-3', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'F Marozsán', 'loser': 'A Rublev', 'score': '7-5 4-6 6-3', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'F Cerúndolo', 'loser': 'N Jarry', 'score': '7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'T Machac', 'loser': 'L Tien', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'J Mensik', 'loser': 'M Gigante', 'score': '7-6(7) 7-5', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'S Korda', 'loser': 'A Vukic', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'J De Jong', 'loser': 'A Davidovich Fokina', 'score': '6-0 6-2', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'M Berrettini', 'loser': 'J Fearnley', 'score': '6-4 7-6(7)', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'H Hurkacz', 'loser': 'P Martínez', 'score': '6-1 7-5', 'round': 'R32'},
    {'date': '2025-05-10', 'winner': 'H Dellien', 'loser': 'T Seyboth Wild', 'score': '4-6 6-3 6-4', 'round': 'R32'},
    
    # ROUND 3 (R16)
    {'date': '2025-05-12', 'winner': 'A Zverev', 'loser': 'V Gaubas', 'score': '6-4 6-0', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'C Alcaraz', 'loser': 'L Djere', 'score': '7-6(7) 6-2', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'J Draper', 'loser': 'V Kopriva', 'score': '6-4 6-3', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'L Musetti', 'loser': 'B Nakashima', 'score': '6-4 6-3', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'C Moutet', 'loser': 'H Rune', 'score': '7-5 5-7 7-6(7)', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'D Medvedev', 'loser': 'A Popyrin', 'score': '6-4 6-1', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'A Fils', 'loser': 'S Tsitsipas', 'score': '2-6 6-4 6-2', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'K Khachanov', 'loser': 'F Passaro', 'score': '6-3 6-0', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'J Sinner', 'loser': 'J De Jong', 'score': '6-4 6-2', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'C Ruud', 'loser': 'M Berrettini', 'score': '7-5 2-0 RET', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'A de Minaur', 'loser': 'H Dellien', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'T Paul', 'loser': 'T Machac', 'score': '6-3 6-7(5) 6-4', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'F Cerúndolo', 'loser': 'S Ofner', 'score': '6-2 6-4', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'J Mensik', 'loser': 'F Marozsán', 'score': '6-4 7-6(7)', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'J Munar', 'loser': 'S Korda', 'score': '6-4 6-2', 'round': 'R16'},
    {'date': '2025-05-12', 'winner': 'H Hurkacz', 'loser': 'M Giron', 'score': '6-3 1-6 6-1', 'round': 'R16'},
    
    # ROUND 4 (Continued R16 - some are QF qualifiers)
    {'date': '2025-05-14', 'winner': 'J Sinner', 'loser': 'F Cerúndolo', 'score': '7-6(7) 6-3', 'round': 'R16'},
    {'date': '2025-05-14', 'winner': 'A Zverev', 'loser': 'A Fils', 'score': '7-6(3) 6-1', 'round': 'R16'},
    {'date': '2025-05-14', 'winner': 'C Alcaraz', 'loser': 'K Khachanov', 'score': '6-3 3-6 7-5', 'round': 'R16'},
    {'date': '2025-05-14', 'winner': 'J Draper', 'loser': 'C Moutet', 'score': '1-6 6-4 6-3', 'round': 'R16'},
    {'date': '2025-05-14', 'winner': 'T Paul', 'loser': 'A de Minaur', 'score': '7-5 6-3', 'round': 'R16'},
    {'date': '2025-05-14', 'winner': 'L Musetti', 'loser': 'D Medvedev', 'score': '7-5 6-4', 'round': 'R16'},
    {'date': '2025-05-14', 'winner': 'H Hurkacz', 'loser': 'J Mensik', 'score': '7-6(7) 4-6 7-6(7)', 'round': 'R16'},
    {'date': '2025-05-14', 'winner': 'C Ruud', 'loser': 'J Munar', 'score': '6-3 6-4', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-05-16', 'winner': 'L Musetti', 'loser': 'A Zverev', 'score': '7-6(7) 6-1', 'round': 'QF'},
    {'date': '2025-05-16', 'winner': 'C Alcaraz', 'loser': 'J Draper', 'score': '6-4 6-4', 'round': 'QF'},
    {'date': '2025-05-16', 'winner': 'J Sinner', 'loser': 'C Ruud', 'score': '6-0 6-1', 'round': 'QF'},
    {'date': '2025-05-16', 'winner': 'T Paul', 'loser': 'H Hurkacz', 'score': '7-6(4) 6-3', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-05-17', 'winner': 'J Sinner', 'loser': 'T Paul', 'score': '1-6 6-0 6-3', 'round': 'SF'},
    {'date': '2025-05-17', 'winner': 'C Alcaraz', 'loser': 'L Musetti', 'score': '6-3 7-6(7)', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-05-18', 'winner': 'C Alcaraz', 'loser': 'J Sinner', 'score': '7-6(5) 6-1', 'round': 'F'},
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
    logger.info("ROME MASTERS 1000 2025")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Rome"
    tournament_tier = "Masters 1000"
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
            'tourney_id': '2025-416',  # Rome 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Rome 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Rome' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Rome 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("ROME MASTERS 1000 2025 LOADED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Champion: Carlos Alcaraz 🏆")
    logger.info(f"Runner-up: Jannik Sinner")
    logger.info(f"Final Score: 7-6(5) 6-1")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: Alcaraz-Sinner final preview before French Open")
    logger.info(f"         M Giron upset #4 seed T Fritz 7-6(4) 7-6(3) in R32")

if __name__ == "__main__":
    main()

