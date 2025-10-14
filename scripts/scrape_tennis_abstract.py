"""
Scrape match data from Tennis Abstract website for 2025.

This script scrapes tournament pages from tennisabstract.com to get
match data from December 18, 2024 onwards.
"""
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import RAW_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_2025_tournaments():
    """
    Get list of 2025 tournaments from Tennis Abstract.
    
    Returns:
        List of tournament IDs/names
    """
    # Known 2025 tournaments from the ATP calendar
    tournaments_2025 = [
        # January
        '2025-Brisbane', '2025-Hong_Kong', '2025-Auckland', '2025-Adelaide',
        '2025-Australian_Open',
        # February
        '2025-Montpellier', '2025-Pune', '2025-Dallas', '2025-Cordoba',
        '2025-Buenos_Aires', '2025-Rotterdam', '2025-Delray_Beach', '2025-Marseille',
        '2025-Doha', '2025-Dubai', '2025-Acapulco',
        # March
        '2025-Indian_Wells', '2025-Miami',
        # April
        '2025-Houston', '2025-Marrakech', '2025-Estoril', '2025-Munich',
        '2025-Barcelona', '2025-Banja_Luka',
        # May
        '2025-Madrid', '2025-Rome', '2025-Geneva', '2025-Lyon', '2025-French_Open',
        # June
        '2025-Stuttgart', '2025-s-Hertogenbosch', '2025-Halle', '2025-London',
        '2025-Mallorca', '2025-Eastbourne',
        # July
        '2025-Wimbledon', '2025-Newport', '2025-Bastad', '2025-Gstaad',
        '2025-Hamburg', '2025-Atlanta', '2025-Umag', '2025-Kitzbuhel',
        # August
        '2025-Washington', '2025-Montreal', '2025-Cincinnati', '2025-Winston-Salem',
        '2025-US_Open',
        # September
        '2025-Chengdu', '2025-Hangzhou', '2025-Zhuhai', '2025-Beijing',
        '2025-Tokyo', '2025-Shanghai',
        # October
        '2025-Antwerp', '2025-Almaty', '2025-Stockholm', '2025-Vienna',
        '2025-Basel', '2025-Paris', '2025-Metz', '2025-Wuhan',
    ]
    
    return tournaments_2025


def scrape_tournament_page(tournament_id, retry_on_429=True, retry_delay=30):
    """
    Scrape a single tournament page from Tennis Abstract.
    
    Args:
        tournament_id: Tournament identifier (e.g., '2025-Dallas')
        retry_on_429: Whether to retry if rate limited
        retry_delay: Seconds to wait before retrying after 429
    
    Returns:
        List of match dictionaries
    """
    # Tennis Abstract URL pattern
    # Example: https://www.tennisabstract.com/cgi-bin/tourney.cgi?t=2025Dallas
    tournament_name = tournament_id.replace('2025-', '').replace('_', '')
    url = f"https://www.tennisabstract.com/cgi-bin/tourney.cgi?t=2025{tournament_name}"
    
    logger.info(f"Scraping: {tournament_id}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 404:
            logger.warning(f"  ⚠️  Tournament not found: {tournament_id}")
            return []
        
        if response.status_code == 429:
            if retry_on_429:
                logger.warning(f"  ⚠️  Rate limited. Waiting {retry_delay}s and retrying...")
                time.sleep(retry_delay)
                # Retry once
                response = requests.get(url, timeout=10)
                if response.status_code == 429:
                    logger.error(f"  ❌ Still rate limited after retry: {tournament_id}")
                    return []
            else:
                logger.error(f"  ❌ HTTP 429 (rate limited) for {tournament_id}")
                return []
        
        if response.status_code != 200:
            logger.error(f"  ❌ HTTP {response.status_code} for {tournament_id}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract tournament info from the page
        tournament_info = {
            'id': tournament_id,
            'name': tournament_id.replace('2025-', '').replace('_', ' '),
            'surface': None,
            'date': None,
        }
        
        # Look for tournament details in the bio section
        bio = soup.find('span', id='bio')
        if bio:
            bio_text = bio.get_text()
            
            # Extract date (e.g., "February 3, 2025")
            date_match = re.search(r'([A-Z][a-z]+ \d+, 2025)', bio_text)
            if date_match:
                try:
                    date_str = date_match.group(1)
                    date_obj = datetime.strptime(date_str, '%B %d, %Y')
                    tournament_info['date'] = date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            # Extract surface (e.g., "Surface: Hard")
            surface_match = re.search(r'Surface:\s*(Hard|Clay|Grass|Carpet)', bio_text, re.IGNORECASE)
            if surface_match:
                tournament_info['surface'] = surface_match.group(1).lower()
        
        # Find the singles-results table
        singles_table = soup.find('table', id='singles-results')
        
        if not singles_table:
            logger.warning(f"  ⚠️  No singles-results table found for {tournament_id}")
            return []
        
        matches = []
        
        # Get tbody rows (skip thead)
        tbody = singles_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
        else:
            rows = singles_table.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) >= 7:  # Need at least: round, wRk, winner, d., lRk, loser, score
                try:
                    match_data = parse_match_row(cells, tournament_info)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.debug(f"  Could not parse row: {e}")
                    continue
        
        logger.info(f"  ✅ Found {len(matches)} matches")
        return matches
    
    except requests.RequestException as e:
        logger.error(f"  ❌ Network error for {tournament_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"  ❌ Error scraping {tournament_id}: {e}")
        return []


def parse_match_row(cells, tournament_info):
    """
    Parse a table row into match data.
    
    Based on Tennis Abstract HTML structure:
    - Cell 0: Round (F, SF, QF, R16, etc.)
    - Cell 1: Winner rank
    - Cell 2: Winner name (with link)
    - Cell 3: "d." (defeated)
    - Cell 4: Loser rank  
    - Cell 5: Loser name (with link)
    - Cell 6: Score
    - Rest: Stats
    """
    try:
        if len(cells) < 7:
            return None
        
        # Extract round
        round_text = cells[0].get_text(strip=True)
        if not round_text or round_text in ['Rd', 'Round']:
            return None  # Skip header rows
        
        # Extract winner name
        winner_link = cells[2].find('a')
        if not winner_link:
            return None
        winner_name = winner_link.get_text(strip=True)
        winner_name = re.sub(r'\s*\[.*?\].*$', '', winner_name)  # Remove [CAN] [yr|ev] etc
        
        # Extract loser name
        loser_link = cells[5].find('a')
        if not loser_link:
            return None
        loser_name = loser_link.get_text(strip=True)
        loser_name = re.sub(r'\s*\[.*?\].*$', '', loser_name)  # Remove [NOR] [yr|ev] etc
        loser_name = re.sub(r'^\(\d+\)\s*', '', loser_name)  # Remove (2) seed notation
        
        # Extract score
        score = cells[6].get_text(strip=True)
        
        # Extract winner/loser IDs from URLs
        winner_id = None
        loser_id = None
        
        winner_url = winner_link.get('href', '')
        loser_url = loser_link.get('href', '')
        
        winner_match = re.search(r'/(\d+)/', winner_url)
        if winner_match:
            winner_id = winner_match.group(1)
        
        loser_match = re.search(r'/(\d+)/', loser_url)
        if loser_match:
            loser_id = loser_match.group(1)
        
        match_data = {
            'tournament_id': tournament_info['id'],
            'tournament_name': tournament_info['name'],
            'surface': tournament_info['surface'],
            'date': tournament_info['date'],
            'round': round_text,
            'winner_id': winner_id,
            'winner_name': winner_name,
            'loser_id': loser_id,
            'loser_name': loser_name,
            'score': score,
        }
        
        return match_data
    
    except Exception as e:
        logger.debug(f"Error parsing match row: {e}")
        return None


def scrape_all_2025_tournaments():
    """
    Scrape all 2025 tournaments and save to CSV.
    """
    logger.info("=" * 80)
    logger.info("SCRAPING TENNIS ABSTRACT FOR 2025 MATCH DATA")
    logger.info("=" * 80)
    
    tournaments = get_2025_tournaments()
    logger.info(f"Found {len(tournaments)} potential 2025 tournaments")
    
    all_matches = []
    
    for i, tournament_id in enumerate(tournaments, 1):
        matches = scrape_tournament_page(tournament_id)
        all_matches.extend(matches)
        
        # Be respectful - wait 5 seconds between requests to avoid rate limiting
        if i < len(tournaments):
            logger.info(f"  Waiting 5 seconds... ({i}/{len(tournaments)} complete)")
            time.sleep(5)
    
    if not all_matches:
        logger.warning("⚠️  No matches found. The scraper may need adjustment.")
        logger.info("\n" + "=" * 80)
        logger.info("NEXT STEPS:")
        logger.info("=" * 80)
        logger.info("""
1. Visit a sample tournament page manually:
   https://www.tennisabstract.com/cgi-bin/tourney.cgi?t=2025Dallas

2. Inspect the HTML structure to understand how match data is organized

3. Update the parse_match_row() function to extract:
   - Match date
   - Player names
   - Score
   - Round
   - Surface

4. Run this script again
        """)
        return
    
    # Save to CSV
    output_file = RAW_DATA_DIR / 'tennis_abstract_2025_scraped.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'tournament_id', 'tournament_name', 'surface', 'date',
            'round', 'winner_id', 'winner_name', 'loser_id', 'loser_name', 'score'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_matches)
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ SCRAPING COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total matches scraped: {len(all_matches)}")
    logger.info(f"Saved to: {output_file}")


def inspect_tournament_page(tournament_id='2025Dallas'):
    """
    Helper function to inspect a tournament page's HTML structure.
    Use this to understand how to parse the data.
    """
    url = f"https://www.tennisabstract.com/cgi-bin/tourney.cgi?t={tournament_id}"
    
    logger.info(f"Inspecting: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save HTML for inspection
        output_file = RAW_DATA_DIR / f'{tournament_id}_sample.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        logger.info(f"✅ Saved HTML to: {output_file}")
        logger.info("\nPage structure:")
        logger.info(f"  Title: {soup.title.string if soup.title else 'N/A'}")
        logger.info(f"  Tables found: {len(soup.find_all('table'))}")
        logger.info(f"  Links found: {len(soup.find_all('a'))}")
        
        # Show first table structure
        first_table = soup.find('table')
        if first_table:
            logger.info("\nFirst table structure:")
            rows = first_table.find_all('tr')[:5]
            for i, row in enumerate(rows):
                cells = row.find_all(['th', 'td'])
                logger.info(f"  Row {i}: {len(cells)} cells")
                for j, cell in enumerate(cells[:5]):
                    logger.info(f"    Cell {j}: {cell.get_text(strip=True)[:50]}")
    
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Tennis Abstract for 2025 match data')
    parser.add_argument('--inspect', action='store_true', 
                       help='Inspect a sample tournament page to understand HTML structure')
    parser.add_argument('--tournament', default='2025Dallas',
                       help='Tournament ID to inspect (default: 2025Dallas)')
    
    args = parser.parse_args()
    
    if args.inspect:
        inspect_tournament_page(args.tournament)
    else:
        scrape_all_2025_tournaments()


if __name__ == "__main__":
    main()

