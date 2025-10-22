import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Users, Trophy, TrendingUp } from 'lucide-react';
import { api, type Player } from '../lib/api';


const PlayersPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState(true);
  const [minElo, setMinElo] = useState(2000);
  const [sortBy, setSortBy] = useState<'elo' | 'tsr' | 'glicko2'>('elo');
  const [currentPage, setCurrentPage] = useState(0);
  const playersPerPage = 20;

  const { data: players, isLoading, error } = useQuery({
    queryKey: ['players', activeFilter, minElo, sortBy, currentPage, playersPerPage],
    queryFn: () => api.getPlayers({
      limit: playersPerPage,
      offset: currentPage * playersPerPage,
      active: activeFilter,
      min_elo: minElo,
      sort_by: sortBy
    }),
  });

  const filteredPlayers = players?.filter((player: Player) =>
    player.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const getRatingValue = (player: Player) => {
    switch (sortBy) {
      case 'tsr': return player.tsr;
      case 'glicko2': return player.glicko2;
      default: return player.elo;
    }
  };

  const getRatingLabel = () => {
    switch (sortBy) {
      case 'tsr': return 'TSR';
      case 'glicko2': return 'Glicko-2';
      default: return 'ELO';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <Users className="text-primary-500" />
            Players
          </h1>
          <p className="text-gray-400">
            Explore {players?.length || 0}+ professional tennis players with detailed statistics
          </p>
        </div>

        {/* Filters */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search players..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              />
            </div>

            {/* Active Filter */}
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="active-filter"
                checked={activeFilter}
                onChange={(e) => setActiveFilter(e.target.checked)}
                className="w-4 h-4 text-primary-500 bg-gray-700 border-gray-600 rounded focus:ring-primary-500"
              />
              <label htmlFor="active-filter" className="text-sm text-gray-300">
                Active players only
              </label>
            </div>

            {/* Min ELO */}
            <div>
              <label className="block text-sm text-gray-300 mb-1">Min ELO</label>
              <select
                value={minElo}
                onChange={(e) => setMinElo(Number(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              >
                <option value={1500}>1500+</option>
                <option value={1800}>1800+</option>
                <option value={2000}>2000+</option>
                <option value={2200}>2200+</option>
                <option value={2400}>2400+</option>
              </select>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-sm text-gray-300 mb-1">Sort by</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'elo' | 'tsr' | 'glicko2')}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              >
                <option value="elo">ELO Rating</option>
                <option value="tsr">TSR Rating</option>
                <option value="glicko2">Glicko-2 Rating</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400">Error loading players. Please try again.</p>
          </div>
        ) : (
          <>
            {/* Stats Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center gap-3">
                  <TrendingUp className="text-primary-500 w-6 h-6" />
                  <div>
                    <p className="text-sm text-gray-400">Total Players</p>
                    <p className="text-2xl font-bold">{players?.length || 0}</p>
                  </div>
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center gap-3">
                  <Trophy className="text-yellow-500 w-6 h-6" />
                  <div>
                    <p className="text-sm text-gray-400">Active Players</p>
                    <p className="text-2xl font-bold">
                      {players?.filter((p: Player) => p.is_active).length || 0}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center gap-3">
                  <Users className="text-green-500 w-6 h-6" />
                  <div>
                    <p className="text-sm text-gray-400">Elite Players (2400+)</p>
                    <p className="text-2xl font-bold">
                      {players?.filter((p: Player) => p.elo >= 2400).length || 0}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Player Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredPlayers.map((player: Player) => (
                <div
                  key={player.name}
                  className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors cursor-pointer border border-gray-700 hover:border-primary-500"
                  onClick={() => window.location.href = `/players/${encodeURIComponent(player.name)}`}
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white">{player.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <div className={`w-2 h-2 rounded-full ${player.is_active ? 'bg-green-500' : 'bg-gray-500'}`}></div>
                        <span className="text-sm text-gray-400">
                          {player.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary-500">
                        {Math.round(getRatingValue(player))}
                      </div>
                      <div className="text-xs text-gray-400">{getRatingLabel()}</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Peak ELO:</span>
                      <span className="text-white">{Math.round(player.peak_elo)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Career Matches:</span>
                      <span className="text-white">{player.career_matches.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Grand Slams:</span>
                      <span className="text-white">{player.grand_slams}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Last Match:</span>
                      <span className="text-white">
                        {new Date(player.last_match).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Rating Comparison */}
                  <div className="mt-4 pt-4 border-t border-gray-700">
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div className="text-center">
                        <div className="text-gray-400">ELO</div>
                        <div className="font-semibold">{Math.round(player.elo)}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-gray-400">TSR</div>
                        <div className="font-semibold">{Math.round(player.tsr)}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-gray-400">Glicko-2</div>
                        <div className="font-semibold">{Math.round(player.glicko2)}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {players && players.length >= playersPerPage && (
              <div className="flex justify-center mt-8">
                <button
                  onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                  disabled={currentPage === 0}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed mr-2"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-gray-400">
                  Page {currentPage + 1}
                </span>
                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={players.length < playersPerPage}
                  className="px-4 py-2 bg-gray-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed ml-2"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default PlayersPage;