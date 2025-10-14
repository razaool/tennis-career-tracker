"""
Convert scraped Tennis Abstract data to standard Tennis Abstract CSV format.

This script transforms the simplified scraped format into the full format
expected by parse_and_load_data.py
"""
import csv
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# Tournament dates and levels (manually curated)
TOURNAMENT_INFO = {
    'Brisbane': {'date': '20250101', 'level': 'A', 'draw': 32},
    'Auckland': {'date': '20250106', 'level': 'A', 'draw': 28},
    'Adelaide': {'date': '20250106', 'level': 'A', 'draw': 28},
    'Montpellier': {'date': '20250203', 'level': 'A', 'draw': 28},
    'Dallas': {'date': '20250203', 'level': 'A', 'draw': 32},
    'Rotterdam': {'date': '20250210', 'level': 'A', 'draw': 32},
    'Marseille': {'date': '20250217', 'level': 'A', 'draw': 28},
    'Doha': {'date': '20250217', 'level': 'A', 'draw': 32},
    'Dubai': {'date': '20250224', 'level': 'A', 'draw': 32},
    'Acapulco': {'date': '20250224', 'level': 'A', 'draw': 32},
    'Houston': {'date': '20250407', 'level': 'A', 'draw': 28},
    'Marrakech': {'date': '20250407', 'level': 'A', 'draw': 28},
    'Munich': {'date': '20250414', 'level': 'A', 'draw': 32},
    'Barcelona': {'date': '20250421', 'level': 'A', 'draw': 32},
    'Geneva': {'date': '20250519', 'level': 'A', 'draw': 28},
    'Stuttgart': {'date': '20250609', 'level': 'A', 'draw': 28},
    'Halle': {'date': '20250616', 'level': 'A', 'draw': 32},
    'Mallorca': {'date': '20250623', 'level': 'A', 'draw': 28},
    'Eastbourne': {'date': '20250623', 'level': 'A', 'draw': 28},
    'Bastad': {'date': '20250714', 'level': 'A', 'draw': 28},
    'Gstaad': {'date': '20250721', 'level': 'A', 'draw': 28},
    'Hamburg': {'date': '20250721', 'level': 'A', 'draw': 32},
    'Winston-Salem': {'date': '20250818', 'level': 'A', 'draw': 48},
    'Chengdu': {'date': '20250922', 'level': 'A', 'draw': 28},
    'Hangzhou': {'date': '20250922', 'level': 'A', 'draw': 28},
    'Beijing': {'date': '20250924', 'level': 'A', 'draw': 32},
    'Tokyo': {'date': '20250929', 'level': 'A', 'draw': 32},
}

def convert_scraped_to_ta_format(input_file, output_file):
    """
    Convert scraped format to Tennis Abstract format
    
    Args:
        input_file: Path to scraped CSV
        output_file: Path to output TA-format CSV
    """
    print(f"Converting {input_file} to Tennis Abstract format...")
    
    # Read scraped data
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        scraped_matches = list(reader)
    
    print(f"  Loaded {len(scraped_matches)} matches")
    
    # Convert to TA format
    ta_matches = []
    match_num = 1
    
    for match in scraped_matches:
        tournament_name = match['tournament_name']
        
        # Get tournament info
        if tournament_name not in TOURNAMENT_INFO:
            print(f"  Warning: Unknown tournament '{tournament_name}', skipping...")
            continue
        
        info = TOURNAMENT_INFO[tournament_name]
        
        # Create TA-format row
        ta_match = {
            'tourney_id': f"2025-{match_num:04d}",
            'tourney_name': tournament_name,
            'surface': match['surface'].capitalize(),
            'draw_size': info['draw'],
            'tourney_level': info['level'],
            'tourney_date': info['date'],
            'match_num': match_num,
            'winner_id': match.get('winner_id', ''),  # Will be created by parser
            'winner_seed': '',
            'winner_entry': '',
            'winner_name': match['winner_name'],
            'winner_hand': '',
            'winner_ht': '',
            'winner_ioc': '',
            'winner_age': '',
            'loser_id': match.get('loser_id', ''),
            'loser_seed': '',
            'loser_entry': '',
            'loser_name': match['loser_name'],
            'loser_hand': '',
            'loser_ht': '',
            'loser_ioc': '',
            'loser_age': '',
            'score': match['score'],
            'best_of': 3,  # All ATP 250/500 are best of 3
            'round': match['round'],
            'minutes': '',
            'w_ace': '',
            'w_df': '',
            'w_svpt': '',
            'w_1stIn': '',
            'w_1stWon': '',
            'w_2ndWon': '',
            'w_SvGms': '',
            'w_bpSaved': '',
            'w_bpFaced': '',
            'l_ace': '',
            'l_df': '',
            'l_svpt': '',
            'l_1stIn': '',
            'l_1stWon': '',
            'l_2ndWon': '',
            'l_SvGms': '',
            'l_bpSaved': '',
            'l_bpFaced': '',
            'winner_rank': '',
            'winner_rank_points': '',
            'loser_rank': '',
            'loser_rank_points': '',
        }
        
        ta_matches.append(ta_match)
        match_num += 1
    
    # Write TA format
    with open(output_file, 'w', newline='') as f:
        fieldnames = list(ta_matches[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ta_matches)
    
    print(f"  ✅ Converted {len(ta_matches)} matches")
    print(f"  Saved to: {output_file}")
    
    return len(ta_matches)


def main():
    """Main execution"""
    input_file = Path('/Users/razaool/tennis-career-tracker/data/raw/tennis_abstract_2025_scraped.csv')
    output_file = Path('/Users/razaool/tennis-career-tracker/data/raw/atp_matches_2025_converted.csv')
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return
    
    count = convert_scraped_to_ta_format(input_file, output_file)
    
    print("\n" + "=" * 80)
    print("✅ CONVERSION COMPLETE!")
    print("=" * 80)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Matches: {count}")
    print("\nNext step:")
    print(f"  python3 scripts/parse_and_load_data.py {output_file}")


if __name__ == "__main__":
    main()

