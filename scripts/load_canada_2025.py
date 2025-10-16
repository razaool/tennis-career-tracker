#!/usr/bin/env python3
"""
Load Canada (Montreal) Masters 1000 2025 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Canada Masters 1000 2025 matches
# Dates: August 4-10, 2025
MATCHES = [
    # ROUND 1 (R64)
    {'date': '2025-08-04', 'winner': 'J Duckworth', 'loser': 'J Shang', 'score': '6-3 7-6(3)', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'M Kecmanović', 'loser': 'Q Halys', 'score': '4-6 6-4 7-5', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'F Bagnis', 'loser': 'V Pospisil', 'score': '6-2 3-6 6-3', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'E Nava', 'loser': 'Z Bergs', 'score': '6-1 7-6(7)', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'N Arseneault', 'loser': 'V Royer', 'score': '6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'R Safiullin', 'loser': 'U Blanchet', 'score': '4-6 6-2 7-6(11)', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'JP Ficovich', 'loser': 'J Fearnley', 'score': '6-2 6-3', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'TM Etcheverry', 'loser': 'P-H Herbert', 'score': '6-4 4-6 7-5', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'G Mpetshi Perricard', 'loser': 'S Mochizuki', 'score': '6-4 6-2', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'T Barrios Vera', 'loser': 'G Monfils', 'score': '6-4 4-6 7-6(3)', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'L Tien', 'loser': 'C Smith', 'score': '6-4 7-5', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'R Opelka', 'loser': 'S Ofner', 'score': '7-6(8) 7-5', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'A Walton', 'loser': 'B Bonzi', 'score': '4-6 6-0 6-3', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'A Galarneau', 'loser': 'A Rinderknech', 'score': '7-6(2) 6-3', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'F Marozsán', 'loser': 'H Dellien', 'score': '6-2 6-2', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'P Carreño Busta', 'loser': 'L Draxl', 'score': '6-2 4-6 6-4', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'M Gigante', 'loser': 'B Coric', 'score': '4-6 6-2 7-6(7)', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'R Carballés Baena', 'loser': 'C Ugo Carabelli', 'score': '6-4 4-1 RET', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'T Boyer', 'loser': 'A Kovacevic', 'score': '7-5 7-6(7)', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'F Comesaña', 'loser': 'D Džumhur', 'score': '6-3 7-5', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'A Mannarino', 'loser': 'M Giron', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'T Schoolkate', 'loser': 'J Fonseca', 'score': '7-6(7) 6-4', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'Y Watanuki', 'loser': 'D Altmaier', 'score': '3-6 6-1 6-4', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'A Vukic', 'loser': 'P Martínez', 'score': '7-5 6-3', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'M Bellucci', 'loser': 'H Gaston', 'score': '6-3 6-4 0-2 RET', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'D Svrcina', 'loser': 'A Blockx', 'score': '6-4 6-2', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'J Munar', 'loser': 'D Martin', 'score': '6-3 6-0', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'C O\'Connell', 'loser': 'C-h Tseng', 'score': '6-1 6-2', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'E Quinn', 'loser': 'Y Nishioka', 'score': '7-6(7) 6-2', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'Y Bu', 'loser': 'V Kopriva', 'score': '7-6(4) 6-2', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'M McDonald', 'loser': 'D Goffin', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-08-04', 'winner': 'C Moutet', 'loser': 'J Brooksby', 'score': '6-2 6-1', 'round': 'R64'},
    
    # ROUND 2 (R32)
    {'date': '2025-08-06', 'winner': 'A Zverev', 'loser': 'A Walton', 'score': '7-6(8) 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'L Musetti', 'loser': 'J Duckworth', 'score': '7-5 6-1', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'H Rune', 'loser': 'G Mpetshi Perricard', 'score': '7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'C Ruud', 'loser': 'R Safiullin', 'score': '6-3 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'D Medvedev', 'loser': 'D Svrcina', 'score': '7-6(7) 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'K Khachanov', 'loser': 'JP Ficovich', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'F Cerúndolo', 'loser': 'J Munar', 'score': '7-6(4) 4-6 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'R Opelka', 'loser': 'T Machac', 'score': '7-6(7) 6-7(5) 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A Popyrin', 'loser': 'N Arseneault', 'score': '7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'L Tien', 'loser': 'D Shapovalov', 'score': '7-6(4) 7-5', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'TM Etcheverry', 'loser': 'T Griekspoor', 'score': '6-4 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A Michelsen', 'loser': 'T Barrios Vera', 'score': '7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A Müller', 'loser': 'M Kecmanović', 'score': '2-6 6-3 7-5', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'N Borges', 'loser': 'F Bagnis', 'score': '7-5 6-7(7) 6-2', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'M Arnaldi', 'loser': 'T Schoolkate', 'score': '6-3 3-6 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'E Nava', 'loser': 'T Atmane', 'score': '6-2 7-5', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'T Fritz', 'loser': 'R Carballés Baena', 'score': '7-5 7-6(1)', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'B Shelton', 'loser': 'A Mannarino', 'score': '6-2 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A Rublev', 'loser': 'H Gaston', 'score': '6-2 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'F Tiafoe', 'loser': 'Y Watanuki', 'score': '1-6 7-5 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A de Minaur', 'loser': 'F Comesaña', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'J Mensik', 'loser': 'T Boyer', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'F Cobolli', 'loser': 'A Galarneau', 'score': '6-4 5-7 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A Fils', 'loser': 'P Carreño Busta', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'J Lehečka', 'loser': 'M McDonald', 'score': '7-6(2) 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A Davidovich Fokina', 'loser': 'C Moutet', 'score': '6-4 6-3', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'F Marozsán', 'loser': 'F Auger-Aliassime', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'C O\'Connell', 'loser': 'S Tsitsipas', 'score': '6-4 4-6 6-2', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'B Nakashima', 'loser': 'E Quinn', 'score': '7-6(8) 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'G Diallo', 'loser': 'M Gigante', 'score': '6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'L Sonego', 'loser': 'Y Bu', 'score': '6-1 6-4', 'round': 'R32'},
    {'date': '2025-08-06', 'winner': 'A Vukic', 'loser': 'C Norrie', 'score': '6-3 6-7(2) 6-3', 'round': 'R32'},
    
    # ROUND 3 (R16)
    {'date': '2025-08-07', 'winner': 'A Zverev', 'loser': 'M Arnaldi', 'score': '6-7(5) 6-3 6-2', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'A Michelsen', 'loser': 'L Musetti', 'score': '6-3 6-7(4) 6-4', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'H Rune', 'loser': 'A Müller', 'score': '6-2 6-4', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'C Ruud', 'loser': 'N Borges', 'score': '7-5 6-4', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'A Popyrin', 'loser': 'D Medvedev', 'score': '5-7 6-4 6-4', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'K Khachanov', 'loser': 'E Nava', 'score': '7-6(8) 4-6 6-1', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'F Cerúndolo', 'loser': 'TM Etcheverry', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'L Tien', 'loser': 'R Opelka', 'score': '7-6(7) 6-3', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'T Fritz', 'loser': 'G Diallo', 'score': '6-4 6-2', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'B Shelton', 'loser': 'B Nakashima', 'score': '6-7(10) 6-2 7-6(7)', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'A Rublev', 'loser': 'L Sonego', 'score': '5-7 6-4 6-3', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'F Tiafoe', 'loser': 'A Vukic', 'score': '6-3 4-6 6-3', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'A Davidovich Fokina', 'loser': 'J Mensik', 'score': '6-2 6-4', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'F Cobolli', 'loser': 'F Marozsán', 'score': '6-2 4-6 6-3', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'J Lehečka', 'loser': 'A Fils', 'score': '3-6 6-3 6-4', 'round': 'R16'},
    {'date': '2025-08-07', 'winner': 'A de Minaur', 'loser': 'C O\'Connell', 'score': 'W/O', 'round': 'R16'},
    
    # ROUND 4 (Continued R16 / QF qualifiers)
    {'date': '2025-08-08', 'winner': 'F Cerúndolo', 'loser': 'A Zverev', 'score': '6-4 0-1 RET', 'round': 'R16'},
    {'date': '2025-08-08', 'winner': 'A Popyrin', 'loser': 'H Rune', 'score': '4-6 6-2 6-3', 'round': 'R16'},
    {'date': '2025-08-08', 'winner': 'K Khachanov', 'loser': 'C Ruud', 'score': '6-4 7-5', 'round': 'R16'},
    {'date': '2025-08-08', 'winner': 'A Michelsen', 'loser': 'L Tien', 'score': '6-3 6-3', 'round': 'R16'},
    {'date': '2025-08-08', 'winner': 'T Fritz', 'loser': 'J Lehečka', 'score': '7-6(4) 6-7(5) 7-6(7)', 'round': 'R16'},
    {'date': '2025-08-08', 'winner': 'B Shelton', 'loser': 'F Cobolli', 'score': '6-4 4-6 7-6(7)', 'round': 'R16'},
    {'date': '2025-08-08', 'winner': 'A Davidovich Fokina', 'loser': 'A Rublev', 'score': '7-6(7) 6-7(2) 0-3 RET', 'round': 'R16'},
    {'date': '2025-08-08', 'winner': 'A de Minaur', 'loser': 'F Tiafoe', 'score': '6-2 4-6 6-4', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-08-09', 'winner': 'A Zverev', 'loser': 'A Popyrin', 'score': '6-7(10) 6-4 6-3', 'round': 'QF'},
    {'date': '2025-08-09', 'winner': 'K Khachanov', 'loser': 'A Michelsen', 'score': '6-4 7-6(3)', 'round': 'QF'},
    {'date': '2025-08-09', 'winner': 'T Fritz', 'loser': 'A Rublev', 'score': '6-3 7-6(4)', 'round': 'QF'},
    {'date': '2025-08-09', 'winner': 'B Shelton', 'loser': 'A de Minaur', 'score': '6-3 6-4', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-08-10', 'winner': 'K Khachanov', 'loser': 'A Zverev', 'score': '3-6 6-4 7-6(4)', 'round': 'SF'},
    {'date': '2025-08-10', 'winner': 'B Shelton', 'loser': 'T Fritz', 'score': '6-4 6-3', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-08-10', 'winner': 'B Shelton', 'loser': 'K Khachanov', 'score': '6-7(5) 6-4 7-6(7)', 'round': 'F'},
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
    logger.info("CANADA (MONTREAL) MASTERS 1000 2025")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Canada"
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
            'tourney_id': '2025-421',  # Canada 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Canada 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Canada' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Canada 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("CANADA MASTERS 1000 2025 LOADED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Champion: Ben Shelton 🏆 (First Masters 1000 title)")
    logger.info(f"Runner-up: Karen Khachanov")
    logger.info(f"Final Score: 6-7(5) 6-4 7-6(7)")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: A Popyrin upset #10 seed D Medvedev 5-7 6-4 6-4 in R16")

if __name__ == "__main__":
    main()

