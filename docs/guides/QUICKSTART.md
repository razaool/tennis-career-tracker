# Quick Start Guide ⚡

Get your Tennis Career Tracker running in 5 minutes

## Prerequisites Check

```bash
# Check Python (need 3.9+)
python --version

# Check PostgreSQL (need 14+)
psql --version

# Check PostgreSQL is running
pg_isready
```

## 5-Minute Setup

### 1. Install Dependencies (1 min)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Database (30 sec)

```bash
# Copy environment template
cp env.example .env

# Edit with your PostgreSQL password
# (or use default postgres/postgres)
nano .env
```

### 3. Run Setup (3 min)

```bash
# One command to do everything:
# - Create database & schema
# - Download Tennis Abstract data
# - Load matches into database
python scripts/setup_all.py
```

**This will:**
- ✅ Create `tennis_tracker` database
- ✅ Download ATP match data (2000-2024)
- ✅ Load ~40,000 matches
- ✅ Load ~3,000 players

### 4. Verify Setup (30 sec)

```bash
python scripts/test_setup.py
```

**Expected output:**
```
✅ PASS - Database Connection
✅ PASS - Tables Exist
✅ PASS - Data Loaded
✅ PASS - Sample Queries

🎉 All tests passed Your setup is complete.
```

## What You Have Now

### Database Tables

```sql
-- Players table: 3,000+ tennis players
SELECT * FROM players LIMIT 5;

-- Matches table: 40,000+ matches (2000-2024)
SELECT * FROM matches WHERE date > '2024-01-01' LIMIT 10;

-- Player career stats (ready for Phase 2)
SELECT * FROM player_career_stats;
```

### Sample Queries

**Top players by match count:**
```sql
SELECT p.name, COUNT(m.match_id) as matches
FROM players p
LEFT JOIN matches m ON (p.player_id = m.player1_id OR p.player_id = m.player2_id)
GROUP BY p.player_id, p.name
ORDER BY matches DESC
LIMIT 10;
```

**Matches by surface:**
```sql
SELECT surface, COUNT(*) as count
FROM matches
GROUP BY surface
ORDER BY count DESC;
```

**Recent Grand Slam finals:**
```sql
SELECT date, tournament_name, 
       p1.name as player1, p2.name as player2, 
       pw.name as winner, score
FROM matches m
JOIN players p1 ON m.player1_id = p1.player_id
JOIN players p2 ON m.player2_id = p2.player_id
JOIN players pw ON m.winner_id = pw.player_id
WHERE tournament_tier = 'Grand Slam' AND round = 'F'
ORDER BY date DESC
LIMIT 10;
```

## Optional: Load More Data

**Load all historical data (1968-present, ~2.5M matches):**
```bash
python scripts/setup_all.py --all-years
# Takes ~30 minutes
```

**Load specific year range:**
```bash
python scripts/setup_all.py --start-year 2010 --end-year 2024
```

## What's Next?

### Phase 2: Calculate Ratings
```bash
# Coming soon - implement Bayesian ELO
python scripts/calculate_ratings.py
```

### Phase 3: Start API
```bash
# Coming soon - FastAPI backend
uvicorn api.main:app --reload
```

### Phase 4: Launch Frontend
```bash
# Coming soon - Next.js visualization
cd frontend && npm run dev
```

## Troubleshooting

**PostgreSQL not running?**
```bash
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql
```

**Wrong password?**
```bash
# Connect to postgres and reset
psql postgres
ALTER USER postgres PASSWORD 'your_password';
```

**Want to reset everything?**
```bash
# ⚠️ Deletes all data
python -c "from database.db_manager import DatabaseManager; DatabaseManager().reset_database()"
python scripts/setup_all.py
```

## Project Structure

```
tennis-career-tracker/
├── config.py                 # Configuration
├── .env                      # Your settings
│
├── database/
│   ├── schema.sql           # Database structure
│   └── db_manager.py        # DB utilities
│
├── scripts/
│   ├── setup_all.py         # 🚀 Main setup script
│   ├── test_setup.py        # ✅ Verification
│   ├── download_tennis_data.py
│   └── parse_and_load_data.py
│
└── data/
    └── raw/
        └── tennis_atp/      # Downloaded data
```

## Need Help?

1. **Setup issues?** → See `SETUP_GUIDE.md`
2. **Project overview?** → See `README.md`
3. **Current status?** → See `PROJECT_STATUS.md`

---

**You're ready to build 🎾**

Next: Implement the Bayesian rating calculations to bring the visualizations to life.

