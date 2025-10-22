import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Trophy, TrendingUp, Calendar, Target } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api, type RecentMatch } from '../lib/api';

const PlayerDetailPage: React.FC = () => {
  const { playerName } = useParams<{ playerName: string }>();
  const navigate = useNavigate();
  const [ratingSystem, setRatingSystem] = useState<'elo' | 'tsr' | 'glicko2'>('elo');

  const { data: player, isLoading: playerLoading, error: playerError } = useQuery({
    queryKey: ['player', playerName],
    queryFn: () => api.getPlayer(playerName!),
    enabled: !!playerName,
  });

  const { data: trajectory } = useQuery({
    queryKey: ['trajectory', playerName],
    queryFn: () => api.getPlayerTrajectory(playerName!, '2020-01-01', '2025-12-31', ratingSystem),
    enabled: !!playerName,
  });

  const { data: recentMatches } = useQuery({
    queryKey: ['recent-matches', playerName],
    queryFn: () => api.getPlayerRecentMatches(playerName!, 10),
    enabled: !!playerName,
  });

  if (playerLoading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (playerError || !player) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Player Not Found</h1>
          <p className="text-gray-400 mb-6">The player "{playerName}" could not be found.</p>
          <button
            onClick={() => navigate('/players')}
            className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Back to Players
          </button>
        </div>
      </div>
    );
  }

  const getRatingValue = () => {
    switch (ratingSystem) {
      case 'tsr': return player.tsr;
      case 'glicko2': return player.glicko2;
      default: return player.elo;
    }
  };

  const getRatingLabel = () => {
    switch (ratingSystem) {
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
          <button
            onClick={() => navigate('/players')}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Players
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">{player.name}</h1>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${player.is_active ? 'bg-green-500' : 'bg-gray-500'}`}></div>
                  <span className="text-gray-400">
                    {player.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <span className="text-gray-400">
                  Last match: {new Date(player.last_match).toLocaleDateString()}
                </span>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-4xl font-bold text-primary-500">
                {Math.round(getRatingValue())}
              </div>
              <div className="text-gray-400">{getRatingLabel()} Rating</div>
            </div>
          </div>
        </div>

        {/* Rating System Selector */}
        <div className="bg-gray-800 rounded-lg p-4 mb-8">
          <div className="flex gap-4">
            {(['elo', 'tsr', 'glicko2'] as const).map((system) => (
              <button
                key={system}
                onClick={() => setRatingSystem(system)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  ratingSystem === system
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {system === 'elo' ? 'ELO' : system === 'tsr' ? 'TSR' : 'Glicko-2'}
              </button>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <Trophy className="text-yellow-500 w-6 h-6" />
              <span className="text-gray-400">Career Record</span>
            </div>
            <div className="text-2xl font-bold">
              {player.wins}-{player.losses}
            </div>
            <div className="text-sm text-gray-400">
              {player.win_percentage.toFixed(1)}% win rate
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="text-blue-500 w-6 h-6" />
              <span className="text-gray-400">Total Matches</span>
            </div>
            <div className="text-2xl font-bold">
              {player.career_matches.toLocaleString()}
            </div>
            <div className="text-sm text-gray-400">
              {player.grand_slams} Grand Slams
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="text-green-500 w-6 h-6" />
              <span className="text-gray-400">Current Form</span>
            </div>
            <div className="text-2xl font-bold">
              {player.form_index.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400">
              Last 20 matches
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-2">
              <Target className="text-red-500 w-6 h-6" />
              <span className="text-gray-400">Big Match Rating</span>
            </div>
            <div className="text-2xl font-bold">
              {player.big_match_rating ? player.big_match_rating.toFixed(0) : 'N/A'}
            </div>
            <div className="text-sm text-gray-400">
              vs Elite opponents
            </div>
          </div>
        </div>

        {/* Rating Comparison */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h3 className="text-xl font-bold mb-4">Rating Systems Comparison</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-500 mb-1">
                {Math.round(player.elo)}
              </div>
              <div className="text-gray-400">ELO Rating</div>
              <div className="text-sm text-gray-500">
                Peak: {Math.round(player.peak_elo)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-500 mb-1">
                {Math.round(player.tsr)}
              </div>
              <div className="text-gray-400">TSR Rating</div>
              <div className="text-sm text-gray-500">
                Bayesian adjusted
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-500 mb-1">
                {Math.round(player.glicko2)}
              </div>
              <div className="text-gray-400">Glicko-2 Rating</div>
              <div className="text-sm text-gray-500">
                Uncertainty aware
              </div>
            </div>
          </div>
        </div>

        {/* Rating Trajectory Chart */}
        {trajectory && trajectory.length > 0 && (
          <div className="bg-gray-800 rounded-lg p-6 mb-8">
            <h3 className="text-xl font-bold mb-4">Rating Trajectory</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trajectory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#9CA3AF"
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <Line 
                    type="monotone" 
                    dataKey={ratingSystem} 
                    stroke="#0EA5E9" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Recent Matches */}
        {recentMatches && recentMatches.length > 0 && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Recent Matches</h3>
            <div className="space-y-3">
              {recentMatches.map((match: RecentMatch, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className={`w-3 h-3 rounded-full ${match.won ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <div>
                      <div className="font-semibold">
                        {match.won ? 'W' : 'L'} vs {match.opponent}
                      </div>
                      <div className="text-sm text-gray-400">
                        {match.tournament} • {match.surface}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">
                      {new Date(match.date).toLocaleDateString()}
                    </div>
                    <div className="text-sm">
                      ELO: {Math.round(match.elo_before)} → {Math.round(match.elo_after)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerDetailPage;