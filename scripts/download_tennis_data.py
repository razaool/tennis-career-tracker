"""
Script to download Tennis Abstract data from GitHub
Downloads both ATP and WTA data repositories
"""
import subprocess
import logging
from pathlib import Path
import shutil

from config import RAW_DATA_DIR, TENNIS_ABSTRACT_REPOS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TennisDataDownloader:
    """Downloads and manages Tennis Abstract data"""
    
    def __init__(self):
        self.raw_data_dir = RAW_DATA_DIR
        self.repos = TENNIS_ABSTRACT_REPOS
    
    def download_repo(self, tour_type='atp'):
        """
        Download Tennis Abstract repository
        
        Args:
            tour_type: 'atp' or 'wta'
        """
        if tour_type not in self.repos:
            raise ValueError(f"Invalid tour type: {tour_type}. Must be 'atp' or 'wta'")
        
        repo_url = self.repos[tour_type]
        target_dir = self.raw_data_dir / f"tennis_{tour_type}"
        
        # Remove existing directory if it exists
        if target_dir.exists():
            logger.info(f"Removing existing {tour_type.upper()} data directory...")
            shutil.rmtree(target_dir)
        
        logger.info(f"Downloading {tour_type.upper()} data from {repo_url}...")
        
        try:
            # Clone the repository
            subprocess.run(
                ['git', 'clone', repo_url, str(target_dir)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"✅ Successfully downloaded {tour_type.upper()} data to {target_dir}")
            
            # List available match files
            match_files = list(target_dir.glob(f"{tour_type}_matches_*.csv"))
            logger.info(f"Found {len(match_files)} match data files")
            
            # Show year range
            if match_files:
                years = sorted([
                    int(f.stem.split('_')[-1]) 
                    for f in match_files 
                    if f.stem.split('_')[-1].isdigit()
                ])
                if years:
                    logger.info(f"Data available for years: {min(years)} - {max(years)}")
            
            return target_dir
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download {tour_type.upper()} data: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Error downloading {tour_type.upper()} data: {e}")
            raise
    
    def download_all(self):
        """Download both ATP and WTA data"""
        results = {}
        
        for tour_type in ['atp', 'wta']:
            try:
                results[tour_type] = self.download_repo(tour_type)
            except Exception as e:
                logger.error(f"Failed to download {tour_type.upper()}: {e}")
                results[tour_type] = None
        
        return results
    
    def get_data_info(self):
        """Get information about downloaded data"""
        info = {}
        
        for tour_type in ['atp', 'wta']:
            data_dir = self.raw_data_dir / f"tennis_{tour_type}"
            
            if not data_dir.exists():
                info[tour_type] = {
                    'downloaded': False,
                    'path': None,
                    'match_files': 0,
                    'player_files': 0,
                    'ranking_files': 0
                }
                continue
            
            # Count different file types
            match_files = list(data_dir.glob(f"{tour_type}_matches_*.csv"))
            player_files = list(data_dir.glob(f"{tour_type}_players.csv"))
            ranking_files = list(data_dir.glob(f"{tour_type}_rankings_*.csv"))
            
            info[tour_type] = {
                'downloaded': True,
                'path': str(data_dir),
                'match_files': len(match_files),
                'player_files': len(player_files),
                'ranking_files': len(ranking_files)
            }
            
            # Get year range from match files
            if match_files:
                years = sorted([
                    int(f.stem.split('_')[-1]) 
                    for f in match_files 
                    if f.stem.split('_')[-1].isdigit()
                ])
                if years:
                    info[tour_type]['year_range'] = f"{min(years)}-{max(years)}"
        
        return info


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Tennis Abstract Data Downloader")
    logger.info("=" * 60)
    
    downloader = TennisDataDownloader()
    
    # Download ATP data (start with ATP for MVP)
    logger.info("\nDownloading ATP data...")
    downloader.download_repo('atp')
    
    # Optionally download WTA data (commented out for now)
    # logger.info("\nDownloading WTA data...")
    # downloader.download_repo('wta')
    
    # Show summary
    logger.info("\n" + "=" * 60)
    logger.info("Download Summary")
    logger.info("=" * 60)
    
    info = downloader.get_data_info()
    for tour_type, details in info.items():
        logger.info(f"\n{tour_type.upper()} Data:")
        if details['downloaded']:
            logger.info(f"  ✅ Downloaded: {details['path']}")
            logger.info(f"  📊 Match files: {details['match_files']}")
            logger.info(f"  👤 Player files: {details['player_files']}")
            logger.info(f"  📈 Ranking files: {details['ranking_files']}")
            if 'year_range' in details:
                logger.info(f"  📅 Years: {details['year_range']}")
        else:
            logger.info(f"  ❌ Not downloaded")
    
    logger.info("\n✅ Data download complete!")


if __name__ == "__main__":
    main()

