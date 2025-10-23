import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, rankingsApi, apiClient } from '../lib/api';
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
      {/* Top Header */}
      <div className="flex justify-between items-center px-6 py-4 border-b border-gray-800 bg-gray-900">
        <div className="text-2xl font-bold text-tennis-green">TENNIS CAREER TRACKER</div>
        <div className="text-sm text-gray-400">EXPERIMENTAL INTERFACE</div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="h-[calc(100vh-80px)] p-4 grid grid-cols-12 grid-rows-12 gap-4">
        
        {/* Panel 1: Stat of the Day (Left Column - Top) */}
        <div className="col-span-4 row-span-3 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">STAT OF THE DAY</h3>
          {statOfDay && (
            <div className="space-y-2 h-full overflow-hidden">
              <div className="text-xs text-tennis-green uppercase tracking-wide">{statOfDay.category}</div>
              <p className="text-sm text-gray-200 leading-relaxed line-clamp-3">{statOfDay.stat}</p>
              {statOfDay.players.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {statOfDay.players.map((player: string) => (
                    <Link
                      key={player}
                      to={`/players/${encodeURIComponent(player)}`}
                      className="text-xs bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded-full transition-colors text-gray-300"
                    >
                      {player}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Panel 2: System Status (Left Column - Middle) */}
        <div className="col-span-4 row-span-3 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">SYSTEM STATUS</h3>
          <div className="space-y-2 h-full">
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">ACTIVE PLAYERS</span>
              <span className="text-lg font-bold text-tennis-green">1,247</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">TOTAL MATCHES</span>
              <span className="text-lg font-bold text-tennis-green">740,000+</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">RATING SYSTEMS</span>
              <span className="text-lg font-bold text-tennis-green">3</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400 text-sm">LAST UPDATE</span>
              <span className="text-sm text-gray-300">2 min ago</span>
            </div>
          </div>
        </div>

        {/* Panel 3: Season Completion Graph (Left Column - Bottom) */}
        <div className="col-span-4 row-span-6 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">SEASON COMPLETION</h3>
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-2xl font-bold text-tennis-green mb-2">75%</div>
              <div className="text-sm text-gray-400">Tournaments Completed</div>
              <div className="w-full bg-gray-700 rounded-full h-2 mt-3">
                <div className="bg-tennis-green h-2 rounded-full" style={{ width: '75%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Panel 4: Live Tournaments (Top Right) */}
        <div className="col-span-4 row-span-3 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">LIVE TOURNAMENTS</h3>
          <div className="space-y-1 h-full overflow-y-auto">
            <div className="text-sm text-gray-400">Australian Open 2025</div>
            <div className="text-sm text-gray-400">French Open 2025</div>
            <div className="text-sm text-gray-400">Wimbledon 2025</div>
            <div className="text-sm text-gray-400">US Open 2025</div>
          </div>
        </div>

        {/* Panel 5: Recent Match Results (Middle Right) */}
        <div className="col-span-4 row-span-3 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">RECENT MATCH RESULTS</h3>
          <div className="space-y-1 h-full overflow-y-auto">
            <div className="text-sm text-gray-400">Alcaraz def. Sinner 6-4, 6-2</div>
            <div className="text-sm text-gray-400">Djokovic def. Nadal 7-6, 6-3</div>
            <div className="text-sm text-gray-400">Fritz def. Zverev 6-2, 6-4</div>
            <div className="text-sm text-gray-400">Medvedev def. Tsitsipas 6-1, 6-3</div>
            <div className="text-sm text-gray-400">Rublev def. Ruud 6-4, 6-2</div>
          </div>
        </div>

        {/* Panel 6: Player Rankings (Bottom Right) */}
        <div className="col-span-4 row-span-9 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">PLAYER RANKINGS</h3>
            <div className="flex space-x-1">
              {(['elo', 'tsr', 'glicko2'] as const).map(system => (
                <button
                  key={system}
                  onClick={() => setSelectedSystem(system)}
                  className={`px-2 py-1 rounded text-xs font-semibold transition-colors ${
                    selectedSystem === system 
                      ? 'bg-tennis-green text-gray-900' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {system.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          <div className="space-y-1 h-[calc(100%-40px)] overflow-y-auto">
            {top10?.rankings?.slice(0, 10).map((player: any, index: number) => (
              <div
                key={player.name}
                onClick={() => handlePlayerSelect(player.name)}
                className={`flex items-center justify-between p-2 rounded cursor-pointer transition-colors ${
                  selectedPlayers.includes(player.name)
                    ? 'bg-tennis-green/20 border border-tennis-green text-tennis-green'
                    : 'bg-gray-800 hover:bg-gray-700 border border-gray-800'
                }`}
              >
                <div className="flex items-center space-x-2 min-w-0">
                  <span className="text-gray-500 text-sm w-4">{index + 1}</span>
                  <span className="text-sm font-medium truncate">{player.name}</span>
                </div>
                <span className="text-xs text-gray-400 flex-shrink-0">
                  {selectedSystem === 'elo' ? Math.round(player.elo || 0) :
                   selectedSystem === 'tsr' ? Math.round(player.tsr || 0) :
                   Math.round(player.glicko2 || 0)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Panel 7: Main Trajectory Chart (Center - Large) */}
        <div className="col-span-8 row-span-6 col-start-5 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <div className="h-full">
            {trajectoryData && trajectoryData.players.length > 0 ? (
              <div className="w-full h-full">
                <TrajectoryChart
                  data={trajectoryData.players}
                  ratingSystem={selectedSystem}
                  title=""
                  height={250}
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 text-lg">
                Loading trajectory data...
              </div>
            )}
          </div>
        </div>

        {/* Panel 8: Quick Actions/Controls (Bottom Center) */}
        <div className="col-span-8 row-span-3 col-start-5 bg-gray-900 border border-gray-700 rounded-lg p-3 overflow-hidden">
          <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wide">QUICK ACTIONS</h3>
          <div className="flex items-center justify-center h-full pb-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-400">RATING SYSTEM:</span>
                <div className="flex space-x-1">
                  {(['elo', 'tsr', 'glicko2'] as const).map(system => (
                    <button
                      key={system}
                      onClick={() => setSelectedSystem(system)}
                      className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                        selectedSystem === system 
                          ? 'bg-tennis-green text-gray-900' 
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {system.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
              <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded transition-colors">
                REFRESH DATA
              </button>
              <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded transition-colors">
                EXPORT REPORT
              </button>
              <div className="text-sm text-gray-400">
                <span className="text-tennis-green">●</span> RUNNING
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}