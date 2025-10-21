import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { rankingsApi } from '../lib/api';
import { TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function RankingsPage() {
  const [system, setSystem] = useState<'elo' | 'tsr' | 'glicko2'>('elo');
  const [activeOnly, setActiveOnly] = useState(true);

  const { data, isLoading } = useQuery({
    queryKey: ['rankings', system, activeOnly],
    queryFn: () => rankingsApi.current({ 
      limit: 50, 
      system, 
      active: activeOnly 
    }).then(res => res.data),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <TrendingUp className="w-8 h-8 mr-3 text-primary-500" />
          Rankings
        </h1>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Rating System</label>
            <div className="flex space-x-2">
              {(['elo', 'tsr', 'glicko2'] as const).map(s => (
                <button
                  key={s}
                  onClick={() => setSystem(s)}
                  className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                    system === s 
                      ? 'bg-primary-600 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {s.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Players</label>
            <button
              onClick={() => setActiveOnly(!activeOnly)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                activeOnly 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {activeOnly ? 'Active Only' : 'All Players'}
            </button>
          </div>
        </div>
      </div>

      {/* Rankings Table */}
      <div className="card">
        {isLoading ? (
          <div className="text-center py-12 text-gray-400">Loading rankings...</div>
        ) : (
          <div className="space-y-2">
            {data?.rankings?.map((player: any, index: number) => (
              <Link
                key={player.name}
                to={`/players/${encodeURIComponent(player.name)}`}
                className="flex items-center justify-between p-4 bg-gray-700/30 hover:bg-gray-700 rounded-lg transition-colors group"
              >
                <div className="flex items-center space-x-4 flex-1">
                  <div className="w-12 text-center">
                    <span className={`font-bold text-lg ${
                      index === 0 ? 'text-yellow-500' :
                      index === 1 ? 'text-gray-400' :
                      index === 2 ? 'text-orange-600' :
                      'text-gray-500'
                    }`}>
                      {player.rank || index + 1}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold group-hover:text-primary-400 transition-colors">
                      {player.name}
                    </div>
                    {player.form_index && (
                      <div className="text-sm text-gray-400">
                        Form: {player.form_index}%
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-lg">{Math.round(player.rating)}</div>
                  <div className="text-xs text-gray-400 uppercase">{system}</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

