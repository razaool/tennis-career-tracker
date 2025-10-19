"""
Export ELO ratings data for visualization.
Creates CSV files ready for charting (DARKO-style career progressions).
"""
import sys
from pathlib import Path
import csv
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from config import PROCESSED_DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def export_player_career_trajectory(db, player_name, output_file=None):
    """
    Export a single player's career ELO trajectory.
    
    Args:
        db: DatabaseManager instance
        player_name: Player name (e.g., 'Novak Djokovic')
        output_file: Optional output file path
    
    Returns:
        List of rating records
    """
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.name,
                pr.career_match_number,
                pr.date,
                pr.elo_rating,
                pr.elo_clay,
                pr.elo_grass,
                pr.elo_hard
            FROM player_ratings pr
            JOIN players p ON pr.player_id = p.player_id
            WHERE p.name = %s
            ORDER BY pr.career_match_number
        """, (player_name,))
        
        ratings = cursor.fetchall()
        
        if not ratings:
            logger.warning(f"No ratings found for player: {player_name}")
            return []
        
        logger.info(f"Found {len(ratings)} ratings for {player_name}")
        
        # Export to CSV if output file specified
        if output_file:
            output_path = PROCESSED_DATA_DIR / output_file
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=ratings[0].keys())
                writer.writeheader()
                writer.writerows(ratings)
            logger.info(f"Exported to: {output_path}")
        
        return ratings


def export_multiple_players(db, player_names, output_file='big3_comparison.csv'):
    """
    Export multiple players' trajectories for comparison.
    Perfect for DARKO-style multi-line charts.
    
    Args:
        db: DatabaseManager instance
        player_names: List of player names
        output_file: Output CSV filename
    """
    with db.get_cursor() as cursor:
        # Use ANY to match multiple players
        cursor.execute("""
            SELECT 
                p.name,
                pr.career_match_number,
                pr.date,
                pr.elo_rating,
                pr.elo_clay,
                pr.elo_grass,
                pr.elo_hard
            FROM player_ratings pr
            JOIN players p ON pr.player_id = p.player_id
            WHERE p.name = ANY(%s)
            ORDER BY p.name, pr.career_match_number
        """, (player_names,))
        
        ratings = cursor.fetchall()
        
        if not ratings:
            logger.warning("No ratings found for specified players")
            return []
        
        logger.info(f"Found {len(ratings)} total ratings for {len(player_names)} players")
        
        # Export to CSV
        output_path = PROCESSED_DATA_DIR / output_file
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=ratings[0].keys())
            writer.writeheader()
            writer.writerows(ratings)
        
        logger.info(f"Exported to: {output_path}")
        
        return ratings


def export_top_players(db, n=10, output_file='top_players_current.csv'):
    """
    Export current top N players by ELO rating (active players only).
    
    Args:
        db: DatabaseManager instance
        n: Number of top players to export
        output_file: Output CSV filename
    """
    with db.get_cursor() as cursor:
        # Get latest rating for each player (active players only - last match in 2024 or 2025)
        cursor.execute("""
            WITH latest_ratings AS (
                SELECT 
                    player_id,
                    MAX(career_match_number) as max_match
                FROM player_ratings
                GROUP BY player_id
            )
            SELECT 
                p.name,
                pr.elo_rating,
                pr.elo_clay,
                pr.elo_grass,
                pr.elo_hard,
                pr.career_match_number as total_matches,
                pr.date as last_match_date
            FROM player_ratings pr
            JOIN latest_ratings lr ON pr.player_id = lr.player_id 
                AND pr.career_match_number = lr.max_match
            JOIN players p ON pr.player_id = p.player_id
            WHERE pr.date >= '2024-01-01'
            ORDER BY pr.elo_rating DESC
            LIMIT %s
        """, (n,))
        
        top_players = cursor.fetchall()
        
        logger.info(f"Top {n} players by current ELO:")
        for i, player in enumerate(top_players, 1):
            logger.info(f"  {i:2d}. {player['name']:30s} ELO: {player['elo_rating']:7.1f}")
        
        # Export to CSV
        output_path = PROCESSED_DATA_DIR / output_file
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=top_players[0].keys())
            writer.writeheader()
            writer.writerows(top_players)
        
        logger.info(f"Exported to: {output_path}")
        
        return top_players


def export_surface_comparison(db, player_name, output_file=None):
    """
    Export a player's ratings across all surfaces for radar chart.
    
    Args:
        db: DatabaseManager instance
        player_name: Player name
        output_file: Optional output file path
    """
    with db.get_cursor() as cursor:
        # Get latest rating
        cursor.execute("""
            SELECT 
                p.name,
                pr.elo_clay,
                pr.elo_grass,
                pr.elo_hard,
                pr.elo_rating as overall
            FROM player_ratings pr
            JOIN players p ON pr.player_id = p.player_id
            WHERE p.name = %s
            ORDER BY pr.career_match_number DESC
            LIMIT 1
        """, (player_name,))
        
        rating = cursor.fetchone()
        
        if not rating:
            logger.warning(f"No ratings found for: {player_name}")
            return None
        
        logger.info(f"{player_name} surface ratings:")
        logger.info(f"  Clay:    {rating['elo_clay']:.1f}")
        logger.info(f"  Grass:   {rating['elo_grass']:.1f}")
        logger.info(f"  Hard:    {rating['elo_hard']:.1f}")
        logger.info(f"  Overall: {rating['overall']:.1f}")
        
        if output_file:
            output_path = PROCESSED_DATA_DIR / output_file
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rating.keys())
                writer.writeheader()
                writer.writerow(rating)
            logger.info(f"Exported to: {output_path}")
        
        return rating


def export_rating_system_csvs(db, rating_type='elo'):
    """
    Export CSVs for a specific rating system (ELO, TSR, or Glicko-2).
    
    Args:
        db: DatabaseManager instance
        rating_type: 'elo', 'tsr', or 'glicko2'
    """
    # Determine columns and directory based on rating type
    if rating_type == 'elo':
        dir_name = 'elo_only'
        rating_col = 'elo_rating'
        clay_col = 'elo_clay'
        grass_col = 'elo_grass'
        hard_col = 'elo_hard'
    elif rating_type == 'tsr':
        dir_name = 'tsr_with_bayesian'
        rating_col = 'tsr_rating'
        clay_col = 'elo_clay'  # TSR uses same surface ratings as ELO
        grass_col = 'elo_grass'
        hard_col = 'elo_hard'
    elif rating_type == 'glicko2':
        dir_name = 'glicko2'
        rating_col = 'glicko2_rating'
        clay_col = 'elo_clay'  # Glicko2 doesn't have separate surface ratings
        grass_col = 'elo_grass'
        hard_col = 'elo_hard'
    else:
        raise ValueError(f"Invalid rating_type: {rating_type}")
    
    output_dir = PROCESSED_DATA_DIR / dir_name
    output_dir.mkdir(exist_ok=True)
    
    logger.info(f"\n📊 Exporting {rating_type.upper()} ratings to {dir_name}/...")
    
    # Export top 10 current players
    with db.get_cursor() as cursor:
        cursor.execute(f"""
            WITH latest_ratings AS (
                SELECT 
                    player_id,
                    MAX(career_match_number) as max_match
                FROM player_ratings
                GROUP BY player_id
            )
            SELECT 
                p.name,
                pr.{rating_col} as rating,
                pr.{clay_col} as clay_rating,
                pr.{grass_col} as grass_rating,
                pr.{hard_col} as hard_rating,
                pr.career_match_number as total_matches,
                pr.date as last_match_date
            FROM player_ratings pr
            JOIN latest_ratings lr ON pr.player_id = lr.player_id 
                AND pr.career_match_number = lr.max_match
            JOIN players p ON pr.player_id = p.player_id
            WHERE pr.date >= '2025-01-01' 
                AND pr.{rating_col} IS NOT NULL
                AND pr.career_match_number >= 100
            ORDER BY pr.{rating_col} DESC
            LIMIT 10
        """)
        
        top_players = cursor.fetchall()
        output_path = output_dir / 'top10_current.csv'
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=top_players[0].keys())
            writer.writeheader()
            writer.writerows(top_players)
        logger.info(f"  ✅ {output_path}")
    
    # Export individual player trajectories
    players_to_export = ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer', 
                         'Carlos Alcaraz', 'Jannik Sinner']
    
    for player in players_to_export:
        with db.get_cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    p.name,
                    pr.career_match_number,
                    pr.date,
                    pr.{rating_col} as rating,
                    pr.{clay_col} as clay_rating,
                    pr.{grass_col} as grass_rating,
                    pr.{hard_col} as hard_rating
                FROM player_ratings pr
                JOIN players p ON pr.player_id = p.player_id
                WHERE p.name = %s AND pr.{rating_col} IS NOT NULL
                ORDER BY pr.career_match_number
            """, (player,))
            
            ratings = cursor.fetchall()
            if ratings:
                safe_name = player.lower().replace(' ', '_')
                output_path = output_dir / f'{safe_name}_career.csv'
                with open(output_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=ratings[0].keys())
                    writer.writeheader()
                    writer.writerows(ratings)
                logger.info(f"  ✅ {output_path}")


def main():
    """Main execution - export common visualizations"""
    logger.info("=" * 70)
    logger.info("EXPORT VISUALIZATION DATA")
    logger.info("=" * 70)
    
    db = DatabaseManager()
    
    # 1. Export Big 3 comparison
    logger.info("\n📊 Exporting Big 3 comparison...")
    export_multiple_players(
        db,
        ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer'],
        'big3_comparison.csv'
    )
    
    # 2. Export Next Gen comparison
    logger.info("\n📊 Exporting Next Gen comparison...")
    export_multiple_players(
        db,
        ['Carlos Alcaraz', 'Jannik Sinner', 'Holger Rune'],
        'nextgen_comparison.csv'
    )
    
    # 3. Export Big 3 vs Next Gen (at same career stage)
    logger.info("\n📊 Exporting Big 3 vs Next Gen...")
    export_multiple_players(
        db,
        ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer', 
         'Carlos Alcaraz', 'Jannik Sinner'],
        'big3_vs_nextgen.csv'
    )
    
    # 4. Export top 10 current players
    logger.info("\n📊 Exporting top 10 current players...")
    export_top_players(db, n=10, output_file='top10_current.csv')
    
    # 5. Export individual player trajectories
    logger.info("\n📊 Exporting individual player trajectories...")
    for player in ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer', 
                   'Carlos Alcaraz', 'Jannik Sinner']:
        safe_name = player.lower().replace(' ', '_')
        export_player_career_trajectory(
            db, 
            player, 
            f'{safe_name}_career.csv'
        )
    
    # 6. Export surface comparisons for Big 3
    logger.info("\n📊 Exporting surface comparisons...")
    for player in ['Novak Djokovic', 'Rafael Nadal', 'Roger Federer']:
        safe_name = player.lower().replace(' ', '_')
        export_surface_comparison(
            db,
            player,
            f'{safe_name}_surfaces.csv'
        )
    
    # 7. Export separate CSV files for each rating system
    logger.info("\n" + "=" * 70)
    logger.info("EXPORTING RATING SYSTEM-SPECIFIC CSVs")
    logger.info("=" * 70)
    
    export_rating_system_csvs(db, rating_type='elo')
    export_rating_system_csvs(db, rating_type='tsr')
    export_rating_system_csvs(db, rating_type='glicko2')
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ EXPORT COMPLETE!")
    logger.info("=" * 70)
    logger.info(f"\nAll files saved to: {PROCESSED_DATA_DIR}")
    logger.info("\nRating-specific CSVs in:")
    logger.info(f"  - {PROCESSED_DATA_DIR}/elo_only/")
    logger.info(f"  - {PROCESSED_DATA_DIR}/tsr_with_bayesian/")
    logger.info(f"  - {PROCESSED_DATA_DIR}/glicko2/")
    logger.info("\nYou can now:")
    logger.info("  1. Load these CSVs in Python/R for visualization")
    logger.info("  2. Import into Excel/Google Sheets")
    logger.info("  3. Use with Plotly/D3.js for interactive charts")
    logger.info("  4. Build your DARKO-style career progression charts!")
    logger.info("  5. Compare rating systems side-by-side!")


if __name__ == "__main__":
    main()

