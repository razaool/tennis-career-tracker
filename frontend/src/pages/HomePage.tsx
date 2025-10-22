import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, rankingsApi, apiClient } from '../lib/api';
import { BarChart3 } from 'lucide-react';
import { Link } from 'react-router-dom';
import TrajectoryChart from '../components/TrajectoryChart';

export default function HomePage() {
  const [selectedSystem, setSelectedSystem] = useState<'elo' | 'tsr' | 'glicko2'>('elo');
  const [selectedPlayers, setSelectedPlayers] = useState<string[]>([]);

  const { data: statOfDay } = useQuery({
    queryKey: ['statOfDay'],
    queryFn: () => dashboardApi.statOfDay(),
  });

  const { data: top10 } = useQuery({
    queryKey: ['rankings', 'current', { limit: 10, system: selectedSystem }],
    queryFn: () => rankingsApi.current({ limit: 10, system: selectedSystem }),
  });

  // Fetch trajectory data for selected players or top 5
  const { data: trajectoryData } = useQuery({
    queryKey: ['trajectory', selectedPlayers.length > 0 ? selectedPlayers : 'top5', selectedSystem],
    queryFn: () => {
      const players = selectedPlayers.length > 0 ? selectedPlayers : top10?.rankings?.slice(0, 5).map((p: any) => p.name) || [];
      if (players.length === 0) return null;
      return apiClient.comparePlayerTrajectories(players, undefined, undefined, selectedSystem);
    },
    enabled: !!top10?.rankings,
  });

  const handlePlayerSelect = (playerName: string) => {
    setSelectedPlayers(prev => {
      if (prev.includes(playerName)) {
        return prev.filter(p => p !== playerName);
      } else if (prev.length < 8) {
        return [...prev, playerName];
      }
      return prev;
    });
  };

  return (
    <div className="fixed inset-0 bg-black text-white w-full h-full overflow-hidden">
      {/* Top Bar */}
      <div className="flex justify-between items-center px-3 py-4 border-b border-gray-800">
        <div className="text-xl font-bold text-tennis-green">TENNIS CAREER TRACKER</div>
        <div className="text-sm text-gray-400">EXPERIMENTAL INTERFACE</div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel - Controls & Player List */}
        <div className="w-1/3 bg-gray-900 border-r border-gray-800 flex flex-col">
          {/* System Selection */}
          <div className="px-3 py-2 border-b border-gray-800">
            <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wide">RATING SYSTEM</h3>
            <div className="flex space-x-2">
              {(['elo', 'tsr', 'glicko2'] as const).map(system => (
                <button
                  key={system}
                  onClick={() => setSelectedSystem(system)}
                  className={`px-4 py-2 rounded text-sm font-semibold transition-colors ${
                    selectedSystem === system
                      ? 'bg-tennis-green text-black'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {system === 'elo' ? 'ELO' : system === 'tsr' ? 'TSR' : 'GLICKO-2'}
                </button>
              ))}
            </div>
          </div>

          {/* Stats Summary */}
          <div className="px-3 py-2 border-b border-gray-800">
            <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wide">MAIN METRICS</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">PLAYERS</span>
                <span className="text-2xl font-bold text-tennis-green">28,986</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">TOTAL MATCHES</span>
                <span className="text-2xl font-bold text-tennis-green">740,000+</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400 text-sm">RATING SYSTEMS</span>
                <span className="text-2xl font-bold text-tennis-green">3</span>
              </div>
            </div>
          </div>

          {/* Player Selection */}
          <div className="flex-1 px-3 py-2 overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wide">
              PLAYER SELECTION ({selectedPlayers.length}/8)
            </h3>
            
            {top10 && (
              <div className="space-y-2">
                {top10.rankings?.map((player: any, index: number) => (
                  <div
                    key={player.name}
                    className={`p-3 rounded cursor-pointer transition-colors ${
                      selectedPlayers.includes(player.name)
                        ? 'bg-tennis-green text-black'
                        : 'bg-gray-800 hover:bg-gray-700'
                    }`}
                    onClick={() => handlePlayerSelect(player.name)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className={`font-bold text-sm ${
                          selectedPlayers.includes(player.name) ? 'text-black' : 'text-gray-400'
                        }`}>
                          {index + 1}
                        </span>
                        <div>
                          <div className={`font-semibold text-sm ${
                            selectedPlayers.includes(player.name) ? 'text-black' : 'text-white'
                          }`}>
                            {player.name}
                          </div>
                          <div className={`text-xs ${
                            selectedPlayers.includes(player.name) ? 'text-gray-700' : 'text-gray-400'
                          }`}>
                            {selectedSystem === 'elo' ? Math.round(player.elo || 0) :
                             selectedSystem === 'tsr' ? Math.round(player.tsr || 0) :
                             Math.round(player.glicko2 || 0)} {selectedSystem.toUpperCase()}
                          </div>
                        </div>
                      </div>
                      {selectedPlayers.includes(player.name) && (
                        <div className="w-2 h-2 bg-black rounded-full"></div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Stat of the Day */}
          {statOfDay && (
            <div className="px-3 py-2 border-t border-gray-800">
              <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wide">STAT OF THE DAY</h3>
              <div className="bg-gray-800 rounded p-4">
                <div className="text-xs text-tennis-green uppercase tracking-wide mb-2">{statOfDay.category}</div>
                <p className="text-sm text-gray-200 leading-relaxed">{statOfDay.stat}</p>
                {statOfDay.players.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {statOfDay.players.map((player: string) => (
                      <Link
                        key={player}
                        to={`/players/${encodeURIComponent(player)}`}
                        className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded transition-colors"
                      >
                        {player}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Main Chart */}
        <div className="flex-1 bg-black flex flex-col">
          {/* Chart Header */}
          <div className="px-3 py-2 border-b border-gray-800">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white mb-2">LIVE CAREER PROGRESSION</h2>
                <p className="text-sm text-gray-400">
                  {selectedPlayers.length > 0 
                    ? `Tracking ${selectedPlayers.length} selected players` 
                    : 'Top 5 players by current ranking'
                  } • {selectedSystem.toUpperCase()} Rating System
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-400">
                  <span className="text-tennis-green">●</span> LIVE
                </div>
                <div className="text-sm text-gray-400">
                  {trajectoryData?.players.reduce((sum, p) => sum + p.data_points, 0) || 0} DATA POINTS
                </div>
              </div>
            </div>
          </div>

          {/* Chart Area */}
          <div className="flex-1 px-3 py-2">
            {trajectoryData && trajectoryData.players.length > 0 ? (
              <TrajectoryChart
                data={trajectoryData.players}
                ratingSystem={selectedSystem}
                title=""
                height={600}
              />
            ) : (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-800 rounded-full flex items-center justify-center">
                    <BarChart3 className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-300 mb-2">No Data Available</h3>
                  <p className="text-sm text-gray-500">Select players from the left panel to view their career progression</p>
                </div>
              </div>
            )}
          </div>

          {/* Bottom Controls */}
          <div className="px-3 py-2 border-t border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="text-sm text-gray-400">
                  <span className="text-tennis-green">●</span> RUNNING
                </div>
                <div className="flex space-x-2">
                  <button className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors">
                    REFRESH
                  </button>
                  <button className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors">
                    EXPORT
                  </button>
                </div>
              </div>
              <div className="text-xs text-gray-500">
                TENNIS CAREER TRACKER • 2025 DATA
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}