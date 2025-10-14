#!/usr/bin/env python3
"""
Parse Wikipedia day-by-day summaries text format into match data
"""

import re
import csv
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def clean_player_name(name):
    """Remove country names, seeds, qualifiers, wildcards, etc."""
    # Remove country names (words before the actual name)
    # Common patterns: "United States Player Name", "China Player Name [5]"
    
    # Remove everything in brackets first
    name = re.sub(r'\[.*?\]', '', name).strip()
    
    # List of countries/regions to remove (partial list)
    countries = [
        'United States', 'United Kingdom', 'Australia', 'China', 'Japan', 'Spain', 
        'France', 'Germany', 'Italy', 'Serbia', 'Poland', 'Kazakhstan', 'Brazil',
        'Argentina', 'Chile', 'Canada', 'Croatia', 'Czech Republic', 'Denmark',
        'Norway', 'Sweden', 'Switzerland', 'Netherlands', 'Belgium', 'Portugal',
        'Greece', 'Bulgaria', 'Ukraine', 'Romania', 'Slovakia', 'Finland',
        'Austria', 'Hungary', 'Bosnia and Herzegovina', 'Thailand', 'India',
        'Mexico', 'Tunisia', 'Morocco', 'Latvia', 'Chinese Taipei', 'Monaco',
        'New Zealand', 'Uruguay', 'El Salvador', 'Turkey', 'Cyprus', 'Israel',
        'Colombia', 'Ecuador', 'Peru', 'Venezuela', 'South Africa', 'Egypt',
        'Algeria', 'Zimbabwe', 'Kenya', 'Nigeria', 'Ghana', 'Cameroon',
        'Senegal', 'Ivory Coast', 'Mali', 'Burkina Faso', 'Niger', 'Chad',
        'Russia', 'Belarus', 'Georgia', 'Armenia', 'Azerbaijan', 'Uzbekistan',
        'Tajikistan', 'Kyrgyzstan', 'Turkmenistan', 'Mongolia', 'North Korea',
        'South Korea', 'Taiwan', 'Hong Kong', 'Macau', 'Singapore', 'Malaysia',
        'Indonesia', 'Philippines', 'Vietnam', 'Cambodia', 'Laos', 'Myanmar',
        'Bangladesh', 'Pakistan', 'Sri Lanka', 'Nepal', 'Bhutan', 'Maldives',
        'Afghanistan', 'Iran', 'Iraq', 'Syria', 'Lebanon', 'Jordan', 'Palestine',
        'Saudi Arabia', 'Yemen', 'Oman', 'UAE', 'Kuwait', 'Bahrain', 'Qatar'
    ]
    
    # Try to remove country prefix
    for country in countries:
        if name.startswith(country + ' '):
            name = name[len(country):].strip()
            break
    
    # Remove any remaining special markers
    name = name.replace('[WC]', '').replace('[Q]', '').replace('[PR]', '').replace('[LL]', '')
    name = name.strip()
    
    return name


def parse_round(round_text):
    """Convert round text to standard format"""
    round_text = round_text.lower().strip()
    
    # Remove any bracketed annotations like [a], [b]
    round_text = re.sub(r'\[.*?\]', '', round_text).strip()
    
    round_map = {
        '1st round': 'R128',
        '2nd round': 'R64',
        '3rd round': 'R32',
        '4th round': 'R16',
        'quarterfinals': 'QF',
        'semifinals': 'SF',
        'final': 'F'
    }
    
    return round_map.get(round_text, round_text)


def parse_score(score_text):
    """Clean up score text"""
    # Remove 'retired' text
    score_text = re.sub(r'\s+retired$', ' RET', score_text, flags=re.IGNORECASE)
    return score_text.strip()


def parse_wikipedia_text(text, tournament_name, year=2025, default_date=None):
    """
    Parse Wikipedia day-by-day summary text into match records
    
    Args:
        text: Raw text from Wikipedia
        tournament_name: Name of the tournament
        year: Year of the tournament
        default_date: Default date for matches before first "Day X" header (format: YYYY-MM-DD)
    
    Returns:
        List of match dictionaries
    """
    matches = []
    
    # Split into lines
    lines = text.split('\n')
    
    current_date = default_date
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Try to extract date from "Day X (DD Month)" pattern
        date_match = re.search(r'Day \d+ \((\d+) (\w+)\)', line)
        if date_match:
            day = date_match.group(1)
            month = date_match.group(2)
            # Convert month name to number
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            month_num = month_map.get(month, 1)
            current_date = f"{year}-{month_num:02d}-{int(day):02d}"
            logger.info(f"Processing {current_date}")
            continue
        
        # Look for match lines with the pattern: Event\tWinner\tLoser\tScore
        # Men's singles lines
        if line.startswith("Men's singles"):
            # Extract round, winner, loser, score
            # Pattern: Men's singles ROUND\tWINNER\tLOSER\tSCORE
            parts = line.split('\t')
            
            if len(parts) >= 4:
                event_round = parts[0]  # "Men's singles 1st Round"
                winner_text = parts[1]
                loser_text = parts[2]
                score_text = parts[3]
                
                # Extract round from event
                round_match = re.search(r"Men's singles\s+(.+)", event_round)
                if round_match:
                    round_text = round_match.group(1)
                    round_code = parse_round(round_text)
                    
                    # Clean player names
                    winner = clean_player_name(winner_text)
                    loser = clean_player_name(loser_text)
                    score = parse_score(score_text)
                    
                    # Skip if postponed or vs. pattern (incomplete match)
                    if 'Postponed' in score_text or 'vs.' in loser_text:
                        continue
                    
                    # Skip if we don't have proper player names
                    if not winner or not loser or len(winner) < 3 or len(loser) < 3:
                        continue
                    
                    match = {
                        'date': current_date,
                        'tournament_name': tournament_name,
                        'round': round_code,
                        'winner_name': winner,
                        'loser_name': loser,
                        'score': score
                    }
                    
                    matches.append(match)
                    logger.debug(f"  {round_code}: {winner} def. {loser} {score}")
    
    return matches


def save_to_csv(matches, output_file):
    """Save matches to CSV file"""
    if not matches:
        logger.warning("No matches to save!")
        return
    
    fieldnames = ['date', 'tournament_name', 'round', 'winner_name', 'loser_name', 'score']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matches)
    
    logger.info(f"✅ Saved {len(matches)} matches to {output_file}")


def main():
    """Main function to parse text file"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python parse_wikipedia_text.py <input_text_file> <tournament_name> <output_csv> [default_date]")
        print("Example: python parse_wikipedia_text.py ao2025.txt 'Australian Open' ao2025_parsed.csv 2025-01-12")
        sys.exit(1)
    
    input_file = sys.argv[1]
    tournament_name = sys.argv[2]
    output_file = sys.argv[3]
    default_date = sys.argv[4] if len(sys.argv) > 4 else None
    
    logger.info(f"Reading from {input_file}")
    if default_date:
        logger.info(f"Using default date: {default_date}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    matches = parse_wikipedia_text(text, tournament_name, default_date=default_date)
    
    logger.info(f"Parsed {len(matches)} matches")
    
    if matches:
        save_to_csv(matches, output_file)
        
        # Show summary by round
        from collections import Counter
        round_counts = Counter(m['round'] for m in matches)
        logger.info("\nMatches by round:")
        for round_code in ['R128', 'R64', 'R32', 'R16', 'QF', 'SF', 'F']:
            if round_code in round_counts:
                logger.info(f"  {round_code}: {round_counts[round_code]} matches")


if __name__ == '__main__':
    main()

