import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Player {
  name: string;
  elo: number;
  tsr: number;
  glicko2: number;
  peak_elo: number;
  career_matches: number;
  grand_slams: number;
  is_active: boolean;
  last_match: string;
  form_index?: number;
  big_match_rating?: number;
  rank?: number;
}

export interface PlayerDetail {
  name: string;
  elo: number;
  tsr: number;
  glicko2: number;
  peak_elo: number;
  career_matches: number;
  grand_slams: number;
  wins: number;
  losses: number;
  win_percentage: number;
  form_index: number;
  big_match_rating: number;
  tournament_success_score: number;
  is_active: boolean;
  last_match: string;
}

export interface TrajectoryPoint {
  match_number: number;
  date: string;
  rating: number;
}

export interface RecentMatch {
  date: string;
  opponent: string;
  tournament: string;
  surface: string;
  won: boolean;
  elo_before: number;
  elo_after: number;
}

export interface MatchPrediction {
  player1: string;
  player2: string;
  surface: string;
  prediction: {
    winner: string;
    probability: number;
    confidence: string;
  };
  factors: {
    elo_difference: number;
    surface_advantage: number;
    form_advantage: number;
    big_match_experience: number;
  };
  breakdown: {
    base_probability: number;
    surface_adjusted: number;
    form_adjusted: number;
    clamped: boolean;
  };
  note: string;
}

export interface StatOfDay {
  stat: string;
  category: string;
  players: string[];
  value?: number;
}

export interface RankingsResponse {
  rankings: Player[];
  total: number;
}

// API Functions
export const apiClient = {
  // Players
  getPlayers: (params?: { 
    limit?: number; 
    offset?: number; 
    active?: boolean; 
    min_elo?: number; 
    sort_by?: 'elo' | 'tsr' | 'glicko2' 
  }) =>
    axiosInstance.get<Player[]>('/api/players', { params }).then(res => res.data),
  
  getPlayer: (name: string) =>
    axiosInstance.get<PlayerDetail>(`/api/players/${encodeURIComponent(name)}`).then(res => res.data),
  
  getPlayerTrajectory: (
    name: string, 
    startDate: string, 
    endDate: string, 
    ratingSystem: 'elo' | 'tsr' | 'glicko2'
  ) =>
    axiosInstance.get<TrajectoryPoint[]>(`/api/players/compare/trajectory`, {
      params: { 
        players: name, 
        start_date: startDate, 
        end_date: endDate, 
        rating_system: ratingSystem 
      }
    }).then(res => res.data),
  
  comparePlayerTrajectories: (
    players: string[], 
    startDate?: string, 
    endDate?: string, 
    ratingSystem: 'elo' | 'tsr' | 'glicko2' = 'elo'
  ) =>
    axiosInstance.get<{
      rating_system: string;
      date_range: { start?: string; end?: string };
      players: Array<{
        name: string;
        data_points: number;
        trajectory: TrajectoryPoint[];
      }>;
    }>(`/api/players/compare/trajectory`, {
      params: { 
        players: players.join(','), 
        start_date: startDate, 
        end_date: endDate, 
        rating_system: ratingSystem 
      }
    }).then(res => res.data),
  
  getPlayerRecentMatches: (name: string, limit: number = 10) =>
    axiosInstance.get<RecentMatch[]>(`/api/players/${encodeURIComponent(name)}/recent`, { 
      params: { limit } 
    }).then(res => res.data),

  // Rankings
  getRankings: (params?: { 
    limit?: number; 
    system?: 'elo' | 'tsr' | 'glicko2'; 
    active?: boolean 
  }) =>
    axiosInstance.get<RankingsResponse>('/api/rankings/current', { params }).then(res => res.data),
  
  getSurfaceRankings: (
    surface: 'clay' | 'grass' | 'hard', 
    params?: { limit?: number; active_only?: boolean }
  ) =>
    axiosInstance.get<RankingsResponse>(`/api/rankings/surface/${surface}`, { params }).then(res => res.data),

  // Predictions
  predictMatch: (player1: string, player2: string, surface: 'clay' | 'grass' | 'hard') =>
    axiosInstance.get<MatchPrediction>('/api/predict/match', {
      params: { player1, player2, surface }
    }).then(res => res.data),

  // Dashboard
  getStatOfDay: () =>
    axiosInstance.get<StatOfDay>('/api/dashboard/stat-of-day').then(res => res.data),
  
  getTop10: () =>
    axiosInstance.get<Player[]>('/api/rankings/current', { 
      params: { limit: 10, system: 'elo' } 
    }).then(res => res.data),

  // Head-to-Head
  getH2H: (player1: string, player2: string, surface?: string) =>
    axiosInstance.get(`/api/h2h/${encodeURIComponent(player1)}/${encodeURIComponent(player2)}`, {
      params: surface ? { surface } : {}
    }).then(res => res.data),
};

export const playerApi = {
  list: (params?: { limit?: number; offset?: number; active?: boolean; min_elo?: number }) =>
    apiClient.getPlayers(params),
  
  get: (name: string) =>
    apiClient.getPlayer(name),
  
  recent: (name: string, limit: number = 20) =>
    apiClient.getPlayerRecentMatches(name, limit),
  
  titles: (name: string) =>
    axiosInstance.get(`/api/players/${encodeURIComponent(name)}/titles`).then(res => res.data),
};

export const rankingsApi = {
  current: (params?: { limit?: number; system?: 'elo' | 'tsr' | 'glicko2'; active?: boolean }) =>
    apiClient.getRankings(params),
  
  surface: (surface: 'clay' | 'grass' | 'hard', limit: number = 10, activeOnly: boolean = true) =>
    apiClient.getSurfaceRankings(surface, { limit, active_only: activeOnly }),
};

export const predictApi = {
  match: (player1: string, player2: string, surface: 'clay' | 'grass' | 'hard') =>
    apiClient.predictMatch(player1, player2, surface),
};

export const dashboardApi = {
  statOfDay: () =>
    apiClient.getStatOfDay(),
  
  top10: () =>
    apiClient.getTop10(),
};

export const h2hApi = {
  get: (player1: string, player2: string, surface?: string) =>
    apiClient.getH2H(player1, player2, surface),
};

// Main API export for backward compatibility
export const api = apiClient;