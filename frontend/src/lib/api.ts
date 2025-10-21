import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Player {
  name: string;
  current_elo: number;
  peak_elo: number;
  career_matches: number;
  grand_slams: number;
  is_active: boolean;
  last_match: string;
}

export interface PlayerDetail extends Player {
  current_ratings: {
    elo: number;
    tsr: number;
    glicko2: number;
    form_index: number;
    big_match_rating: number | null;
  };
  career_stats: {
    total_matches: number;
    wins: number;
    losses: number;
    win_percentage: number;
  };
  peak_ratings: {
    peak_elo: number;
    peak_tsr: number;
    peak_glicko2: number;
  };
  surface_ratings: {
    clay: number;
    grass: number;
    hard: number;
  };
}

export interface MatchPrediction {
  player1: {
    name: string;
    current_elo: number;
    surface_elo: number;
    surface_record: string;
    form: number;
  };
  player2: {
    name: string;
    current_elo: number;
    surface_elo: number;
    surface_record: string;
    form: number;
  };
  surface: string;
  prediction: {
    player1_win_probability: number;
    player2_win_probability: number;
    confidence: string;
    expected_closeness: string;
  };
  factors: {
    elo_advantage: string;
    surface_advantage: string;
    form_advantage: string;
  };
  breakdown: {
    base_probability: number;
    surface_adjusted: number;
    form_adjusted: number;
    clamped: boolean;
  };
}

export interface StatOfDay {
  stat: string;
  category: string;
  players: string[];
  value?: number;
}

// API Functions
export const playerApi = {
  list: (params?: { limit?: number; offset?: number; active?: boolean; min_elo?: number }) =>
    api.get<{ total: number; players: Player[] }>('/api/players', { params }),
  
  get: (name: string) =>
    api.get<PlayerDetail>(`/api/players/${encodeURIComponent(name)}`),
  
  recent: (name: string, limit: number = 20) =>
    api.get(`/api/players/${encodeURIComponent(name)}/recent`, { params: { limit } }),
  
  titles: (name: string) =>
    api.get(`/api/players/${encodeURIComponent(name)}/titles`),
};

export const rankingsApi = {
  current: (params?: { limit?: number; system?: 'elo' | 'tsr' | 'glicko2'; active?: boolean }) =>
    api.get('/api/rankings/current', { params }),
  
  surface: (surface: 'clay' | 'grass' | 'hard', limit: number = 10, activeOnly: boolean = true) =>
    api.get(`/api/rankings/surface/${surface}`, { params: { limit, active_only: activeOnly } }),
};

export const predictApi = {
  match: (player1: string, player2: string, surface: 'clay' | 'grass' | 'hard') =>
    api.get<MatchPrediction>('/api/predict/match', {
      params: { player1, player2, surface }
    }),
};

export const dashboardApi = {
  statOfDay: () =>
    api.get<StatOfDay>('/api/dashboard/stat-of-day'),
  
  top10: () =>
    api.get('/api/dashboard/top10'),
};

export const h2hApi = {
  get: (player1: string, player2: string, surface?: string) =>
    api.get(`/api/h2h/${encodeURIComponent(player1)}/${encodeURIComponent(player2)}`, {
      params: surface ? { surface } : {}
    }),
};

