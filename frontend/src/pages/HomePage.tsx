import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { rankingsApi, playerApi } from '../lib/api';

export default function HomePage() {
  const [ratingSystem, setRatingSystem] = useState<'elo' | 'tsr' | 'glicko2'>('elo');

  // Fetch rankings data
  const { data: rankingsData, isLoading } = useQuery({
    queryKey: ['rankings', ratingSystem],
    queryFn: () => rankingsApi.current({ system: ratingSystem, limit: 25, active: true }),
  });

  const rankings = rankingsData?.rankings;

  // Fetch detailed player info and 2025 stats for top players
  const { data: playerDetails } = useQuery({
    queryKey: ['player-details', rankings?.slice(0, 25).map(p => p.name)],
    queryFn: async () => {
      if (!rankings) return {};
      const details: Record<string, any> = {};
      
      const topPlayers = rankings.slice(0, 25);
      const promises = topPlayers.map(async (player) => {
        try {
          const [playerDetail, yearStats] = await Promise.all([
            playerApi.get(player.name),
            playerApi.getCurrentYearStats(player.name, 2025)
          ]);
          details[player.name] = {
            ...playerDetail,
            year_2025_stats: yearStats.matches
          };
        } catch (error) {
          console.warn(`Failed to fetch details for ${player.name}:`, error);
        }
      });
      
      await Promise.all(promises);
      return details;
    },
    enabled: !!rankings && rankings.length > 0,
  });

  return (
    <div className="fixed inset-0 bg-black text-white w-full h-full">
      {/* Main Dashboard Grid */}
      <div className="h-full p-4 grid grid-cols-1 lg:grid-cols-12 auto-rows-fr lg:grid-rows-12 gap-4 overflow-y-auto">
        
        {/* Panel 1: Stat of the Day (Top Left) */}
        <div className="col-span-1 lg:col-span-4 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">1</h3>
        </div>

        {/* Panel 2: System Status (Top Center Left) */}
        <div className="col-span-1 lg:col-span-3 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">2</h3>
        </div>

        {/* Panel 3: Live Tournaments (Top Center Right) */}
        <div className="col-span-1 lg:col-span-3 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">3</h3>
        </div>

        {/* Panel 4: Recent Match Results (Top Right) */}
        <div className="col-span-1 lg:col-span-2 row-span-1 lg:row-span-1 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">4</h3>
        </div>

        {/* Panel 5: Player Rankings (Left Column - Tall) */}
        <div className="col-span-1 lg:col-span-4 row-span-1 lg:row-span-11 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex flex-col">
          {/* Header with title and rating system toggle */}
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">PLAYER RANKINGS</h3>
            <div className="flex gap-1">
              {(['elo', 'tsr', 'glicko2'] as const).map((system) => (
                <button
                  key={system}
                  onClick={() => setRatingSystem(system)}
                  className={`px-2 py-1 text-xs rounded-none border border-gray-700 transition-colors ${
                    ratingSystem === system
                      ? 'bg-white text-black border-white'
                      : 'bg-black text-gray-300 hover:bg-gray-800'
                  }`}
                >
                  {system.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Column headers */}
          <div className="flex items-center text-xs text-gray-400 mb-2 px-2 border-b border-gray-700 pb-1">
            <span className="w-8 text-center">#</span>
            <span className="flex-1 ml-2">PLAYER</span>
            <span className="w-14 text-center ml-2">RATING</span>
            {ratingSystem === 'tsr' && (
              <span className="w-14 text-center ml-2">UNCERT.</span>
            )}
            {ratingSystem === 'glicko2' && (
              <span className="w-14 text-center ml-2">RD</span>
            )}
            <span className="w-10 text-center ml-2">AGE</span>
            <span className="w-14 text-center ml-2">2025%</span>
          </div>
          
          {/* Player list */}
          <div className="flex-1 overflow-y-auto scrollbar-hide">
            {isLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-400">Loading...</div>
              </div>
            ) : rankings && rankings.length > 0 ? (
              <div className="space-y-1">
                {rankings?.slice(0, 25).map((player, index) => {
                  const rating = ratingSystem === 'elo' ? player.elo : 
                                ratingSystem === 'tsr' ? player.tsr : player.glicko2;
                  const details = playerDetails?.[player.name];
                  const age = details?.age || null;
                  const winPercentage2025 = details?.year_2025_stats?.win_percentage ? 
                    `${details.year_2025_stats.win_percentage.toFixed(1)}%` : 'N/A';
                  
                  return (
                    <div key={player.name} className="flex items-center py-2 px-2 hover:bg-gray-800 rounded-none border border-gray-700 bg-black text-sm transition-colors">
                      {/* Rank */}
                      <span className="w-8 text-center text-gray-400 text-xs">{player.rank || index + 1}</span>
                      
                      {/* Player name and country */}
                      <div className="flex-1 ml-2 min-w-0">
                        <div className="text-white font-medium truncate">{player.name}</div>
                        {details?.country && (
                          <div className="text-xs text-gray-500 truncate">{details.country}</div>
                        )}
                      </div>
                      
                      {/* Rating */}
                      <span className="w-14 text-center font-mono text-xs bg-gray-700 px-1 rounded ml-2">
                        {rating?.toFixed(0) || 'N/A'}
                      </span>
                      
                      {/* TSR Uncertainty Column (only shown when TSR is selected) */}
                      {ratingSystem === 'tsr' && (
                        <span className="w-14 text-center font-mono text-xs bg-gray-700 px-1 rounded ml-2">
                          {details?.current_metrics?.tsr_uncertainty ? `±${details.current_metrics.tsr_uncertainty.toFixed(0)}` : 'N/A'}
                        </span>
                      )}
                      
                      {/* Glicko-2 RD Column (only shown when Glicko-2 is selected) */}
                      {ratingSystem === 'glicko2' && (
                        <span className="w-14 text-center font-mono text-xs bg-gray-700 px-1 rounded ml-2">
                          {details?.current_metrics?.glicko_rd ? `±${details.current_metrics.glicko_rd.toFixed(0)}` : 'N/A'}
                        </span>
                      )}
                      
                      {/* Age */}
                      <span className="w-10 text-center text-gray-400 text-xs ml-2">
                        {age || 'N/A'}
                      </span>
                      
                      {/* 2025 Win % */}
                      <span className="w-14 text-center text-xs font-medium ml-2">
                        {winPercentage2025 === 'N/A' ? (
                          <span className="text-gray-500">{winPercentage2025}</span>
                        ) : (
                          <span className={
                            details?.year_2025_stats?.win_percentage >= 80 ? 'text-green-500' :
                            details?.year_2025_stats?.win_percentage >= 60 ? 'text-green-300' :
                            details?.year_2025_stats?.win_percentage >= 40 ? 'text-yellow-400' :
                            'text-red-500'
                          }>{winPercentage2025}</span>
                        )}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-gray-400 text-center">
                  <div>No rankings data available</div>
                  <div className="text-xs mt-1">Check API connection</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Panel 6: Season Completion Graph (Right Column - Tall) */}
        <div className="col-span-1 lg:col-span-8 row-span-1 lg:row-span-8 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">6</h3>
        </div>


        {/* Panel 7: Main Trajectory Chart (Bottom - Full Width) */}
        <div className="col-span-1 lg:col-span-8 lg:col-start-5 lg:row-start-10 row-span-1 lg:row-span-3 bg-black border border-gray-700 rounded-none p-3 overflow-hidden flex items-center justify-center">
          <h3 className="text-4xl font-bold text-white">7</h3>
        </div>
      </div>
    </div>
  );
}