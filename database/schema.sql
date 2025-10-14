-- Tennis Career Tracker Database Schema
-- PostgreSQL 14+

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS player_ratings CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS tournament_tiers CASCADE;

-- Players table
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    date_of_birth DATE,
    country VARCHAR(3),
    hand VARCHAR(10),  -- L, R, or U (unknown)
    height_cm INT,
    turned_pro INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tournament tiers lookup table
CREATE TABLE tournament_tiers (
    tier_name VARCHAR(50) PRIMARY KEY,
    weight FLOAT NOT NULL,
    importance_score INT NOT NULL,
    description TEXT
);

-- Insert tournament tier data
INSERT INTO tournament_tiers (tier_name, weight, importance_score, description) VALUES
    ('Grand Slam', 2.0, 100, 'Australian Open, French Open, Wimbledon, US Open'),
    ('ATP Finals', 1.8, 90, 'Year-end championship'),
    ('Masters 1000', 1.5, 80, 'Masters 1000 events'),
    ('Masters', 1.5, 80, 'Masters events (legacy name)'),
    ('ATP 500', 1.2, 60, 'ATP 500 series'),
    ('ATP 250', 1.0, 40, 'ATP 250 series'),
    ('Davis Cup', 1.3, 70, 'Davis Cup matches'),
    ('Olympics', 1.6, 85, 'Olympic Games'),
    ('Challenger', 0.8, 30, 'Challenger tour events'),
    ('ITF', 0.6, 20, 'ITF tournaments');

-- Matches table (core data)
CREATE TABLE matches (
    match_id SERIAL PRIMARY KEY,
    
    -- Match identification
    tourney_id VARCHAR(50),  -- From Tennis Abstract
    match_num INT,  -- Match number within tournament
    
    -- Date and tournament info
    date DATE NOT NULL,
    tournament_name VARCHAR(255),
    tournament_tier VARCHAR(50) REFERENCES tournament_tiers(tier_name),
    surface VARCHAR(20),  -- clay, grass, hard, carpet
    round VARCHAR(50),  -- R128, R64, R32, R16, QF, SF, F
    best_of INT,  -- 3 or 5
    
    -- Players
    player1_id INT REFERENCES players(player_id),
    player2_id INT REFERENCES players(player_id),
    winner_id INT REFERENCES players(player_id),
    
    -- Rankings at time of match
    player1_rank INT,
    player2_rank INT,
    player1_rank_points INT,
    player2_rank_points INT,
    
    -- Score data
    score VARCHAR(100),
    player1_sets_won INT,
    player2_sets_won INT,
    player1_games_won INT,
    player2_games_won INT,
    
    -- Match statistics (optional, for future enhancement)
    player1_aces INT,
    player2_aces INT,
    player1_double_faults INT,
    player2_double_faults INT,
    player1_first_serve_pct FLOAT,
    player2_first_serve_pct FLOAT,
    player1_break_points_saved FLOAT,
    player2_break_points_saved FLOAT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT different_players CHECK (player1_id != player2_id),
    CONSTRAINT valid_winner CHECK (winner_id IN (player1_id, player2_id)),
    CONSTRAINT valid_surface CHECK (surface IN ('clay', 'grass', 'hard', 'carpet', 'none'))
);

-- Create indexes for matches table
CREATE INDEX idx_matches_date ON matches(date);
CREATE INDEX idx_matches_player1 ON matches(player1_id);
CREATE INDEX idx_matches_player2 ON matches(player2_id);
CREATE INDEX idx_matches_winner ON matches(winner_id);
CREATE INDEX idx_matches_surface ON matches(surface);
CREATE INDEX idx_matches_tournament ON matches(tournament_name);
CREATE INDEX idx_matches_tier ON matches(tournament_tier);
CREATE INDEX idx_matches_date_surface ON matches(date, surface);
CREATE INDEX idx_matches_player1_date ON matches(player1_id, date);
CREATE INDEX idx_matches_player2_date ON matches(player2_id, date);

-- Player ratings table (output of Bayesian model)
CREATE TABLE player_ratings (
    rating_id SERIAL PRIMARY KEY,
    player_id INT REFERENCES players(player_id),
    match_id INT REFERENCES matches(match_id),
    
    -- Timeline
    date DATE NOT NULL,
    career_match_number INT,  -- Nth match in player's career
    age_days INT,  -- Age in days at time of match
    
    -- Core rating (Tennis Skill Rating)
    tsr_rating FLOAT,  -- Main composite rating
    tsr_uncertainty FLOAT,  -- Bayesian uncertainty (standard deviation)
    tsr_smoothed FLOAT,  -- Gaussian Process smoothed value
    
    -- Surface-specific ratings
    clay_rating FLOAT,
    clay_uncertainty FLOAT,
    grass_rating FLOAT,
    grass_uncertainty FLOAT,
    hard_rating FLOAT,
    hard_uncertainty FLOAT,
    
    -- Supporting metrics
    form_index FLOAT,  -- Recent 20-match rolling performance
    big_match_rating FLOAT,  -- Performance against top 20 players
    tournament_success_score FLOAT,  -- Weighted tournament performance
    
    -- ELO ratings (base for TSR)
    elo_rating FLOAT,
    elo_clay FLOAT,
    elo_grass FLOAT,
    elo_hard FLOAT,
    
    -- Metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(20),  -- Track model iterations
    
    -- Unique constraint
    UNIQUE (player_id, match_id)
);

-- Create indexes for player_ratings table
CREATE INDEX idx_ratings_player_date ON player_ratings(player_id, date);
CREATE INDEX idx_ratings_player_match_num ON player_ratings(player_id, career_match_number);
CREATE INDEX idx_ratings_date ON player_ratings(date);

-- Player career summary table (for quick lookups)
CREATE TABLE player_career_stats (
    player_id INT PRIMARY KEY REFERENCES players(player_id),
    
    -- Career totals
    total_matches INT DEFAULT 0,
    total_wins INT DEFAULT 0,
    total_losses INT DEFAULT 0,
    win_percentage FLOAT,
    
    -- Surface breakdown
    clay_wins INT DEFAULT 0,
    clay_losses INT DEFAULT 0,
    grass_wins INT DEFAULT 0,
    grass_losses INT DEFAULT 0,
    hard_wins INT DEFAULT 0,
    hard_losses INT DEFAULT 0,
    
    -- Career highlights
    grand_slam_titles INT DEFAULT 0,
    masters_titles INT DEFAULT 0,
    atp_500_titles INT DEFAULT 0,
    atp_250_titles INT DEFAULT 0,
    
    -- Peak performance
    peak_tsr_rating FLOAT,
    peak_tsr_date DATE,
    peak_ranking INT,
    peak_ranking_date DATE,
    
    -- Career span
    first_match_date DATE,
    last_match_date DATE,
    career_duration_days INT,
    
    -- Top opponent wins
    top_10_wins INT DEFAULT 0,
    top_10_losses INT DEFAULT 0,
    
    -- Updated timestamp
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on player career stats
CREATE INDEX idx_career_peak_rating ON player_career_stats(peak_tsr_rating DESC);
CREATE INDEX idx_career_win_pct ON player_career_stats(win_percentage DESC);
CREATE INDEX idx_career_slam_titles ON player_career_stats(grand_slam_titles DESC);

-- Create a view for easy player lookup with stats
CREATE VIEW player_overview AS
SELECT 
    p.player_id,
    p.name,
    p.date_of_birth,
    p.country,
    p.hand,
    p.height_cm,
    p.turned_pro,
    cs.total_matches,
    cs.total_wins,
    cs.total_losses,
    cs.win_percentage,
    cs.grand_slam_titles,
    cs.masters_titles,
    cs.peak_tsr_rating,
    cs.peak_tsr_date,
    cs.peak_ranking,
    cs.peak_ranking_date,
    cs.first_match_date,
    cs.last_match_date
FROM players p
LEFT JOIN player_career_stats cs ON p.player_id = cs.player_id;

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_career_stats_updated_at BEFORE UPDATE ON player_career_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE players IS 'Master player information table';
COMMENT ON TABLE matches IS 'All match results with scores and context';
COMMENT ON TABLE player_ratings IS 'Calculated performance ratings over time (output of Bayesian model)';
COMMENT ON TABLE player_career_stats IS 'Aggregated career statistics for quick lookups';
COMMENT ON COLUMN player_ratings.tsr_rating IS 'Tennis Skill Rating - primary composite metric';
COMMENT ON COLUMN player_ratings.tsr_smoothed IS 'Gaussian Process smoothed TSR for career trajectory visualization';

