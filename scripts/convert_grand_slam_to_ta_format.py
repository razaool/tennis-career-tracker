"""
Convert Grand Slam Wikipedia parsed data to Tennis Abstract format.

This script transforms the Wikipedia parsed format (date, tournament, round, winner, loser, score)
into the full Tennis Abstract format expected by parse_and_load_data.py
"""
import csv
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# Grand Slam tournament info
GRAND_SLAM_INFO = {
    'Australian Open': {
        'surface': 'Hard',
        'draw': 128,
        'level': 'G',
        'best_of': 5,
    },
    'French Open': {
        'surface': 'Clay',
        'draw': 128,
        'level': 'G',
        'best_of': 5,
    },
    'Wimbledon': {
        'surface': 'Grass',
        'draw': 128,
        'level': 'G',
        'best_of': 5,
    },
    'US Open': {
        'surface': 'Hard',
        'draw': 128,
        'level': 'G',
        'best_of': 5,
    },
}


def convert_grand_slam_to_ta_format(input_file, output_file):
    """
    Convert Wikipedia parsed format to Tennis Abstract format
    
    Args:
        input_file: Path to parsed CSV (date, tournament, round, winner, loser, score)
        output_file: Path to output TA-format CSV
    """
    print(f"Converting {input_file} to Tennis Abstract format...")
    
    # Read parsed data
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        parsed_matches = list(reader)
    
    print(f"  Loaded {len(parsed_matches)} matches")
    
    # Convert to TA format
    ta_matches = []
    match_num = 1
    
    for match in parsed_matches:
        tournament_name = match['tournament_name']
        
        # Get tournament info
        if tournament_name not in GRAND_SLAM_INFO:
            print(f"  Warning: Unknown tournament '{tournament_name}', skipping...")
            continue
        
        info = GRAND_SLAM_INFO[tournament_name]
        
        # Convert date from YYYY-MM-DD to YYYYMMDD
        date_obj = datetime.strptime(match['date'], '%Y-%m-%d')
        tourney_date = date_obj.strftime('%Y%m%d')
        
        # Create TA-format row
        ta_match = {
            'tourney_id': f"2025-{tournament_name.replace(' ', '-').lower()}-{match_num:04d}",
            'tourney_name': tournament_name,
            'surface': info['surface'],
            'draw_size': info['draw'],
            'tourney_level': info['level'],
            'tourney_date': tourney_date,
            'match_num': match_num,
            'winner_id': '',  # Will be created by parser
            'winner_seed': '',
            'winner_entry': '',
            'winner_name': match['winner_name'],
            'winner_hand': '',
            'winner_ht': '',
            'winner_ioc': '',
            'winner_age': '',
            'loser_id': '',
            'loser_seed': '',
            'loser_entry': '',
            'loser_name': match['loser_name'],
            'loser_hand': '',
            'loser_ht': '',
            'loser_ioc': '',
            'loser_age': '',
            'score': match['score'],
            'best_of': info['best_of'],
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
    if ta_matches:
        with open(output_file, 'w', newline='') as f:
            fieldnames = list(ta_matches[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ta_matches)
        
        print(f"  ✅ Converted {len(ta_matches)} matches")
        print(f"  Saved to: {output_file}")
    else:
        print("  ⚠️  No matches to convert!")
    
    return len(ta_matches)


def main():
    """Main execution"""
    if len(sys.argv) != 3:
        print("Usage: python3 convert_grand_slam_to_ta_format.py <input_csv> <output_csv>")
        print("\nExample:")
        print("  python3 convert_grand_slam_to_ta_format.py data/raw/ao2025_parsed.csv data/raw/atp_matches_ao2025_converted.csv")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    count = convert_grand_slam_to_ta_format(input_file, output_file)
    
    print("\n" + "=" * 80)
    print("✅ CONVERSION COMPLETE!")
    print("=" * 80)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Matches: {count}")


if __name__ == "__main__":
    main()

