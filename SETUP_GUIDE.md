# Setup Guide - Tennis Career Tracker

This guide walks you through setting up the Tennis Career Tracker from scratch.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Python 3.9 or higher** - Check with `python --version`
- [ ] **PostgreSQL 14 or higher** - Check with `psql --version`
- [ ] **Git** - Check with `git --version`
- [ ] **PostgreSQL running** - Check with `pg_isready` or try connecting with `psql`

## Step-by-Step Setup

### 1. Install PostgreSQL (if not installed)

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

### 2. Create Virtual Environment

```bash
# Navigate to project directory
cd tennis-career-tracker

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Database tools (psycopg2, SQLAlchemy)
- Data processing (pandas, numpy, scipy)
- Bayesian modeling (pymc, arviz)
- API framework (FastAPI, uvicorn)
- Visualization (plotly, matplotlib)

### 4. Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Example `.env` configuration:**
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tennis_tracker
DB_USER=postgres
DB_PASSWORD=your_postgres_password

START_YEAR=2000
END_YEAR=2024
```

### 5. Initialize Database

```bash
# This creates the database and schema
python -m database.db_manager
```

**What this does:**
- Creates `tennis_tracker` database
- Sets up tables: `players`, `matches`, `player_ratings`, `player_career_stats`
- Creates indexes for fast queries
- Initializes tournament tier lookup table

**Expected output:**
```
INFO - Created database: tennis_tracker
INFO - Database schema created successfully
✅ Database initialized successfully

Current database stats:
  players: 0 rows
  matches: 0 rows
  player_ratings: 0 rows
  player_career_stats: 0 rows
```

### 6. Download and Load Data

**Option A: Automated (Recommended)**

```bash
# Download data + load to database in one command
python scripts/setup_all.py

# For specific year range:
python scripts/setup_all.py --start-year 2010 --end-year 2024

# For ALL historical data (1968-present, ~2.5M matches):
python scripts/setup_all.py --all-years
```

**Option B: Manual Steps**

```bash
# Step 1: Download Tennis Abstract data
python scripts/download_tennis_data.py

# Step 2: Parse and load into database
python scripts/parse_and_load_data.py
```

**What gets downloaded:**
- ATP match data (CSV files by year)
- Player metadata (names, DOB, country, hand)
- Tournament information
- Match statistics

**Time estimates:**
- Download: ~1-2 minutes
- Loading 2000-2024: ~5-10 minutes
- Loading all historical (1968-present): ~20-30 minutes

### 7. Verify Setup

```bash
# Check database stats
python -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); print(db.get_database_stats())"
```

**Expected output (for 2000-2024):**
```
{'players': ~3000, 'matches': ~40000, 'player_ratings': 0, 'player_career_stats': 0}
```

## Troubleshooting

### PostgreSQL Connection Issues

**Error: `could not connect to server`**
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux
```

**Error: `password authentication failed`**
- Check your `.env` file has correct password
- Try connecting manually: `psql -U postgres -d tennis_tracker`
- Reset password if needed:
  ```bash
  psql postgres
  ALTER USER postgres PASSWORD 'new_password';
  ```

### Python Package Issues

**Error: `No module named 'psycopg2'`**
```bash
# Reinstall with binary version
pip install psycopg2-binary --force-reinstall
```

**Error: `pymc installation failed`**
```bash
# Install build dependencies first
pip install cython numpy scipy
pip install pymc
```

### Data Download Issues

**Error: `git clone failed`**
- Check internet connection
- Try manual download from: https://github.com/JeffSackmann/tennis_atp
- Extract to `data/raw/tennis_atp/`

**Error: `No ATP match files found`**
```bash
# Verify data directory structure
ls -la data/raw/tennis_atp/
# Should show: atp_matches_2024.csv, atp_matches_2023.csv, etc.
```

### Database Schema Issues

**Error: `relation "players" does not exist`**
```bash
# Re-run schema creation
python -m database.db_manager
```

**To completely reset database:**
```bash
# ⚠️ This deletes all data
python -c "from database.db_manager import DatabaseManager; DatabaseManager().reset_database()"
```

## Next Steps

Once setup is complete:

1. **Calculate Ratings** (Phase 2 - coming soon)
   ```bash
   python scripts/calculate_ratings.py
   ```

2. **Start API Server** (Phase 3 - coming soon)
   ```bash
   uvicorn api.main:app --reload
   ```

3. **Launch Frontend** (Phase 4 - coming soon)
   ```bash
   cd frontend
   npm run dev
   ```

## Project Structure Overview

```
tennis-career-tracker/
├── config.py              # Central configuration
├── .env                   # Your local settings (not committed)
├── requirements.txt       # Python dependencies
│
├── database/
│   ├── schema.sql         # Database schema definition
│   └── db_manager.py      # Connection & utilities
│
├── scripts/
│   ├── download_tennis_data.py    # Step 1: Download data
│   ├── parse_and_load_data.py     # Step 2: Load to DB
│   └── setup_all.py               # Automated setup
│
├── data/
│   ├── raw/                       # Downloaded Tennis Abstract data
│   └── processed/                 # Processed datasets (future)
│
└── api/                           # FastAPI backend (Phase 3)
```

## Database Schema Summary

**`players`** - Player information
- Basic: name, DOB, country, hand, height
- ~3,000 active/historical players

**`matches`** - All match results
- Match details: date, score, surface, tournament
- Player rankings at match time
- Match stats: aces, DFs, serve %
- ~40,000 matches (2000-2024) or ~2.5M (all-time)

**`player_ratings`** - Performance metrics (calculated in Phase 2)
- TSR (Tennis Skill Rating)
- Surface-specific ratings
- Form indices, big match ratings

**`player_career_stats`** - Aggregated stats
- Career totals, win %
- Titles, peak rankings
- Surface breakdowns

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify your environment matches prerequisites
3. Check logs in terminal output
4. Open an issue on GitHub with error details

---

**Ready to build the future of tennis analytics 🎾**

