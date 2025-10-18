#!/usr/bin/env python3
"""
Analyze player dominance WITHIN their eras (not across eras).
This is the CORRECT way to compare Big 3 vs NextGen.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from datetime import datetime, timedelta


def analyze_era_dominance():
    """Calculate relative dominance within specific eras"""
    
    db = DatabaseManager()
    
    print("\n" + "=" * 100)
    print("ERA-ADJUSTED DOMINANCE ANALYSIS")
    print("=" * 100)
    print("This shows how much each player dominated THEIR OWN ERA")
    print("(Not direct ELO comparisons across time)")
    print("=" * 100)
    
    # Define eras
    eras = {
        'Big 3 Prime': ('2010-01-01', '2016-12-31'),
        'Big 3 Late': ('2017-01-01', '2022-12-31'),
        'NextGen': ('2023-01-01', '2025-12-31')
    }
    
    for era_name, (start_date, end_date) in eras.items():
        print(f"\n{'='*100}")
        print(f"📅 {era_name.upper()}: {start_date} to {end_date}")
        print(f"{'='*100}\n")
        
        with db.get_cursor() as cursor:
            # Get top 10 peak ratings in this era
            cursor.execute("""
                WITH era_peaks AS (
                    SELECT 
                        pl.name,
                        MAX(pr.elo_rating) as peak_elo,
                        MAX(pr.tsr_rating) as peak_tsr,
                        MAX(pr.glicko2_rating) as peak_glicko2,
                        COUNT(DISTINCT pr.match_id) as matches_in_era,
                        AVG(pr.elo_rating) as avg_elo,
                        AVG(pr.form_index) as avg_form,
                        AVG(pr.big_match_rating) as avg_big_match
                    FROM player_ratings pr
                    JOIN players pl ON pr.player_id = pl.player_id
                    WHERE pr.date BETWEEN %s AND %s
                      AND pr.elo_rating IS NOT NULL
                    GROUP BY pl.player_id, pl.name
                    HAVING COUNT(DISTINCT pr.match_id) >= 20  -- At least 20 matches in era
                ),
                era_stats AS (
                    SELECT 
                        AVG(peak_elo) as avg_top10_peak,
                        AVG(avg_elo) as avg_top10_avg
                    FROM (
                        SELECT peak_elo, avg_elo
                        FROM era_peaks
                        ORDER BY peak_elo DESC
                        LIMIT 10
                    ) top10
                )
                SELECT 
                    ep.name,
                    ROUND(ep.peak_elo::numeric, 2) as peak_elo,
                    ROUND(ep.avg_elo::numeric, 2) as avg_elo,
                    ROUND((ep.peak_elo - es.avg_top10_peak)::numeric, 2) as peak_vs_peers,
                    ROUND((ep.avg_elo - es.avg_top10_avg)::numeric, 2) as avg_vs_peers,
                    ep.matches_in_era,
                    ROUND(ep.avg_form::numeric, 2) as avg_form,
                    ROUND(ep.avg_big_match::numeric, 2) as avg_big_match
                FROM era_peaks ep
                CROSS JOIN era_stats es
                ORDER BY ep.peak_elo DESC
                LIMIT 15
            """, (start_date, end_date))
            
            results = cursor.fetchall()
            
            if not results:
                print(f"⚠️  No data available for {era_name}")
                continue
            
            # Print results
            print(f"{'Rank':<5} {'Player':<25} {'Peak ELO':<12} {'Δ vs Peers':<15} "
                  f"{'Matches':<10} {'Form%':<10} {'Big Match':<12}")
            print("-" * 100)
            
            for i, row in enumerate(results, 1):
                print(f"{i:<5} {row['name']:<25} {row['peak_elo']:<12} "
                      f"{'+' if row['peak_vs_peers'] > 0 else ''}{row['peak_vs_peers']:<14} "
                      f"{row['matches_in_era']:<10} {row['avg_form'] or 0:<10.1f} "
                      f"{row['avg_big_match'] or 0:<12.2f}")
            
            # Calculate dominance metrics
            if results:
                top_player = results[0]
                second_player = results[1] if len(results) > 1 else None
                
                print(f"\n{'─'*100}")
                print(f"📊 ERA DOMINANCE METRICS:")
                print(f"{'─'*100}")
                print(f"Most dominant: {top_player['name']}")
                print(f"  • Peak ELO: {top_player['peak_elo']}")
                print(f"  • Dominance over peers: +{top_player['peak_vs_peers']} ELO points")
                
                if second_player:
                    gap = top_player['peak_elo'] - second_player['peak_elo']
                    print(f"  • Gap to #2: {gap:.2f} ELO points")
                
                # Top 3 average
                top3_avg = sum(r['peak_elo'] for r in results[:3]) / 3
                print(f"  • Top 3 average: {top3_avg:.2f}")
                print(f"  • Top player advantage: +{(top_player['peak_elo'] - top3_avg):.2f} over top 3 avg")
    
    # Now compare dominance across eras
    print(f"\n\n{'='*100}")
    print("🏆 CROSS-ERA DOMINANCE COMPARISON")
    print("="*100)
    print("Who dominated their era the MOST? (Relative to their competition)")
    print("="*100 + "\n")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH era_definitions AS (
                SELECT 'Big 3 Prime' as era, '2010-01-01'::date as start_date, '2016-12-31'::date as end_date
                UNION ALL
                SELECT 'Big 3 Late', '2017-01-01'::date, '2022-12-31'::date
                UNION ALL
                SELECT 'NextGen', '2023-01-01'::date, '2025-12-31'::date
            ),
            player_era_peaks AS (
                SELECT 
                    ed.era,
                    pl.name,
                    MAX(pr.elo_rating) as peak_elo_in_era,
                    COUNT(DISTINCT pr.match_id) as matches,
                    AVG(pr.elo_rating) as avg_elo
                FROM era_definitions ed
                JOIN player_ratings pr ON pr.date BETWEEN ed.start_date AND ed.end_date
                JOIN players pl ON pr.player_id = pl.player_id
                WHERE pr.elo_rating IS NOT NULL
                GROUP BY ed.era, pl.player_id, pl.name
                HAVING COUNT(DISTINCT pr.match_id) >= 20
            ),
            era_averages AS (
                SELECT 
                    era,
                    AVG(peak_elo_in_era) as era_avg_peak
                FROM (
                    SELECT era, peak_elo_in_era
                    FROM player_era_peaks
                    ORDER BY era, peak_elo_in_era DESC
                ) sub
                GROUP BY era
            ),
            top_players_per_era AS (
                SELECT DISTINCT ON (pep.era)
                    pep.era,
                    pep.name,
                    pep.peak_elo_in_era,
                    ea.era_avg_peak,
                    pep.peak_elo_in_era - ea.era_avg_peak as dominance_over_era,
                    pep.matches
                FROM player_era_peaks pep
                JOIN era_averages ea ON pep.era = ea.era
                ORDER BY pep.era, pep.peak_elo_in_era DESC
            )
            SELECT *
            FROM top_players_per_era
            ORDER BY dominance_over_era DESC
        """)
        
        results = cursor.fetchall()
        
        print(f"{'Era':<20} {'Dominant Player':<25} {'Peak ELO':<12} {'Era Avg':<12} "
              f"{'Dominance':<15}")
        print("-" * 100)
        
        for row in results:
            print(f"{row['era']:<20} {row['name']:<25} {row['peak_elo_in_era']:<12.2f} "
                  f"{row['era_avg_peak']:<12.2f} +{row['dominance_over_era']:<14.2f}")
    
    print("\n" + "="*100)
    print("💡 KEY INSIGHT:")
    print("="*100)
    print("The player with the HIGHEST 'Dominance' score dominated their era the most,")
    print("regardless of absolute ELO numbers. This is the FAIR way to compare eras!")
    print("="*100 + "\n")


if __name__ == "__main__":
    analyze_era_dominance()

