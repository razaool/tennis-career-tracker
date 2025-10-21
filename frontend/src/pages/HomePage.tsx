import { useQuery } from '@tanstack/react-query';
import { dashboardApi, rankingsApi } from '../lib/api';
import { TrendingUp, Users, Trophy, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function HomePage() {
  const { data: statOfDay } = useQuery({
    queryKey: ['statOfDay'],
    queryFn: () => dashboardApi.statOfDay().then(res => res.data),
  });

  const { data: top10 } = useQuery({
    queryKey: ['rankings', 'current', { limit: 10, system: 'elo' }],
    queryFn: () => rankingsApi.current({ limit: 10, system: 'elo' }).then(res => res.data),
  });

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4 py-12">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-tennis-green to-primary-500 bg-clip-text text-transparent">
          Tennis Career Tracker
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto">
          Analyzing 57 years of professional tennis • 740,000+ matches • 3 rating systems
        </p>
      </div>

      {/* Stat of the Day */}
      {statOfDay && (
        <div className="card bg-gradient-to-br from-gray-800 to-gray-900 border-primary-500/20">
          <div className="flex items-start space-x-4">
            <div className="bg-primary-500/10 p-3 rounded-lg">
              <Zap className="w-8 h-8 text-primary-500" />
            </div>
            <div className="flex-1">
              <h2 className="text-sm font-semibold text-primary-400 uppercase tracking-wide mb-2">
                Stat of the Day • {statOfDay.category}
              </h2>
              <p className="text-xl text-gray-100">{statOfDay.stat}</p>
              {statOfDay.players.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {statOfDay.players.map(player => (
                    <Link
                      key={player}
                      to={`/players/${encodeURIComponent(player)}`}
                      className="text-sm bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded-full transition-colors"
                    >
                      {player}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={<Trophy className="w-8 h-8" />}
          label="Total Matches"
          value="740,000+"
          color="text-yellow-500"
        />
        <StatCard
          icon={<Users className="w-8 h-8" />}
          label="Players Tracked"
          value="28,986"
          color="text-tennis-green"
        />
        <StatCard
          icon={<TrendingUp className="w-8 h-8" />}
          label="Rating Systems"
          value="3"
          subtitle="ELO • TSR • Glicko-2"
          color="text-primary-500"
        />
      </div>

      {/* Current Top 10 */}
      <div className="card">
        <h2 className="text-2xl font-bold mb-6 flex items-center">
          <Trophy className="w-6 h-6 mr-2 text-yellow-500" />
          Current Top 10 Rankings
        </h2>
        
        {top10 && (
          <div className="space-y-2">
            {top10.rankings?.map((player: any, index: number) => (
              <Link
                key={player.name}
                to={`/players/${encodeURIComponent(player.name)}`}
                className="flex items-center justify-between p-4 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors group"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-8 text-center">
                    <span className={`font-bold text-lg ${
                      index === 0 ? 'text-yellow-500' :
                      index === 1 ? 'text-gray-400' :
                      index === 2 ? 'text-orange-600' :
                      'text-gray-500'
                    }`}>
                      {index + 1}
                    </span>
                  </div>
                  <div>
                    <div className="font-semibold group-hover:text-primary-400 transition-colors">
                      {player.name}
                    </div>
                    {player.form && (
                      <div className="text-sm text-gray-400">
                        Form: {player.form}%
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-lg">{Math.round(player.rating)}</div>
                  <div className="text-xs text-gray-400">ELO</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <QuickLinkCard
          to="/rankings"
          icon={<TrendingUp className="w-8 h-8" />}
          title="Rankings"
          description="View current rankings by ELO, TSR, and Glicko-2"
        />
        <QuickLinkCard
          to="/players"
          icon={<Users className="w-8 h-8" />}
          title="Players"
          description="Browse player profiles and career statistics"
        />
        <QuickLinkCard
          to="/predict"
          icon={<Zap className="w-8 h-8" />}
          title="Match Predictor"
          description="Predict match outcomes with our AI model"
        />
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, subtitle, color }: any) {
  return (
    <div className="card">
      <div className="flex items-center space-x-4">
        <div className={`${color}`}>{icon}</div>
        <div>
          <div className="text-sm text-gray-400">{label}</div>
          <div className="text-2xl font-bold">{value}</div>
          {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
        </div>
      </div>
    </div>
  );
}

function QuickLinkCard({ to, icon, title, description }: any) {
  return (
    <Link
      to={to}
      className="card hover:border-primary-500/50 transition-all group cursor-pointer"
    >
      <div className="flex items-start space-x-4">
        <div className="text-primary-500 group-hover:scale-110 transition-transform">
          {icon}
        </div>
        <div>
          <h3 className="font-bold text-lg mb-1 group-hover:text-primary-400 transition-colors">
            {title}
          </h3>
          <p className="text-sm text-gray-400">{description}</p>
        </div>
      </div>
    </Link>
  );
}

