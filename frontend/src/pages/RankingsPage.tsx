import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api, type Player } from '../lib/api';


const RankingsPage: React.FC = () => {
  const [system, setSystem] = useState<'elo' | 'tsr' | 'glicko2'>('elo');
  const [surface, setSurface] = useState<'all' | 'hard' | 'clay' | 'grass'>('all');
  const [limit, setLimit] = useState(50);

  const { data: rankings, isLoading } = useQuery({
    queryKey: ['rankings', system, surface, limit],
    queryFn: () => {
      if (surface === 'all') {
        return api.getRankings({ 
          limit, 
          system, 
          active: true 
        });
      } else {
        return api.getSurfaceRankings(surface, { 
          limit, 
          active_only: true 
        });
      }
    },
  });

  const getRatingValue = (player: Player) => {
    // For surface-specific rankings, use surface_rating if available
    if (surface !== 'all' && 'surface_rating' in player) {
      return (player as any).surface_rating;
    }
    
    // For overall rankings, use the selected system
    switch (system) {
      case 'tsr': return player.tsr;
      case 'glicko2': return player.glicko2;
      default: return player.elo;
    }
  };

  const getSystemLabel = () => {
    // For surface-specific rankings, always show ELO since that's what surface rankings use
    if (surface !== 'all') {
      return 'ELO';
    }
    
    // For overall rankings, use the selected system
    switch (system) {
      case 'tsr': return 'TSR';
      case 'glicko2': return 'Glicko-2';
      default: return 'ELO';
    }
  };

  const getSurfaceIcon = (surface: string) => {
    switch (surface) {
      case 'clay': return '🟤';
      case 'grass': return '🟢';
      case 'hard': return '🔵';
      default: return '🏆';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <TrendingUp className="text-primary-500" />
            Rankings
          </h1>
          <p className="text-gray-400">
            Current player rankings across different rating systems and surfaces
          </p>
        </div>

        {/* Filters */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Rating System */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">Rating System</label>
              <div className="flex space-x-2">
                {(['elo', 'tsr', 'glicko2'] as const).map(s => (
                  <button
                    key={s}
                    onClick={() => setSystem(s)}
                    disabled={surface !== 'all'}
                    className={`px-3 py-2 rounded-lg text-sm font-semibold transition-colors ${
                      surface !== 'all' 
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : system === s 
                          ? 'bg-primary-500 text-white' 
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {s === 'elo' ? 'ELO' : s === 'tsr' ? 'TSR' : 'Glicko-2'}
                  </button>
                ))}
              </div>
              {surface !== 'all' && (
                <p className="text-xs text-gray-500 mt-1">Surface rankings use ELO only</p>
              )}
            </div>

            {/* Surface */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">Surface</label>
              <select
                value={surface}
                onChange={(e) => setSurface(e.target.value as 'all' | 'hard' | 'clay' | 'grass')}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              >
                <option value="all">🏆 All Surfaces</option>
                <option value="hard">🔵 Hard Court</option>
                <option value="clay">🟤 Clay Court</option>
                <option value="grass">🟢 Grass Court</option>
              </select>
            </div>

            {/* Limit */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">Show</label>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              >
                <option value={25}>Top 25</option>
                <option value={50}>Top 50</option>
                <option value={100}>Top 100</option>
              </select>
            </div>
          </div>
        </div>

        {/* Rankings Table */}
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-bold flex items-center gap-2">
              {getSurfaceIcon(surface)} {surface === 'all' ? 'Overall' : surface.charAt(0).toUpperCase() + surface.slice(1)} Rankings
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Ranked by {getSystemLabel()} rating system
            </p>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <div className="divide-y divide-gray-700">
              {rankings?.rankings?.map((player: Player, index: number) => (
                <Link
                  key={player.name}
                  to={`/players/${encodeURIComponent(player.name)}`}
                  className="flex items-center justify-between p-6 hover:bg-gray-750 transition-colors group"
                >
                  <div className="flex items-center space-x-6 flex-1">
                    {/* Rank */}
                    <div className="w-12 text-center">
                      <span className={`font-bold text-xl ${
                        index === 0 ? 'text-yellow-500' :
                        index === 1 ? 'text-gray-400' :
                        index === 2 ? 'text-orange-600' :
                        'text-gray-500'
                      }`}>
                        {player.rank || index + 1}
                      </span>
                    </div>

                    {/* Player Info */}
                    <div className="flex-1">
                      <div className="font-semibold text-lg group-hover:text-primary-400 transition-colors">
                        {player.name}
                      </div>
                      <div className="flex items-center gap-4 mt-1">
                        {player.form_index && (
                          <span className="text-sm text-gray-400">
                            Form: {player.form_index.toFixed(1)}%
                          </span>
                        )}
                        {player.big_match_rating && player.big_match_rating > 0 && (
                          <span className="text-sm text-gray-400">
                            Big Match: {player.big_match_rating.toFixed(0)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Rating */}
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary-500">
                      {Math.round(getRatingValue(player))}
                    </div>
                    <div className="text-xs text-gray-400 uppercase">{getSystemLabel()}</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Additional Info */}
        <div className="mt-8 bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="text-blue-400">ℹ️</div>
            <div>
              <h4 className="font-semibold text-blue-400 mb-1">About the Rankings</h4>
              <div className="text-blue-200 text-sm space-y-1">
                <p>
                  <strong>ELO:</strong> Traditional skill rating based on match results
                </p>
                <p>
                  <strong>TSR:</strong> Bayesian-adjusted rating considering experience and uncertainty
                </p>
                <p>
                  <strong>Glicko-2:</strong> Advanced rating system with volatility and deviation
                </p>
                <p>
                  <strong>Surface Rankings:</strong> Performance on specific court types over the last 2 years
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RankingsPage;