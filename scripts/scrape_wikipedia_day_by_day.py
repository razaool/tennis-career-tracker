"""
Scrape 2025 Australian Open data from Wikipedia day-by-day summaries page.

This page has a much simpler format than the draw pages, with clean tables
showing Winner | Loser | Score for each match.
"""
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import csv
import re
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import RAW_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_player_name(name):
    """Clean player name from Wikipedia format"""
    if not name:
        return None
    
    # Remove seed numbers in brackets
    name = re.sub(r'\s*\[\d+\]\s*', '', name)
    name = re.sub(r'\s*\[WC\]\s*', '', name)
    name = re.sub(r'\s*\[Q\]\s*', '', name)
    name = re.sub(r'\s*\[LL\]\s*', '', name)
    name = re.sub(r'\s*\[PR\]\s*', '', name)
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    return name.strip() if name else None


def parse_score(score_text):
    """Extract clean score from Wikipedia format"""
    if not score_text:
        return None
    
    # Remove HTML tags
    score = re.sub(r'<[^>]+>', '', score_text)
    
    # Convert superscript tiebreak scores
    # e.g., "7–6(7–2)" from "7–6<sup>(7–2)</sup>"
    score = score.replace('–', '-')
    
    # Clean up whitespace
    score = ' '.join(score.split())
    
    return score.strip() if score else None


def extract_round_from_heading(heading_text):
    """Extract round from table heading"""
    heading_lower = heading_text.lower()
    
    if 'final' in heading_lower and 'semifinal' not in heading_lower:
        return 'F'
    elif 'semifinal' in heading_lower:
        return 'SF'
    elif 'quarterfinal' in heading_lower:
        return 'QF'
    elif '4th round' in heading_lower or 'round of 16' in heading_lower:
        return 'R16'
    elif '3rd round' in heading_lower or 'round of 32' in heading_lower:
        return 'R32'
    elif '2nd round' in heading_lower or 'round of 64' in heading_lower:
        return 'R64'
    elif '1st round' in heading_lower or 'round of 128' in heading_lower:
        return 'R128'
    
    return 'R128'  # Default


def scrape_australian_open_2025():
    """
    Scrape 2025 Australian Open from Wikipedia day-by-day summaries.
    """
    url = 'https://en.wikipedia.org/wiki/2025_Australian_Open_–_Day-by-day_summaries'
    logger.info("=" * 80)
    logger.info("SCRAPING 2025 AUSTRALIAN OPEN FROM WIKIPEDIA")
    logger.info("=" * 80)
    logger.info(f"URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"❌ HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        matches = []
        current_round = 'R128'
        
        # Find all tables on the page
        tables = soup.find_all('table', class_='wikitable')
        logger.info(f"Found {len(tables)} tables")
        
        for table in tables:
            # Try to find the round from nearby heading
            # Look backwards for the nearest heading
            prev_element = table.find_previous(['h2', 'h3', 'h4', 'caption', 'th'])
            if prev_element:
                heading_text = prev_element.get_text()
                if 'men' in heading_text.lower() and 'singles' in heading_text.lower():
                    current_round = extract_round_from_heading(heading_text)
            
            # Parse table rows
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                
                if len(cells) < 4:
                    continue
                
                try:
                    # Expected format: Event | Winner | Loser | Score
                    event_cell = cells[0]
                    winner_cell = cells[1]
                    loser_cell = cells[2]
                    score_cell = cells[3]
                    
                    # Check if this is a men's singles match
                    # Look for link text in the event cell
                    event_link = event_cell.find('a')
                    if not event_link:
                        continue
                    
                    event_text = event_link.get_text().lower()
                    if 'men' not in event_text or 'singles' not in event_text:
                        continue
                    
                    # Extract round from event text
                    current_round = extract_round_from_heading(event_text)
                    
                    # Extract winner name (look for link)
                    winner_link = winner_cell.find('a', href=re.compile(r'/wiki/'))
                    if not winner_link:
                        continue
                    
                    winner_name = clean_player_name(winner_link.get_text())
                    
                    # Extract loser name
                    loser_link = loser_cell.find('a', href=re.compile(r'/wiki/'))
                    if not loser_link:
                        continue
                    
                    loser_name = clean_player_name(loser_link.get_text())
                    
                    # Extract score
                    score = parse_score(score_cell.get_text())
                    
                    if not winner_name or not loser_name or not score:
                        continue
                    
                    # Check if it's a men's singles match
                    # (Skip if it's women's, doubles, etc.)
                    # We can infer this from the context or just include all
                    
                    match_data = {
                        'tournament_name': 'Australian Open',
                        'surface': 'Hard',
                        'date': '20250126',  # Final date, we'll adjust per round later
                        'level': 'G',
                        'round': current_round,
                        'winner_name': winner_name,
                        'loser_name': loser_name,
                        'score': score,
                    }
                    
                    matches.append(match_data)
                    logger.debug(f"  {current_round}: {winner_name} def. {loser_name} {score}")
                
                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue
        
        logger.info(f"\n✅ Found {len(matches)} total matches")
        
        # Filter for men's singles only
        # We need to be smarter about this - for now, keep all
        return matches
    
    except requests.RequestException as e:
        logger.error(f"❌ Network error: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """Main execution"""
    matches = scrape_australian_open_2025()
    
    if matches:
        output_file = RAW_DATA_DIR / 'australian_open_2025_wikipedia.csv'
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'tournament_name', 'surface', 'date', 'level',
                'round', 'winner_name', 'loser_name', 'score'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matches)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ SCRAPING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total matches: {len(matches)}")
        logger.info(f"Saved to: {output_file}")
        
        # Show sample matches
        logger.info("\n📊 SAMPLE MATCHES:")
        for match in matches[:5]:
            logger.info(f"  {match['round']}: {match['winner_name']} def. {match['loser_name']} {match['score']}")
        
        logger.info("\n" + "=" * 80)
        logger.info("NEXT STEPS:")
        logger.info("=" * 80)
        logger.info("1. Review the data:")
        logger.info(f"   head -20 {output_file}")
        logger.info("\n2. Convert to Tennis Abstract format:")
        logger.info("   python3 scripts/convert_scraped_to_ta_format.py")
        logger.info("\n3. Load into database:")
        logger.info("   python3 scripts/load_2025_data.py")
    else:
        logger.warning("⚠️  No matches found")


if __name__ == "__main__":
    main()

