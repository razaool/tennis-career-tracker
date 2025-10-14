"""
Scrape 2025 Grand Slam data from Tennis Abstract.

Focuses only on the 4 major tournaments:
- Australian Open
- French Open
- Wimbledon
- US Open
"""
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import RAW_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Grand Slam tournament IDs on Tennis Abstract
GRAND_SLAMS_2025 = {
    '580-2025': {
        'name': 'Australian Open',
        'surface': 'Hard',
        'level': 'G',
        'date_start': '20250112',
        'url': 'https://www.tennisabstract.com/cgi-bin/wplayer.cgi?f=ACareerqq580-2025'
    },
    '520-2025': {
        'name': 'French Open',
        'surface': 'Clay',
        'level': 'G',
        'date_start': '20250525',
        'url': 'https://www.tennisabstract.com/cgi-bin/wplayer.cgi?f=ACareerqq520-2025'
    },
    '540-2025': {
        'name': 'Wimbledon',
        'surface': 'Grass',
        'level': 'G',
        'date_start': '20250630',
        'url': 'https://www.tennisabstract.com/cgi-bin/wplayer.cgi?f=ACareerqq540-2025'
    },
    '560-2025': {
        'name': 'US Open',
        'surface': 'Hard',
        'level': 'G',
        'date_start': '20250825',
        'url': 'https://www.tennisabstract.com/cgi-bin/wplayer.cgi?f=ACareerqq560-2025'
    },
}


def scrape_grand_slam(tournament_id, tournament_info, retry_on_429=True, retry_delay=30):
    """
    Scrape a Grand Slam tournament from Tennis Abstract.
    
    Args:
        tournament_id: Tournament identifier (e.g., '580-2025')
        tournament_info: Dict with tournament details
        retry_on_429: Whether to retry on rate limit
        retry_delay: Seconds to wait before retry
    
    Returns:
        List of match dictionaries
    """
    url = f'https://www.tennisabstract.com/cgi-bin/tournaments/{tournament_id}.html'
    logger.info(f"\nScraping: {tournament_info['name']}")
    logger.info(f"  URL: {url}")
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 429:
            if retry_on_429:
                logger.warning(f"  ⚠️  Rate limited (429). Waiting {retry_delay} seconds...")
                time.sleep(retry_delay)
                return scrape_grand_slam(tournament_id, tournament_info, retry_on_429=False)
            else:
                logger.error(f"  ❌ Rate limited (429) - skipping")
                return []
        
        if response.status_code == 404:
            logger.warning(f"  ⚠️  Tournament not found (404) - may not have occurred yet")
            return []
        
        if response.status_code != 200:
            logger.error(f"  ❌ HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract tournament info from the page
        tournament_name = tournament_info['name']
        surface = tournament_info['surface']
        
        # Try to extract date from page
        date_match = re.search(r'(\w+ \d+, \d{4})', response.text)
        if date_match:
            logger.info(f"  Found date: {date_match.group(1)}")
        
        # Find the singles results table
        results_table = None
        for table in soup.find_all('table'):
            # Look for table with "singles" in nearby text
            table_text = table.get_text().lower()
            if 'singles' in table_text or 'round' in table_text:
                results_table = table
                break
        
        if not results_table:
            logger.warning(f"  ⚠️  No results table found")
            return []
        
        matches = []
        rows = results_table.find_all('tr')
        
        logger.info(f"  Found {len(rows)} rows in results table")
        
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            
            if len(cells) < 4:
                continue
            
            try:
                # Parse match data
                match_data = parse_match_row(cells, tournament_info)
                
                if match_data:
                    matches.append(match_data)
            
            except Exception as e:
                logger.debug(f"  Error parsing row: {e}")
                continue
        
        logger.info(f"  ✅ Found {len(matches)} matches")
        return matches
    
    except requests.RequestException as e:
        logger.error(f"  ❌ Network error: {e}")
        return []
    except Exception as e:
        logger.error(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_match_row(cells, tournament_info):
    """
    Parse a match row from the results table.
    
    Expected format varies, but typically:
    - Round
    - Winner name (with link)
    - Score
    - Loser name (with link)
    """
    if len(cells) < 3:
        return None
    
    # Try to extract round
    round_text = cells[0].get_text().strip() if cells else 'R128'
    
    # Find player names (look for links)
    player_links = []
    for cell in cells:
        links = cell.find_all('a')
        for link in links:
            href = link.get('href', '')
            if '/cgi-bin/player' in href or '/cgi-bin/wplayer' in href:
                player_links.append(link)
    
    if len(player_links) < 2:
        return None
    
    # Extract winner and loser
    winner_link = player_links[0]
    loser_link = player_links[1]
    
    winner_name = winner_link.get_text().strip()
    loser_name = loser_link.get_text().strip()
    
    # Extract player IDs from URLs
    winner_id = extract_player_id(winner_link.get('href', ''))
    loser_id = extract_player_id(loser_link.get('href', ''))
    
    # Try to find score
    score = None
    for cell in cells:
        cell_text = cell.get_text().strip()
        # Score pattern: contains numbers and dashes
        if re.search(r'\d+-\d+', cell_text) and 'http' not in cell_text:
            score = cell_text
            break
    
    if not winner_name or not loser_name:
        return None
    
    return {
        'tournament_id': tournament_info.get('tournament_id', ''),
        'tournament_name': tournament_info['name'],
        'surface': tournament_info['surface'],
        'date': tournament_info['date_start'],
        'level': tournament_info['level'],
        'round': round_text,
        'winner_id': winner_id,
        'winner_name': winner_name,
        'loser_id': loser_id,
        'loser_name': loser_name,
        'score': score or '',
    }


def extract_player_id(url):
    """Extract player ID from Tennis Abstract URL"""
    if not url:
        return ''
    
    # Pattern: player.cgi?p=PlayerId or wplayer.cgi?f=...PlayerId
    match = re.search(r'[?&]p=([^&]+)', url)
    if match:
        return match.group(1)
    
    match = re.search(r'[?&]f=.*?([A-Z][a-z]+[A-Z][a-z]+\d+)', url)
    if match:
        return match.group(1)
    
    return ''


def scrape_all_grand_slams():
    """Scrape all 4 Grand Slams for 2025"""
    logger.info("=" * 80)
    logger.info("SCRAPING 2025 GRAND SLAMS FROM TENNIS ABSTRACT")
    logger.info("=" * 80)
    logger.info(f"Target: 4 Grand Slam tournaments")
    
    all_matches = []
    successful = []
    failed = []
    
    for tournament_id, info in GRAND_SLAMS_2025.items():
        matches = scrape_grand_slam(tournament_id, info)
        
        if matches:
            all_matches.extend(matches)
            successful.append(info['name'])
        else:
            failed.append(info['name'])
        
        # Be respectful - wait between requests
        logger.info("  Waiting 5 seconds before next request...")
        time.sleep(5)
    
    # Save to CSV
    if all_matches:
        output_file = RAW_DATA_DIR / 'grand_slams_2025_scraped.csv'
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'tournament_id', 'tournament_name', 'surface', 'date', 'level',
                'round', 'winner_id', 'winner_name', 'loser_id', 'loser_name', 'score'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_matches)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ SCRAPING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Successful: {len(successful)} tournaments")
        for name in successful:
            logger.info(f"  ✅ {name}")
        
        if failed:
            logger.info(f"\nNot found: {len(failed)} tournaments (may not have occurred yet)")
            for name in failed:
                logger.info(f"  ⚠️  {name}")
        
        logger.info(f"\nTotal matches: {len(all_matches)}")
        logger.info(f"Saved to: {output_file}")
        
        return output_file
    else:
        logger.warning("\n⚠️  No matches found from any Grand Slam")
        return None


def main():
    """Main execution"""
    output_file = scrape_all_grand_slams()
    
    if output_file:
        logger.info("\n" + "=" * 80)
        logger.info("NEXT STEPS:")
        logger.info("=" * 80)
        logger.info("1. Review the scraped data:")
        logger.info(f"   cat {output_file}")
        logger.info("\n2. Convert to Tennis Abstract format:")
        logger.info("   python3 scripts/convert_scraped_to_ta_format.py")
        logger.info("\n3. Load into database:")
        logger.info("   python3 scripts/load_2025_data.py")
        logger.info("\n4. Recalculate ELO ratings:")
        logger.info("   python3 scripts/calculate_elo.py")


if __name__ == "__main__":
    main()

