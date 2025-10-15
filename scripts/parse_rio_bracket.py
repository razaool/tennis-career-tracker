#!/usr/bin/env python3
"""
Parse Rio ATP 500 bracket format into Tennis Abstract CSV format

Bracket format shows matches in a tree structure:
- First round: player pairs in consecutive lines
- Later rounds: winners shown on the right side
"""

import csv
import re
import sys
from pathlib import Path

def clean_player_name(raw_text):
    """Extract just the player's last name and first initial"""
    # Remove qualifiers and seeds
    text = re.sub(r'^\s*\d+\s+', '', raw_text)  # Remove seed number
    text = re.sub(r'^\s*(WC|Q|SE|LL)\s+', '', text)  # Remove qualifiers
    
    # List of countries to remove
    countries = [
        'Argentina', 'Brazil', 'Chile', 'China', 'Chinese Taipei', 'Bolivia',
        'France', 'Germany', 'Italy', 'Kazakhstan', 'Spain', 'Serbia',
        'Bosnia and Herzegovina', 'Portugal', 'United States', 'Canada',
        'Australia', 'United Kingdom', 'Netherlands', 'Belgium', 'Switzerland',
        'Austria', 'Poland', 'Czech Republic', 'Croatia', 'Denmark', 'Norway',
        'Sweden', 'Finland', 'Greece', 'Bulgaria', 'Romania', 'Slovakia',
        'Hungary', 'Latvia', 'Lithuania', 'Estonia', 'Slovenia', 'Montenegro',
        'North Macedonia', 'Albania', 'Moldova', 'Ukraine', 'Russia', 'Belarus'
    ]
    
    # Remove country prefix
    for country in countries:
        if text.startswith(country + ' '):
            text = text[len(country):].strip()
            break
    
    return text.strip()

def parse_score_format(score_str):
    """
    Convert compact score format to standard tennis format
    
    Examples:
    - "77 6" -> "7-6(7) 6-?"
    - "6 3 4" -> "6-? 3-? 4-?" (need opponent's scores)
    """
    parts = score_str.strip().split()
    formatted = []
    
    for part in parts:
        # Handle retirement
        if 'r' in part.lower():
            return 'RET'
        
        # Two-digit scores
        if len(part) == 2:
            first = part[0]
            second = part[1]
            
            # Tiebreak detection
            if first == '7' and second in '123456789':
                formatted.append(f"7-6({second})")
            elif first == '6' and second in '123456789':
                formatted.append(f"6-7({second})")
            else:
                formatted.append(f"{first}-{second}")
        elif len(part) == 3:
            # Three digit tiebreak (e.g., "711" = 7-11 in tiebreak)
            formatted.append(f"{part[0]}-{part[1:]}")
        else:
            formatted.append(part)
    
    return " ".join(formatted) if formatted else score_str

def extract_matches_from_bracket(text, base_date='2025-02-17'):
    """
    Extract all matches from bracket text by parsing each round
    """
    matches = []
    
    # Process line by line to find match patterns
    lines = text.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip header lines
        if ('First round' in line or 'Second round' in line or 
            'Quarterfinals' in line or 'Semifinals' in line or
            'Top half' in line or 'Bottom half' in line or not line):
            i += 1
            continue
        
        # Split by tabs to get match data
        parts = line.split('\t')
        
        # Filter out empty parts
        parts = [p.strip() for p in parts if p.strip()]
        
        if len(parts) < 4:  # Need at least: player, scores, player, scores
            i += 1
            continue
        
        # Try to identify player-score patterns
        # Pattern: [seed] Country Name [scores...] [seed] Country Name [scores...]
        
        # Look for the first player name (contains letters, not just numbers)
        player1_idx = None
        for idx, part in enumerate(parts):
            # Skip pure numbers (seeds/scores)
            if part.isdigit():
                continue
            # Found text that could be a player name
            if re.search(r'[A-Za-z]', part):
                player1_idx = idx
                break
        
        if player1_idx is None:
            i += 1
            continue
        
        # Get player 1 name
        player1_name = clean_player_name(parts[player1_idx])
        
        # Get player 1 scores (numbers after player 1 name)
        player1_scores = []
        scores_idx = player1_idx + 1
        while scores_idx < len(parts) and parts[scores_idx].replace('r', '').isdigit():
            player1_scores.append(parts[scores_idx])
            scores_idx += 1
        
        # Look for player 2 (should be on next line if this is a first-round match)
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            next_parts = next_line.split('\t')
            next_parts = [p.strip() for p in next_parts if p.strip()]
            
            # Find player 2 name in next line
            player2_idx = None
            for idx, part in enumerate(next_parts):
                if part.isdigit():
                    continue
                if re.search(r'[A-Za-z]', part):
                    player2_idx = idx
                    break
            
            if player2_idx is not None:
                player2_name = clean_player_name(next_parts[player2_idx])
                
                # Get player 2 scores
                player2_scores = []
                scores_idx = player2_idx + 1
                while scores_idx < len(next_parts) and next_parts[scores_idx].replace('r', '').isdigit():
                    player2_scores.append(next_parts[scores_idx])
                    scores_idx += 1
                
                # If both players have scores, this is a match
                if player1_scores and player2_scores and len(player1_scores) == len(player2_scores):
                    # Determine winner (who won more sets)
                    p1_sets = 0
                    p2_sets = 0
                    
                    for s1, s2 in zip(player1_scores, player2_scores):
                        if 'r' in s1.lower():
                            p2_sets += 2  # Opponent wins if player retired
                            break
                        if 'r' in s2.lower():
                            p1_sets += 2
                            break
                        
                        # Compare first digit of each score
                        try:
                            if int(s1[0]) > int(s2[0]):
                                p1_sets += 1
                            elif int(s2[0]) > int(s1[0]):
                                p2_sets += 1
                        except:
                            pass
                    
                    # Determine winner and format score
                    if p1_sets > p2_sets:
                        winner = player1_name
                        loser = player2_name
                        score = parse_score_format(" ".join(player1_scores))
                    else:
                        winner = player2_name
                        loser = player1_name
                        score = parse_score_format(" ".join(player2_scores))
                    
                    # Only add valid matches
                    if winner and loser and len(winner) >= 2 and len(loser) >= 2:
                        matches.append({
                            'date': base_date,
                            'tournament_name': 'Rio de Janeiro',
                            'round': 'R32',  # Will update based on position
                            'winner_name': winner,
                            'loser_name': loser,
                            'score': score
                        })
                    
                    # Skip next line since we processed it
                    i += 2
                    continue
        
        i += 1
    
    return matches

def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_rio_bracket.py <input_file> <output_file> [date]")
        print("\nExample:")
        print("  python parse_rio_bracket.py data/raw/atp_500/rio_2025_bracket.txt data/raw/atp_500/rio_2025_parsed.csv 2025-02-17")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    date = sys.argv[3] if len(sys.argv) > 3 else '2025-02-17'
    
    print(f"Parsing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    matches = extract_matches_from_bracket(text, date)
    
    print(f"\n✅ Parsed {len(matches)} matches")
    
    if matches:
        # Show sample matches
        print("\nSample matches:")
        for match in matches[:5]:
            print(f"  {match['round']}: {match['winner_name']} def. {match['loser_name']} - {match['score']}")
        
        # Save to CSV
        fieldnames = ['date', 'tournament_name', 'round', 'winner_name', 'loser_name', 'score']
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matches)
        
        print(f"\n✅ Saved to {output_file}")
    else:
        print("⚠️  No matches found!")
    
    return len(matches)

if __name__ == '__main__':
    main()
