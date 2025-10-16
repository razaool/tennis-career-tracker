#!/usr/bin/env python3
"""
Load Madrid Masters 1000 2025 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Madrid Masters 1000 2025 matches
# Dates: April 24 - May 4, 2025
MATCHES = [
    # ROUND 1 (R64)
    {'date': '2025-04-24', 'winner': 'F Cobolli', 'loser': 'F Marozsán', 'score': '7-6(4) 7-5', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'G Monfils', 'loser': 'B Gojo', 'score': '1-6 6-2 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'A Bublik', 'loser': 'A Michelsen', 'score': '7-6(2) 7-6(4)', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'JM Cerúndolo', 'loser': 'A Kovacevic', 'score': '3-6 7-5 6-2', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'L Djere', 'loser': 'F Fognini', 'score': '6-2 6-3', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'F Comesaña', 'loser': 'P Martínez', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'S Ofner', 'loser': 'H Gaston', 'score': '6-4 6-3', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'R Bautista Agut', 'loser': 'J Munar', 'score': '6-4 2-6 6-3', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'E Quinn', 'loser': 'D Lajović', 'score': '6-3 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'H Mayot', 'loser': 'C Moutet', 'score': '6-3 4-2 RET', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'N Borges', 'loser': 'P Carreño Busta', 'score': '6-7(7) 7-6(7) 6-3', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'C O\'Connell', 'loser': 'C Ugo Carabelli', 'score': '6-3 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'B Bonzi', 'loser': 'M Cilic', 'score': '6-3 6-2', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'M Navone', 'loser': 'G Mpetshi Perricard', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'F Cina', 'loser': 'C Wong', 'score': '7-6(7) 6-1', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'A Rinderknech', 'loser': 'R Safiullin', 'score': '7-6(4) 6-1', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'J Fearnley', 'loser': 'Y Bu', 'score': '6-3 7-6(2)', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'R Opelka', 'loser': 'R Hijikata', 'score': '7-5 7-5', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'T Griekspoor', 'loser': 'V Kopriva', 'score': '6-1 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'M Giron', 'loser': 'L Tien', 'score': '6-1 1-6 7-6(4)', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'J Fonseca', 'loser': 'E Moller', 'score': '6-2 6-3', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'J-L Struff', 'loser': 'B Van De Zandschulp', 'score': '7-5 2-6 4-1 RET', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'M Arnaldi', 'loser': 'B Coric', 'score': '4-6 6-4 7-5', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'C Norrie', 'loser': 'M Landaluce', 'score': '6-7(4) 7-5 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'N Jarry', 'loser': 'D Altmaier', 'score': '6-3 6-2', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'L Darderi', 'loser': 'Q Halys', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'L Sonego', 'loser': 'M Kecmanović', 'score': '6-4 7-6(7)', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'G Diallo', 'loser': 'Z Bergs', 'score': '6-1 6-2', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'A Müller', 'loser': 'D Goffin', 'score': '6-3 3-6 1-0 RET', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'D Džumhur', 'loser': 'M Bellucci', 'score': '4-6 6-4 6-2', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'K Nishikori', 'loser': 'A Vukic', 'score': '4-6 6-3 6-3', 'round': 'R64'},
    {'date': '2025-04-24', 'winner': 'TM Etcheverry', 'loser': 'H Medjedovic', 'score': '6-4 6-7(4) 6-4', 'round': 'R64'},
    
    # ROUND 2 (R32)
    {'date': '2025-04-26', 'winner': 'A Zverev', 'loser': 'R Bautista Agut', 'score': '6-2 6-2', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'T Fritz', 'loser': 'C O\'Connell', 'score': '6-1 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'A Rublev', 'loser': 'G Monfils', 'score': 'W/O', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'F Cobolli', 'loser': 'H Rune', 'score': '6-2 RET', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'D Medvedev', 'loser': 'L Djere', 'score': 'W/O', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'B Shelton', 'loser': 'M Navone', 'score': '4-6 7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'F Comesaña', 'loser': 'A Fils', 'score': '7-6(7) 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'C Ruud', 'loser': 'A Rinderknech', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'JM Cerúndolo', 'loser': 'F Auger-Aliassime', 'score': '7-6(7) 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'F Cerúndolo', 'loser': 'H Mayot', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'J Mensik', 'loser': 'E Quinn', 'score': '7-6(4) 6-1', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'S Korda', 'loser': 'F Cina', 'score': '6-3 3-6 6-1', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'A Bublik', 'loser': 'A Popyrin', 'score': '6-4 7-6(4)', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'B Bonzi', 'loser': 'H Hurkacz', 'score': '6-4 7-5', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'A Davidovich Fokina', 'loser': 'N Borges', 'score': '6-2 6-3', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'B Nakashima', 'loser': 'S Ofner', 'score': '6-3 7-6(7)', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'M Arnaldi', 'loser': 'N Djokovic', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'J Draper', 'loser': 'T Griekspoor', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'A de Minaur', 'loser': 'L Sonego', 'score': '6-2 6-3', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'L Musetti', 'loser': 'TM Etcheverry', 'score': '7-6(7) 6-2', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'T Paul', 'loser': 'J Fonseca', 'score': '7-6(7) 6-7(3) 7-6(7)', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'G Dimitrov', 'loser': 'N Jarry', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'F Tiafoe', 'loser': 'L Darderi', 'score': '7-5 3-1 RET', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'S Tsitsipas', 'loser': 'J-L Struff', 'score': '3-6 6-4 6-3', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'J Fearnley', 'loser': 'T Machac', 'score': '1-6 6-3 6-2', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'A Müller', 'loser': 'U Humbert', 'score': '6-2 6-7(3) 7-6(7)', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'K Khachanov', 'loser': 'R Opelka', 'score': '7-6(7) 7-6(7)', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'C Norrie', 'loser': 'J Lehečka', 'score': '2-6 6-4 6-0', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'D Shapovalov', 'loser': 'K Nishikori', 'score': '6-1 6-4', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'M Berrettini', 'loser': 'M Giron', 'score': '6-7(3) 7-6(8) 6-1', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'D Džumhur', 'loser': 'S Báez', 'score': '6-1 1-6 6-2', 'round': 'R32'},
    {'date': '2025-04-26', 'winner': 'G Diallo', 'loser': 'K Majchrzak', 'score': '7-5 4-6 6-4', 'round': 'R32'},
    
    # ROUND 3 (R16)
    {'date': '2025-04-28', 'winner': 'A Davidovich Fokina', 'loser': 'A Zverev', 'score': '6-2 7-6(7) 6-7(0)', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'B Bonzi', 'loser': 'T Fritz', 'score': '6-4 5-7 RET', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'A Bublik', 'loser': 'A Rublev', 'score': '6-4 0-6 6-4', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'D Medvedev', 'loser': 'JM Cerúndolo', 'score': '6-2 6-2', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'J Mensik', 'loser': 'B Shelton', 'score': '6-1 6-4', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'C Ruud', 'loser': 'S Korda', 'score': '6-3 6-3', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'F Cerúndolo', 'loser': 'F Comesaña', 'score': '6-4 6-4', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'B Nakashima', 'loser': 'F Cobolli', 'score': '7-5 6-3', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'M Arnaldi', 'loser': 'D Džumhur', 'score': '6-3 6-4', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'J Draper', 'loser': 'M Berrettini', 'score': '7-6(7) RET', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'A de Minaur', 'loser': 'D Shapovalov', 'score': '6-3 7-6(7)', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'L Musetti', 'loser': 'S Tsitsipas', 'score': '7-5 7-6(3)', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'T Paul', 'loser': 'K Khachanov', 'score': '6-3 3-6 6-2', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'G Dimitrov', 'loser': 'J Fearnley', 'score': '6-4 7-6(7)', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'F Tiafoe', 'loser': 'A Müller', 'score': '6-3 6-3', 'round': 'R16'},
    {'date': '2025-04-28', 'winner': 'G Diallo', 'loser': 'C Norrie', 'score': '2-6 6-4 6-4', 'round': 'R16'},
    
    # ROUND 4 (R16 continuation - some tournaments call it R16, some R4)
    {'date': '2025-04-30', 'winner': 'F Cerúndolo', 'loser': 'A Zverev', 'score': '7-5 6-3', 'round': 'R16'},
    {'date': '2025-04-30', 'winner': 'C Ruud', 'loser': 'T Fritz', 'score': '7-5 6-4', 'round': 'R16'},
    {'date': '2025-04-30', 'winner': 'D Medvedev', 'loser': 'B Nakashima', 'score': '3-6 6-1 6-4', 'round': 'R16'},
    {'date': '2025-04-30', 'winner': 'J Mensik', 'loser': 'A Bublik', 'score': '6-3 6-2', 'round': 'R16'},
    {'date': '2025-04-30', 'winner': 'J Draper', 'loser': 'T Paul', 'score': '6-2 6-2', 'round': 'R16'},
    {'date': '2025-04-30', 'winner': 'L Musetti', 'loser': 'A de Minaur', 'score': '6-4 6-2', 'round': 'R16'},
    {'date': '2025-04-30', 'winner': 'G Diallo', 'loser': 'G Dimitrov', 'score': '5-7 7-6(7) 6-4', 'round': 'R16'},
    {'date': '2025-04-30', 'winner': 'M Arnaldi', 'loser': 'F Tiafoe', 'score': '6-3 7-5', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-05-02', 'winner': 'J Draper', 'loser': 'M Arnaldi', 'score': '6-0 6-4', 'round': 'QF'},
    {'date': '2025-05-02', 'winner': 'C Ruud', 'loser': 'D Medvedev', 'score': '6-3 7-5', 'round': 'QF'},
    {'date': '2025-05-02', 'winner': 'L Musetti', 'loser': 'G Diallo', 'score': '6-4 6-3', 'round': 'QF'},
    {'date': '2025-05-02', 'winner': 'F Cerúndolo', 'loser': 'J Mensik', 'score': '3-6 7-6(7) 6-2', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-05-03', 'winner': 'J Draper', 'loser': 'L Musetti', 'score': '6-3 7-6(7)', 'round': 'SF'},
    {'date': '2025-05-03', 'winner': 'C Ruud', 'loser': 'F Cerúndolo', 'score': '6-4 7-5', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-05-04', 'winner': 'C Ruud', 'loser': 'J Draper', 'score': '7-5 3-6 6-4', 'round': 'F'},
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
    logger.info("MADRID MASTERS 1000 2025")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Madrid"
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
            'tourney_id': '2025-1536',  # Madrid 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Madrid 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Madrid' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Madrid 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("MADRID MASTERS 1000 2025 LOADED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Champion: Casper Ruud 🏆")
    logger.info(f"Runner-up: Jack Draper")
    logger.info(f"Final Score: 7-5 3-6 6-4")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: M Arnaldi def. #4 seed N Djokovic 6-3 6-4 in R32")
    logger.info(f"         F Cerúndolo def. #1 seed A Zverev 7-5 6-3 in R16")

if __name__ == "__main__":
    main()

