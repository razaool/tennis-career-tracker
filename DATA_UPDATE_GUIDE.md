# Data Update Guide - Getting Latest Match Data

## 🎯 Goal
Update your database with matches from **December 18, 2024** to **October 14, 2025** (present).

---

## 🚀 Quick Update (Automated)

### **Step 1: Run the Update Script**

```bash
cd /Users/razaool/tennis-career-tracker
source venv/bin/activate
python3 scripts/update_data.py
```

This script will:
1. ✅ Download latest 2025 data from Tennis Abstract
2. ✅ Parse and load new matches into database
3. ✅ Recalculate ELO ratings for all players
4. ✅ Regenerate all export CSV files

**Expected output:**
```
📅 Current database last match: 2024-12-18
✅ Downloaded 2025 data: 850 matches
📈 Added 850 new matches since 2024-12-18
🔄 Recalculating ELO ratings...
✅ ELO ratings recalculated successfully
📤 Regenerating export files...
✅ UPDATE COMPLETE!
```

---

## 📊 Data Sources (In Order of Preference)

### **1. Tennis Abstract (Automated) ⭐ RECOMMENDED**

**Pros:**
- ✅ Free and open source
- ✅ Automated download via script
- ✅ Consistent format (works with existing parser)
- ✅ Historical data back to 1968

**Cons:**
- ❌ Updated every 1-2 weeks (slight delay)
- ❌ May not have last few days of matches

**How to use:**
```bash
python3 scripts/update_data.py
```

**Manual check:**
- URL: https://github.com/JeffSackmann/tennis_atp
- Look for: `atp_matches_2025.csv`
- Last updated: Check commit history

---

### **2. Ultimate Tennis Statistics (Manual)**

**Pros:**
- ✅ More up-to-date than Tennis Abstract
- ✅ Comprehensive statistics
- ✅ Good data quality

**Cons:**
- ❌ Requires manual download
- ❌ May need format conversion

**How to use:**
1. Visit: https://www.ultimatetennisstatistics.com/
2. Go to "Matches" → "Results Archive"
3. Filter: Date range (Dec 18, 2024 - Oct 14, 2025)
4. Export as CSV
5. Save to: `data/raw/uts_matches_2025.csv`
6. Run: `python3 scripts/parse_and_load_data.py data/raw/uts_matches_2025.csv`

---

### **3. ATP Official Website (Web Scraping)**

**Pros:**
- ✅ Most current data (real-time)
- ✅ Official source

**Cons:**
- ❌ Requires web scraping (complex)
- ❌ No bulk download option
- ❌ Rate limiting

**How to use:**
1. Visit: https://www.atptour.com/en/scores/results-archive
2. Scrape match results (requires custom script)
3. Convert to CSV format
4. Load into database

**Note:** This requires building a custom scraper. Not recommended unless you need real-time data.

---

### **4. Manual Entry (Last Resort)**

For missing matches or corrections:

```sql
-- Connect to database
psql -U postgres -d tennis_tracker

-- Insert a match manually
INSERT INTO matches (
    tournament_name, surface, date, 
    player1_id, player2_id, winner_id,
    score, round, best_of
) VALUES (
    'Australian Open', 'hard', '2025-01-20',
    (SELECT player_id FROM players WHERE name = 'Jannik Sinner'),
    (SELECT player_id FROM players WHERE name = 'Carlos Alcaraz'),
    (SELECT player_id FROM players WHERE name = 'Jannik Sinner'),
    '6-4 7-6(3) 6-3', 'F', 5
);
```

---

## 🔍 Checking Data Status

### **What's currently in the database?**

```bash
psql -U postgres -d tennis_tracker -c "
  SELECT 
    MIN(date) as first_match,
    MAX(date) as last_match,
    COUNT(*) as total_matches
  FROM matches;
"
```

**Expected output:**
```
 first_match | last_match | total_matches 
-------------+------------+---------------
 1978-01-08  | 2024-12-18 |        828202
```

### **How many matches per year?**

```bash
psql -U postgres -d tennis_tracker -c "
  SELECT 
    EXTRACT(YEAR FROM date) as year,
    COUNT(*) as matches
  FROM matches
  GROUP BY year
  ORDER BY year DESC
  LIMIT 5;
"
```

### **Who played most recently?**

```bash
psql -U postgres -d tennis_tracker -c "
  SELECT 
    m.date,
    p1.name as player1,
    p2.name as player2,
    pw.name as winner,
    m.tournament_name
  FROM matches m
  JOIN players p1 ON m.player1_id = p1.player_id
  JOIN players p2 ON m.player2_id = p2.player_id
  JOIN players pw ON m.winner_id = pw.player_id
  ORDER BY m.date DESC
  LIMIT 10;
"
```

---

## 🔄 Update Workflow

### **Full Update Process:**

```bash
# 1. Activate environment
cd /Users/razaool/tennis-career-tracker
source venv/bin/activate

# 2. Download new data (automated)
python3 scripts/update_data.py

# OR manually download and specify file:
python3 scripts/parse_and_load_data.py data/raw/atp_matches_2025.csv

# 3. Recalculate ELO ratings
python3 scripts/calculate_elo.py

# 4. Regenerate exports
python3 scripts/export_visualization_data.py

# 5. Generate updated rankings
python3 scripts/generate_comprehensive_rankings.py
```

---

## ⏰ Update Frequency Recommendations

### **For Production App:**

**Option A: Weekly Updates (Recommended)**
```bash
# Run every Monday morning
0 9 * * 1 cd /path/to/tennis-career-tracker && source venv/bin/activate && python3 scripts/update_data.py
```

**Option B: Daily Updates (If using real-time source)**
```bash
# Run every day at 6 AM
0 6 * * * cd /path/to/tennis-career-tracker && source venv/bin/activate && python3 scripts/update_data.py
```

**Option C: Manual Updates (Development)**
- Update when you need fresh data
- Run `python3 scripts/update_data.py`

---

## 🐛 Troubleshooting

### **Problem: "2025 data not yet available"**

**Cause:** Tennis Abstract hasn't updated their GitHub yet

**Solutions:**
1. **Wait:** Check back in a few days
2. **Check manually:** Visit https://github.com/JeffSackmann/tennis_atp
3. **Use alternative source:** Try Ultimate Tennis Statistics
4. **Check last update:**
   ```bash
   curl -s https://api.github.com/repos/JeffSackmann/tennis_atp/commits?path=atp_matches_2025.csv | grep -m 1 '"date"'
   ```

---

### **Problem: "Duplicate key error" when loading data**

**Cause:** Match already exists in database

**Solution:**
```sql
-- Check for duplicates
SELECT tournament_name, date, COUNT(*) 
FROM matches 
GROUP BY tournament_name, date 
HAVING COUNT(*) > 1;

-- Delete duplicates (keep earliest entry)
DELETE FROM matches 
WHERE match_id NOT IN (
  SELECT MIN(match_id) 
  FROM matches 
  GROUP BY tournament_name, date, player1_id, player2_id
);
```

---

### **Problem: "Player not found" error**

**Cause:** New player not in database

**Solution:** Parser should auto-create players, but if not:
```sql
-- Add missing player
INSERT INTO players (player_id, name, hand, birth_date, country_code)
VALUES (999999, 'New Player Name', 'R', '2000-01-01', 'USA');
```

---

### **Problem: ELO ratings not updating**

**Cause:** Need to recalculate after adding matches

**Solution:**
```bash
# Recalculate all ELO ratings from scratch
python3 scripts/calculate_elo.py

# Check if it worked
psql -U postgres -d tennis_tracker -c "
  SELECT name, elo_rating, date 
  FROM player_ratings pr
  JOIN players p ON pr.player_id = p.player_id
  ORDER BY date DESC 
  LIMIT 10;
"
```

---

## 📅 Expected Data Availability

### **Tennis Abstract Update Schedule:**

| Month | Typical Update Date | Matches Covered |
|-------|---------------------|-----------------|
| January | Feb 1-7 | Australian Open |
| February | Mar 1-7 | Early hard court season |
| March | Apr 1-7 | Indian Wells, Miami |
| April | May 1-7 | Clay court season starts |
| May | Jun 1-7 | French Open |
| June | Jul 1-7 | Grass season |
| July | Aug 1-7 | Wimbledon |
| August | Sep 1-7 | US Open Series |
| September | Oct 1-7 | US Open |
| October | Nov 1-7 | Asian swing |
| November | Dec 1-7 | ATP Finals |
| December | Jan 1-7 | Off-season |

**Note:** These are estimates. Check the GitHub repo for actual updates.

---

## 🎯 What You Need Right Now

**Current situation:**
- Database has matches through: **December 18, 2024**
- Today's date: **October 14, 2025**
- Missing: **~10 months of data**

**Expected missing tournaments:**
- 2025 Australian Open (January)
- Indian Wells & Miami (March)
- Clay court season (April-May)
- French Open (May-June)
- Grass season (June)
- Wimbledon (July)
- US Open Series (August)
- US Open (September)
- Asian swing (September-October)

**Estimated missing matches:** ~8,000-10,000 matches

---

## ✅ Next Steps

1. **Run the update script:**
   ```bash
   python3 scripts/update_data.py
   ```

2. **If 2025 data not available:**
   - Check Tennis Abstract GitHub manually
   - Try Ultimate Tennis Statistics
   - Wait a few days and retry

3. **Once data is loaded:**
   - Verify with `psql` queries
   - Check updated rankings
   - Regenerate visualizations

4. **Set up automated updates:**
   - Add cron job for weekly updates
   - Monitor for data freshness

---

**Need help?** Check the Tennis Abstract GitHub issues or open an issue in your repo!

