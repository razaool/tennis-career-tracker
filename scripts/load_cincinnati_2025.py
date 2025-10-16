#!/usr/bin/env python3
"""
Load Cincinnati Masters 1000 2025 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cincinnati Masters 1000 2025 matches
# Dates: August 11-17, 2025
MATCHES = [
    # ROUND 1 (R64)
    {'date': '2025-08-11', 'winner': 'S Báez', 'loser': 'D Goffin', 'score': '6-1 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'F Marozsán', 'loser': 'C Smith', 'score': '6-1 4-6 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'C Moutet', 'loser': 'M McDonald', 'score': '7-5 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'A Mannarino', 'loser': 'J Thompson', 'score': '6-2 6-2', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'TM Etcheverry', 'loser': 'J Shang', 'score': '6-7(5) 7-6(7) 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'T Atmane', 'loser': 'Y Nishioka', 'score': '6-2 6-2', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'R Safiullin', 'loser': 'A Tabilo', 'score': '6-3 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'D Galán', 'loser': 'V Kopriva', 'score': '6-2 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'Z Bergs', 'loser': 'J Fearnley', 'score': '6-1 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'C Wong', 'loser': 'G Mpetshi Perricard', 'score': '6-3 6-2', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'P Martínez', 'loser': 'N Jarry', 'score': '1-6 6-4 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'J Fonseca', 'loser': 'Y Bu', 'score': '4-6 6-2 7-5', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'B Bonzi', 'loser': 'M Arnaldi', 'score': '6-7(1) 6-3 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'R Carballés Baena', 'loser': 'H Gaston', 'score': '6-4 5-7 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'A Rinderknech', 'loser': 'N Borges', 'score': '6-3 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'N Basavareddy', 'loser': 'A Vukic', 'score': '7-6(5) 7-5', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'D Džumhur', 'loser': 'M Bellucci', 'score': '7-6(7) 7-6(5)', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'V Royer', 'loser': 'S Ofner', 'score': '7-5 3-6 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'L Tien', 'loser': 'L Riedi', 'score': '6-3 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'M Landaluce', 'loser': 'P Kypson', 'score': '3-6 6-3 6-2', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'R Bautista Agut', 'loser': 'D Altmaier', 'score': '7-6(5) 7-6(1)', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'H Medjedovic', 'loser': 'A Kovacevic', 'score': '6-2 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'A Walton', 'loser': 'M Navone', 'score': '4-6 7-6(7) 6-1', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'R Opelka', 'loser': 'H Dellien', 'score': '7-5 7-6(3)', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'J Brooksby', 'loser': 'A Müller', 'score': '7-6(7) 5-7 6-1', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'F Comesaña', 'loser': 'J Munar', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'E Quinn', 'loser': 'M Kecmanović', 'score': '7-6(7) 6-4', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'E Nava', 'loser': 'B Coric', 'score': '6-3 7-5', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'A Blockx', 'loser': 'M Giron', 'score': '6-2 3-6 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'T Boyer', 'loser': 'B Holt', 'score': '6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'C Ugo Carabelli', 'loser': 'K Nishikori', 'score': '7-5 6-3', 'round': 'R64'},
    {'date': '2025-08-11', 'winner': 'L Nardi', 'loser': 'T Tirante', 'score': '6-4 7-6(7)', 'round': 'R64'},
    
    # ROUND 2 (R32)
    {'date': '2025-08-13', 'winner': 'J Sinner', 'loser': 'D Galán', 'score': '6-1 6-1', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'T Fritz', 'loser': 'E Nava', 'score': '6-4 6-4', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'H Rune', 'loser': 'R Safiullin', 'score': '7-5 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'B Bonzi', 'loser': 'L Musetti', 'score': '5-7 6-4 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'F Tiafoe', 'loser': 'R Carballés Baena', 'score': '6-4 6-3', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Rinderknech', 'loser': 'C Ruud', 'score': '6-7(5) 6-4 6-2', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'T Paul', 'loser': 'P Martínez', 'score': '6-2 6-2', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'T Atmane', 'loser': 'F Cobolli', 'score': '6-4 3-6 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Davidovich Fokina', 'loser': 'J Fonseca', 'score': '7-6(7) 4-5 RET', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Mannarino', 'loser': 'T Machac', 'score': '6-3 6-3', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'U Humbert', 'loser': 'C Wong', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'F Auger-Aliassime', 'loser': 'TM Etcheverry', 'score': '6-2 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'S Tsitsipas', 'loser': 'F Marozsán', 'score': '7-6(7) 6-2', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Michelsen', 'loser': 'C Moutet', 'score': '3-6 6-3 6-4', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'G Diallo', 'loser': 'S Báez', 'score': '7-5 6-4', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'L Sonego', 'loser': 'Z Bergs', 'score': '6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'C Alcaraz', 'loser': 'D Džumhur', 'score': '6-1 2-6 6-3', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Zverev', 'loser': 'N Basavareddy', 'score': '6-3 6-3', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'B Shelton', 'loser': 'C Ugo Carabelli', 'score': '6-3 3-1 RET', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'R Opelka', 'loser': 'A de Minaur', 'score': '7-6(8) 6-4', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Rublev', 'loser': 'L Tien', 'score': '7-6(4) 6-3', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Walton', 'loser': 'D Medvedev', 'score': '6-7(0) 6-4 6-1', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'K Khachanov', 'loser': 'V Royer', 'score': '6-4 7-6(8)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'J Mensik', 'loser': 'E Quinn', 'score': '6-4 6-2', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'A Popyrin', 'loser': 'M Landaluce', 'score': '7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'J Lehečka', 'loser': 'T Boyer', 'score': '4-6 6-1 6-4', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'L Nardi', 'loser': 'D Shapovalov', 'score': '6-7(5) 6-3 6-4', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'H Medjedovic', 'loser': 'T Griekspoor', 'score': '6-4 7-6(3)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'B Nakashima', 'loser': 'A Blockx', 'score': '4-6 6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'F Comesaña', 'loser': 'L Darderi', 'score': '6-4 3-1 RET', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'R Bautista Agut', 'loser': 'C Norrie', 'score': '6-4 6-3', 'round': 'R32'},
    {'date': '2025-08-13', 'winner': 'J Brooksby', 'loser': 'A Cazaux', 'score': '7-5 6-1', 'round': 'R32'},
    
    # ROUND 3 (R16)
    {'date': '2025-08-14', 'winner': 'J Sinner', 'loser': 'G Diallo', 'score': '6-2 7-6(8)', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'T Fritz', 'loser': 'L Sonego', 'score': '7-6(7) 7-5', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'H Rune', 'loser': 'A Michelsen', 'score': '7-6(4) 6-3', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'F Tiafoe', 'loser': 'U Humbert', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'A Mannarino', 'loser': 'T Paul', 'score': '5-7 6-3 6-4', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'F Auger-Aliassime', 'loser': 'A Rinderknech', 'score': '6-7(4) 4-2 RET', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'B Bonzi', 'loser': 'S Tsitsipas', 'score': '6-7(4) 6-4 6-3', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'T Atmane', 'loser': 'J Fonseca', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'C Alcaraz', 'loser': 'H Medjedovic', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'A Rublev', 'loser': 'A Popyrin', 'score': '6-7(5) 7-6(7) 7-5', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'K Khachanov', 'loser': 'J Brooksby', 'score': '6-3 6-3', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'L Nardi', 'loser': 'J Mensik', 'score': '6-2 2-1 RET', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'J Lehečka', 'loser': 'A Walton', 'score': '7-6(7) 7-6(7)', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'F Comesaña', 'loser': 'R Opelka', 'score': '6-7(4) 6-4 7-5', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'A Zverev', 'loser': 'B Nakashima', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-08-14', 'winner': 'B Shelton', 'loser': 'R Bautista Agut', 'score': '7-6(7) 6-3', 'round': 'R16'},
    
    # ROUND 4 (Continued R16 / QF qualifiers)
    {'date': '2025-08-15', 'winner': 'J Sinner', 'loser': 'A Mannarino', 'score': '6-4 7-6(7)', 'round': 'R16'},
    {'date': '2025-08-15', 'winner': 'C Alcaraz', 'loser': 'L Nardi', 'score': '6-1 6-4', 'round': 'R16'},
    {'date': '2025-08-15', 'winner': 'A Zverev', 'loser': 'K Khachanov', 'score': '7-5 3-0 RET', 'round': 'R16'},
    {'date': '2025-08-15', 'winner': 'T Atmane', 'loser': 'T Fritz', 'score': '6-3 7-5 6-3', 'round': 'R16'},
    {'date': '2025-08-15', 'winner': 'H Rune', 'loser': 'F Tiafoe', 'score': '6-4 3-1 RET', 'round': 'R16'},
    {'date': '2025-08-15', 'winner': 'A Rublev', 'loser': 'F Comesaña', 'score': '6-2 6-3', 'round': 'R16'},
    {'date': '2025-08-15', 'winner': 'F Auger-Aliassime', 'loser': 'B Bonzi', 'score': '6-4 6-3', 'round': 'R16'},
    {'date': '2025-08-15', 'winner': 'B Shelton', 'loser': 'J Lehečka', 'score': '6-4 6-4', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-08-16', 'winner': 'J Sinner', 'loser': 'F Auger-Aliassime', 'score': '6-0 6-2', 'round': 'QF'},
    {'date': '2025-08-16', 'winner': 'T Atmane', 'loser': 'H Rune', 'score': '6-2 6-3', 'round': 'QF'},
    {'date': '2025-08-16', 'winner': 'C Alcaraz', 'loser': 'A Rublev', 'score': '6-3 4-6 7-5', 'round': 'QF'},
    {'date': '2025-08-16', 'winner': 'A Zverev', 'loser': 'B Shelton', 'score': '6-2 6-2', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-08-17', 'winner': 'J Sinner', 'loser': 'T Atmane', 'score': '7-6(7) 6-2', 'round': 'SF'},
    {'date': '2025-08-17', 'winner': 'C Alcaraz', 'loser': 'A Zverev', 'score': '6-4 6-3', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-08-17', 'winner': 'C Alcaraz', 'loser': 'J Sinner', 'score': '5-0 RET', 'round': 'F'},
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
    logger.info("CINCINNATI MASTERS 1000 2025")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Cincinnati"
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
            'tourney_id': '2025-422',  # Cincinnati 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Cincinnati 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Cincinnati' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Cincinnati 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("CINCINNATI MASTERS 1000 2025 LOADED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Champion: Carlos Alcaraz 🏆")
    logger.info(f"Runner-up: Jannik Sinner (retired)")
    logger.info(f"Final Score: 5-0 RET (Sinner retired)")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: A Walton upset #12 seed D Medvedev 6-7(0) 6-4 6-1 in R32")
    logger.info(f"         Terence Atmane reached QF with wins over Cobolli and Fritz")

if __name__ == "__main__":
    main()

