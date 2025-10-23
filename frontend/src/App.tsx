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
          {/* Main Content */}
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/rankings" element={
              <main className="container mx-auto px-4 py-8">
                <RankingsPage />
              </main>
            } />
            <Route path="/players" element={
              <main className="container mx-auto px-4 py-8">
                <PlayersPage />
              </main>
            } />
            <Route path="/players/:playerName" element={
              <main className="container mx-auto px-4 py-8">
                <PlayerDetailPage />
              </main>
            } />
            <Route path="/predict" element={
              <main className="container mx-auto px-4 py-8">
                <PredictPage />
              </main>
            } />
          </Routes>
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
