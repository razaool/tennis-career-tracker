import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Home, Trophy, Users, TrendingUp, Swords } from 'lucide-react';
import HomePage from './pages/HomePage';
import RankingsPage from './pages/RankingsPage';
import PlayersPage from './pages/PlayersPage';
import PredictPage from './pages/PredictPage';
import PlayerDetailPage from './pages/PlayerDetailPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-900 text-gray-100">
          {/* Navigation */}
          <nav className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
            <div className="container mx-auto px-4">
              <div className="flex items-center justify-between h-16">
                <Link to="/" className="flex items-center space-x-2">
                  <Trophy className="w-8 h-8 text-tennis-green" />
                  <span className="text-xl font-bold">Tennis Career Tracker</span>
                </Link>
                
                <div className="flex space-x-1">
                  <NavLink to="/" icon={<Home size={18} />} label="Home" />
                  <NavLink to="/rankings" icon={<TrendingUp size={18} />} label="Rankings" />
                  <NavLink to="/players" icon={<Users size={18} />} label="Players" />
                  <NavLink to="/predict" icon={<Swords size={18} />} label="Predict" />
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/rankings" element={<RankingsPage />} />
              <Route path="/players" element={<PlayersPage />} />
              <Route path="/players/:playerName" element={<PlayerDetailPage />} />
              <Route path="/predict" element={<PredictPage />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="bg-gray-800 border-t border-gray-700 mt-16">
            <div className="container mx-auto px-4 py-6 text-center text-gray-400 text-sm">
              <p>Tennis Career Tracker • 1968-2025 • 740K+ Matches</p>
            </div>
          </footer>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

function NavLink({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </Link>
  );
}

export default App;
