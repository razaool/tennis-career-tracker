"""
Parse Indian Wells match format.

This format has:
- Player names on separate lines
- Scores on separate lines (one per set)
- "Final" marker between matches
"""
import csv
import re
import sys
from pathlib import Path

def clean_player_name(name):
    """Clean player name"""
    name = name.strip()
    # Remove any leading/trailing whitespace
    return name

def parse_score_lines(lines):
    """Parse score lines into a score string"""
    scores = []
    for line in lines:
        line = line.strip()
        if line and line.isdigit() or re.match(r'^\d+$', line) or re.match(r'^\d{1,2}$', line):
            scores.append(line)
    
    # Group into sets (pairs of scores)
    sets = []
    i = 0
    while i < len(scores) - 1:
        set_score = f"{scores[i]}-{scores[i+1]}"
        sets.append(set_score)
        i += 2
    
    return ", ".join(sets) if sets else ""

def parse_indian_wells_format(input_file, tournament_name, date, output_file):
    """
    Parse Indian Wells format
    
    Format:
    [Seed]
    Player 1 Name
    Set1Score1
    Set2Score1
    Set3Score1 (if exists)
    
    [Seed]
    Player 2 Name
    Set1Score2
    Set2Score2
    Set3Score2 (if exists)
    """
    print(f"Parsing {input_file}...")
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Detect round from content
    default_round = 'R64'
    if 'ROUND 2' in content.upper():
        default_round = 'R32'
    elif 'ROUND 3' in content.upper():
        default_round = 'R16'
    
    # Split by "Final" or "Retired" markers
    content = content.replace('Retired', 'Final')
    matches_raw = content.split('Final')
    
    matches = []
    
    for match_text in matches_raw:
        if not match_text.strip():
            continue
        
        lines = [l.strip() for l in match_text.strip().split('\n') if l.strip()]
        
        # Skip headers and stadium info
        lines = [l for l in lines if not l.startswith('ROUND') and 
                 not l.startswith('Round ') and 
                 not l.upper().startswith('INDIAN WELLS') and
                 not l.upper().startswith('MARCH') and
                 not l.startswith('DAY')]
        
        if len(lines) < 2:
            continue
        
        # Remove seed numbers (1-32 on their own line followed by a name)
        cleaned_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if this is a seed number (1-32)
            if re.match(r'^[1-9]$|^[1-2][0-9]$|^3[0-2]$', line):
                # Check if next line exists and is NOT a number (i.e., it's a player name)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # If next line is not purely numeric (or is a long number like a score), this is a seed
                    if not re.match(r'^\d{1,2}$', next_line):
                        # This is a seed, skip it
                        i += 1
                        continue
            cleaned_lines.append(line)
            i += 1
        
        lines = cleaned_lines
        
        if len(lines) < 2:
            continue
        
        # First line should be player 1 name
        player1_name = lines[0]
        
        # Find player 2 name (first line that's not a number after player 1)
        player2_idx = None
        for i in range(1, len(lines)):
            if not re.match(r'^\d{1,2}$', lines[i]):
                player2_idx = i
                break
        
        if player2_idx is None:
            continue
        
        player2_name = lines[player2_idx]
        
        # Scores for player 1 are between player1_name and player2_name
        player1_scores = lines[1:player2_idx]
        
        # Scores for player 2 are after player2_name
        player2_scores = lines[player2_idx + 1:]
        
        # Determine winner (player with more sets won)
        if len(player1_scores) != len(player2_scores):
            print(f"  Warning: Score mismatch for {player1_name} vs {player2_name}")
            continue
        
        player1_sets = 0
        player2_sets = 0
        score_parts = []
        
        for i in range(len(player1_scores)):
            s1 = player1_scores[i]
            s2 = player2_scores[i]
            
            # Handle tiebreak scores (77, 64, etc.)
            if len(s1) == 2 and len(s2) == 2:
                # Could be tiebreak or regular score
                if int(s1) > 10 or int(s2) > 10:
                    # Tiebreak notation
                    score_parts.append(f"{s1[0]}-{s2[0]}({s1[1]}-{s2[1]})")
                    if int(s1[0]) > int(s2[0]):
                        player1_sets += 1
                    else:
                        player2_sets += 1
                else:
                    score_parts.append(f"{s1}-{s2}")
                    if int(s1) > int(s2):
                        player1_sets += 1
                    else:
                        player2_sets += 1
            else:
                score_parts.append(f"{s1}-{s2}")
                if int(s1) > int(s2):
                    player1_sets += 1
                else:
                    player2_sets += 1
        
        score = ", ".join(score_parts)
        
        # Determine winner
        if player1_sets > player2_sets:
            winner = player1_name
            loser = player2_name
        else:
            winner = player2_name
            loser = player1_name
        
        # Determine round based on context or default
        round_code = default_round
        
        matches.append({
            'date': date,
            'tournament_name': tournament_name,
            'round': round_code,
            'winner_name': winner,
            'loser_name': loser,
            'score': score
        })
    
    # Write to CSV
    if matches:
        with open(output_file, 'w', newline='') as f:
            fieldnames = ['date', 'tournament_name', 'round', 'winner_name', 'loser_name', 'score']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matches)
        
        print(f"✅ Parsed {len(matches)} matches")
        print(f"✅ Saved to {output_file}")
    else:
        print("⚠️  No matches parsed!")
    
    return len(matches)

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 parse_indian_wells_format.py <input_file> <tournament_name> <date> <output_file>")
        print("\nExample:")
        print("  python3 parse_indian_wells_format.py data/raw/iw_day1.txt 'Indian Wells' 2025-03-05 data/raw/iw_day1_parsed.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    tournament_name = sys.argv[2]
    date = sys.argv[3]
    output_file = sys.argv[4]
    
    count = parse_indian_wells_format(input_file, tournament_name, date, output_file)
    
    print(f"\n{'='*80}")
    print("✅ PARSING COMPLETE!")
    print(f"{'='*80}")
    print(f"Matches parsed: {count}")

if __name__ == "__main__":
    main()

