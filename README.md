# Tennis Career Tracker

Interactive platform for visualizing tennis player career progressions using Bayesian hierarchical modeling and advanced analytics.

## 🎾 Overview

This project provides a comprehensive tool for analyzing and visualizing tennis player career trajectories, similar to DARKO DPM for basketball. It uses a sophisticated **Tennis Skill Rating (TSR)** metric based on Bayesian ELO ratings, tournament context, and match quality.

## 🏗️ Project Structure

```
tennis-career-tracker/
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
│
├── database/
│   ├── schema.sql              # PostgreSQL database schema
│   └── db_manager.py           # Database connection utilities
│
├── scripts/
│   ├── download_tennis_data.py # Download Tennis Abstract data
│   ├── parse_and_load_data.py  # Parse and load data to DB
│   └── setup_all.py            # Complete setup automation
│
├── data/
│   ├── raw/                    # Raw Tennis Abstract data
│   └── processed/              # Processed datasets
│
└── api/                        # FastAPI backend (coming soon)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Git

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd tennis-career-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env.example .env
# Edit .env with your database credentials
```

### 2. Database Setup

Make sure PostgreSQL is running, then:

```bash
# Create database and schema
python -m database.db_manager
```

This will:
- Create the `tennis_tracker` database
- Set up all tables and indexes
- Initialize tournament tiers

### 3. Download and Load Data

#### Option A: Automated Setup (Recommended)

```bash
# Run complete setup (downloads data + loads to DB)
python scripts/setup_all.py

# Load specific year range
python scripts/setup_all.py --start-year 2010 --end-year 2024

# Load all historical data (1968-present)
python scripts/setup_all.py --all-years
```

#### Option B: Manual Steps

```bash
# 1. Download Tennis Abstract data
python scripts/download_tennis_data.py

# 2. Parse and load into database
python scripts/parse_and_load_data.py
```

## 📊 Database Schema

### Core Tables

**`players`** - Player master data
- `player_id`, `name`, `date_of_birth`, `country`, `hand`, `height_cm`

**`matches`** - All match results with context
- Match details (date, score, surface, tournament)
- Player rankings at time of match
- Match statistics (aces, double faults, etc.)

**`player_ratings`** - Calculated performance metrics
- `tsr_rating` - Tennis Skill Rating (primary metric)
- `tsr_smoothed` - Gaussian Process smoothed for visualization
- Surface-specific ratings (clay, grass, hard)
- Supporting metrics (form index, big match rating)

**`player_career_stats`** - Aggregated career statistics
- Career totals, win percentages
- Grand Slam titles, peak rankings
- Surface breakdown

## 🎯 Performance Metrics

### Tennis Skill Rating (TSR)
Our primary metric combining:
- **Bayesian ELO** (40%) - Surface-adjusted, opponent-strength weighted
- **Recent Form** (30%) - Rolling 20-match performance
- **Quality Wins** (20%) - Performance against top players
- **Tournament Success** (10%) - Slam/Masters results

### Supporting Metrics
- **Form Index** - Recent match performance
- **Big Match Rating** - Top-10 opponent performance
- **Surface Ratings** - Clay, grass, hard court specific

## 📈 Data Sources

- **Tennis Abstract** (Jeff Sackmann): Historical ATP/WTA matches (1968-present)
- **ATP/WTA APIs**: Live rankings and current matches (coming soon)

## 🔮 Next Steps

### Phase 1: ✅ Data Foundation (Complete)
- [x] Database schema
- [x] Data ingestion pipeline
- [x] Tennis Abstract integration

### Phase 2: 🚧 Rating Calculations (In Progress)
- [ ] Basic ELO implementation
- [ ] Surface-adjusted ratings
- [ ] Bayesian hierarchical model
- [ ] Gaussian Process smoothing

### Phase 3: 📅 API Development (Planned)
- [ ] FastAPI endpoints
- [ ] Player career progressions
- [ ] Comparison endpoints
- [ ] Live rankings integration

### Phase 4: 📅 Visualization (Planned)
- [ ] Next.js frontend
- [ ] Interactive career progression charts
- [ ] Player overview pages
- [ ] Live rankings dashboard

## 🛠️ Development

### Running Tests
```bash
pytest
```

### Database Management
```bash
# Check database stats
python -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); print(db.get_database_stats())"

# Reset database (⚠️ deletes all data)
python -c "from database.db_manager import DatabaseManager; DatabaseManager().reset_database()"
```

## 📝 Configuration

Edit `.env` file:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tennis_tracker
DB_USER=postgres
DB_PASSWORD=your_password

# Data Processing
START_YEAR=2000
END_YEAR=2024
```

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Tennis Abstract (Jeff Sackmann) for comprehensive tennis data
- Inspired by DARKO DPM visualization for basketball

---

Built with ❤️ for tennis analytics
