"""
Parse Indian Wells match format - Version 2 with improved logic.

This format has:
- Optional seed number
- Player names on separate lines
- Scores on separate lines (one per set)
- "Final" or "Retired" marker between matches
"""
import csv
import re
import sys
from pathlib import Path

def clean_player_name(name):
    """Clean player name"""
    return name.strip()

def is_seed(line):
    """Check if a line is a seed number (1-32)"""
    return bool(re.match(r'^[1-9]$|^[1-2][0-9]$|^3[0-2]$', line.strip()))

def is_score(line):
    """Check if a line is a score (1-2 digits)"""
    return bool(re.match(r'^\d{1,2}$', line.strip()))

def is_player_name(line):
    """Check if a line is a player name (contains letters and is not just a seed)"""
    # Must contain letters
    has_letters = bool(re.search(r'[a-zA-Z]', line))
    # Must not be a seed number
    not_seed = not is_seed(line)
    return has_letters and not_seed

def parse_score_to_format(p1_scores, p2_scores):
    """Convert score lists to formatted string
    
    Tiebreak format:
    - Winner shows like "77" = won 7-6(7)
    - Loser shows like "64" = lost 6-7(4)
    """
    if len(p1_scores) != len(p2_scores):
        return None
    
    score_parts = []
    p1_sets = 0
    p2_sets = 0
    
    for i in range(len(p1_scores)):
        s1 = p1_scores[i]
        s2 = p2_scores[i]
        
        # Check if either score indicates a tiebreak (2 digits >= 60)
        is_tiebreak = False
        if len(s1) == 2 and int(s1) >= 60:
            is_tiebreak = True
        if len(s2) == 2 and int(s2) >= 60:
            is_tiebreak = True
        
        if is_tiebreak:
            # Tiebreak set - one player has 7X (won 7-6), other has 6Y (lost 6-7)
            # The player with 7 in first digit won
            if s1[0] == '7':
                # P1 won the set 7-6
                score_parts.append(f"7-6({s1[1]}-{s2[1]})")
                p1_sets += 1
            else:
                # P2 won the set 7-6
                score_parts.append(f"6-7({s1[1]}-{s2[1]})")
                p2_sets += 1
        else:
            # Regular set
            score_parts.append(f"{s1}-{s2}")
            try:
                if int(s1) > int(s2):
                    p1_sets += 1
                else:
                    p2_sets += 1
            except:
                pass
    
    return ", ".join(score_parts), p1_sets, p2_sets

def parse_indian_wells_format(input_file, tournament_name, date, output_file):
    """Parse Indian Wells format"""
    print(f"Parsing {input_file}...")
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Detect round from content
    default_round = 'R64'
    if 'ROUND 2' in content.upper():
        default_round = 'R32'
    elif 'ROUND 3' in content.upper():
        default_round = 'R16'
    elif 'ROUND 4' in content.upper() or 'ROUND OF 16' in content.upper():
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
        
        # Don't remove seeds - instead, be smart about what we collect as scores
        # Seeds appear immediately before player names, scores appear after player names
        
        if len(lines) < 2:
            continue
        
        # Find player names (lines with letters)
        player_indices = []
        for i, line in enumerate(lines):
            if is_player_name(line):
                player_indices.append(i)
        
        if len(player_indices) < 2:
            continue
        
        # First two player names
        p1_idx = player_indices[0]
        p2_idx = player_indices[1]
        
        player1_name = lines[p1_idx]
        player2_name = lines[p2_idx]
        
        # Scores for player 1 are between p1 and p2
        # Skip any number that's immediately before p2 (that's p2's seed)
        player1_scores = []
        for i in range(p1_idx + 1, p2_idx):
            if is_score(lines[i]):
                # Don't include if this is immediately before player 2 (it's a seed)
                if i + 1 == p2_idx:
                    continue
                player1_scores.append(lines[i])
        
        # Scores for player 2 are after p2
        # Stop when we hit a seed+player combo or another player
        player2_scores = []
        for i in range(p2_idx + 1, len(lines)):
            if is_score(lines[i]):
                # Check if next line is a player name (this number is a seed, not a score)
                if i + 1 < len(lines) and is_player_name(lines[i + 1]):
                    break
                player2_scores.append(lines[i])
            elif is_player_name(lines[i]):
                # Hit another player, stop
                break
        
        # Parse scores
        result = parse_score_to_format(player1_scores, player2_scores)
        if result is None:
            print(f"  Warning: Score mismatch for {player1_name} vs {player2_name}")
            continue
        
        score, p1_sets, p2_sets = result
        
        # Determine winner
        if p1_sets > p2_sets:
            winner = player1_name
            loser = player2_name
        else:
            winner = player2_name
            loser = player1_name
        
        matches.append({
            'date': date,
            'tournament_name': tournament_name,
            'round': default_round,
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
        print("Usage: python3 parse_indian_wells_format_v2.py <input_file> <tournament_name> <date> <output_file>")
        print("\nExample:")
        print("  python3 parse_indian_wells_format_v2.py data/raw/iw_day1.txt 'Indian Wells' 2025-03-05 data/raw/iw_day1_parsed.csv")
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

