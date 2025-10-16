#!/usr/bin/env python3
"""
Load Monte Carlo Masters 1000 2025 matches into the database
"""
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Monte Carlo Masters 1000 2025 matches
# Dates: April 6-13, 2025
MATCHES = [
    # ROUND 1 (R64)
    {'date': '2025-04-06', 'winner': 'J Thompson', 'loser': 'G Mpetshi Perricard', 'score': '6-4 6-3', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'V Vacherot', 'loser': 'J-L Struff', 'score': '6-2 6-1', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'R Gasquet', 'loser': 'M Arnaldi', 'score': '6-3 4-6 6-4', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'D Medvedev', 'loser': 'K Khachanov', 'score': '7-5 4-6 6-4', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'A Davidovich Fokina', 'loser': 'B Shelton', 'score': '6-7(2) 6-2 6-1', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'L Musetti', 'loser': 'Y Bu', 'score': '4-6 7-5 6-3', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'D Altmaier', 'loser': 'F Auger-Aliassime', 'score': '7-6(5) 6-3', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'F Cerúndolo', 'loser': 'F Fognini', 'score': '6-0 6-3', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'A Müller', 'loser': 'C Ugo Carabelli', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'M Berrettini', 'loser': 'M Navone', 'score': '6-4 6-4', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'G Monfils', 'loser': 'F Marozsán', 'score': '4-6 6-1 6-1', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'M Giron', 'loser': 'D Shapovalov', 'score': '6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'J Lehečka', 'loser': 'S Korda', 'score': '6-3 7-6(7)', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'A Tabilo', 'loser': 'S Wawrinka', 'score': '1-6 7-5 7-5', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'N Borges', 'loser': 'H Rune', 'score': '6-2 3-0 RET', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'A Fils', 'loser': 'T Griekspoor', 'score': '6-7(3) 6-4 6-2', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'F Tiafoe', 'loser': 'M Kecmanović', 'score': '6-2 5-7 7-6(7)', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'G Dimitrov', 'loser': 'N Jarry', 'score': '6-3 6-4', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'T Machac', 'loser': 'S Báez', 'score': '3-6 6-3 6-2', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'TM Etcheverry', 'loser': 'C Moutet', 'score': '4-6 6-1 6-4', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'F Cobolli', 'loser': 'D Lajović', 'score': '6-4 6-2', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'R Bautista Agut', 'loser': 'B Nakashima', 'score': '6-2 6-4', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'P Martínez', 'loser': 'L Sonego', 'score': '6-4 1-6 6-2', 'round': 'R64'},
    {'date': '2025-04-06', 'winner': 'A Popyrin', 'loser': 'U Humbert', 'score': '6-3 6-7(7) 6-4', 'round': 'R64'},
    
    # ROUND 2 (R32)
    {'date': '2025-04-08', 'winner': 'M Berrettini', 'loser': 'A Zverev', 'score': '2-6 6-3 7-5', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'J Draper', 'loser': 'M Giron', 'score': '6-1 6-1', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'S Tsitsipas', 'loser': 'J Thompson', 'score': '4-6 6-4 6-2', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'C Alcaraz', 'loser': 'F Cerúndolo', 'score': '6-3 0-6 6-1', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'A Tabilo', 'loser': 'N Djokovic', 'score': '6-3 6-4', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'C Ruud', 'loser': 'R Bautista Agut', 'score': '6-2 6-1', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'A Rublev', 'loser': 'G Monfils', 'score': '6-4 7-6(2)', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'A de Minaur', 'loser': 'T Machac', 'score': '3-6 6-0 6-3', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'D Medvedev', 'loser': 'A Müller', 'score': '7-6(8) 5-7 6-2', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'A Fils', 'loser': 'F Cobolli', 'score': '6-2 6-4', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'L Musetti', 'loser': 'J Lehečka', 'score': '1-6 7-5 6-2', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'A Popyrin', 'loser': 'F Tiafoe', 'score': '3-6 6-3 6-3', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'G Dimitrov', 'loser': 'V Vacherot', 'score': '4-6 6-3 6-1', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'N Borges', 'loser': 'P Martínez', 'score': '7-5 6-7(4) 6-4', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'A Davidovich Fokina', 'loser': 'TM Etcheverry', 'score': '7-6(7) 6-3', 'round': 'R32'},
    {'date': '2025-04-08', 'winner': 'D Altmaier', 'loser': 'R Gasquet', 'score': '7-5 5-7 6-2', 'round': 'R32'},
    
    # ROUND 3 (R16)
    {'date': '2025-04-10', 'winner': 'C Alcaraz', 'loser': 'D Altmaier', 'score': '6-3 6-1', 'round': 'R16'},
    {'date': '2025-04-10', 'winner': 'A Popyrin', 'loser': 'C Ruud', 'score': '6-4 3-6 7-5', 'round': 'R16'},
    {'date': '2025-04-10', 'winner': 'A Davidovich Fokina', 'loser': 'J Draper', 'score': '6-3 7-6(8) 6-4', 'round': 'R16'},
    {'date': '2025-04-10', 'winner': 'S Tsitsipas', 'loser': 'N Borges', 'score': '6-1 6-1', 'round': 'R16'},
    {'date': '2025-04-10', 'winner': 'A Fils', 'loser': 'A Rublev', 'score': '6-2 6-3', 'round': 'R16'},
    {'date': '2025-04-10', 'winner': 'A de Minaur', 'loser': 'D Medvedev', 'score': '6-2 6-2', 'round': 'R16'},
    {'date': '2025-04-10', 'winner': 'L Musetti', 'loser': 'M Berrettini', 'score': '6-3 6-3', 'round': 'R16'},
    {'date': '2025-04-10', 'winner': 'G Dimitrov', 'loser': 'A Tabilo', 'score': '6-3 3-6 6-2', 'round': 'R16'},
    
    # QUARTERFINALS
    {'date': '2025-04-11', 'winner': 'C Alcaraz', 'loser': 'A Fils', 'score': '4-6 7-5 6-3', 'round': 'QF'},
    {'date': '2025-04-11', 'winner': 'L Musetti', 'loser': 'S Tsitsipas', 'score': '1-6 6-3 6-4', 'round': 'QF'},
    {'date': '2025-04-11', 'winner': 'A de Minaur', 'loser': 'G Dimitrov', 'score': '6-0 6-0', 'round': 'QF'},
    {'date': '2025-04-11', 'winner': 'A Davidovich Fokina', 'loser': 'A Popyrin', 'score': '6-3 6-2', 'round': 'QF'},
    
    # SEMIFINALS
    {'date': '2025-04-12', 'winner': 'C Alcaraz', 'loser': 'A Davidovich Fokina', 'score': '7-6(2) 6-4', 'round': 'SF'},
    {'date': '2025-04-12', 'winner': 'L Musetti', 'loser': 'A de Minaur', 'score': '1-6 6-4 7-6(7)', 'round': 'SF'},
    
    # FINAL
    {'date': '2025-04-13', 'winner': 'C Alcaraz', 'loser': 'L Musetti', 'score': '3-6 6-1 6-0', 'round': 'F'},
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
    logger.info("MONTE CARLO MASTERS 1000 2025")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # Tournament info
    tournament_name = "Monte Carlo"
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
            'tourney_id': '2025-410',  # Monte Carlo 2025 ID
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
    logger.info(f"\n✅ Inserted {inserted} matches from Monte Carlo 2025")
    
    # Verify
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM matches 
            WHERE tournament_name = 'Monte Carlo' 
            AND date >= '2025-01-01'
        """)
        result = cursor.fetchone()
        logger.info(f"✅ Verification: {result['count']} Monte Carlo 2025 matches in database")
    
    logger.info("\n" + "=" * 70)
    logger.info("MONTE CARLO MASTERS 1000 2025 LOADED SUCCESSFULLY")
    logger.info("=" * 70)
    logger.info(f"Champion: Carlos Alcaraz 🏆")
    logger.info(f"Runner-up: Lorenzo Musetti")
    logger.info(f"Final Score: 3-6 6-1 6-0")
    logger.info(f"Total matches: {len(MATCHES)}")
    logger.info(f"Notable: A Tabilo def. #3 seed N Djokovic 6-3 6-4 in R32")
    logger.info(f"         M Berrettini upset #1 seed A Zverev 2-6 6-3 7-5 in R32")

if __name__ == "__main__":
    main()

