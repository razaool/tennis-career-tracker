# Separating Active vs Inactive Players

## Quick Answer

Use **time-based filtering** with a **6-12 month cutoff**:
- **6 months**: Currently active players
- **12 months**: Include players returning from injury
- **24 months**: All recently active (excludes clearly retired players)

---

## Current Status in Your Database

```
Last 6 months:    397 active players  ✅ RECOMMENDED
Last 12 months:  1,964 active players
Last 18 months:  3,315 active players
Last 24 months:  3,683 active players
```

---

## Four Approaches to Separate Active/Inactive

### 1. **Time-Based Filtering** (RECOMMENDED) ⭐

Filter by last match date:

```python
from datetime import datetime, timedelta

cutoff_date = (datetime.now() - timedelta(days=6 * 30)).strftime('%Y-%m-%d')

query = """
    WITH latest_ratings AS (
        SELECT DISTINCT ON (player_id)
            player_id,
            elo_rating,
            date as last_match
        FROM player_ratings
        WHERE date >= %s  -- Only players who played recently
        ORDER BY player_id, date DESC
    )
    SELECT 
        pl.name,
        lr.elo_rating,
        lr.last_match
    FROM latest_ratings lr
    JOIN players pl ON lr.player_id = pl.player_id
    ORDER BY lr.elo_rating DESC
"""
```

**Pros:**
- ✅ Simple and objective
- ✅ Automatically updates daily
- ✅ No manual maintenance

**Cons:**
- ❌ Might include one-off comeback matches
- ❌ Misses players on temporary break

---

### 2. **Status-Based Classification**

Categorize players into tiers:

```python
def classify_player_status(last_match_date):
    months_since = (datetime.now() - last_match_date).days / 30
    
    if months_since <= 6:
        return 'ACTIVE'       # 🟢 Currently playing
    elif months_since <= 12:
        return 'SEMI-ACTIVE'  # 🟡 Might return (injury)
    elif months_since <= 24:
        return 'INACTIVE'     # 🟠 Long absence
    else:
        return 'RETIRED'      # 🔴 Likely retired
```

**SQL Implementation:**

```sql
SELECT 
    pl.name,
    lr.elo_rating,
    lr.last_match,
    CASE 
        WHEN lr.last_match >= CURRENT_DATE - INTERVAL '6 months' THEN 'ACTIVE'
        WHEN lr.last_match >= CURRENT_DATE - INTERVAL '12 months' THEN 'SEMI-ACTIVE'
        WHEN lr.last_match >= CURRENT_DATE - INTERVAL '24 months' THEN 'INACTIVE'
        ELSE 'RETIRED'
    END as status
FROM latest_ratings lr
JOIN players pl ON lr.player_id = pl.player_id
```

**Pros:**
- ✅ More nuanced than binary active/inactive
- ✅ Can show different lists for each category

**Cons:**
- ❌ More complex to implement
- ❌ Threshold choices are subjective

---

### 3. **Minimum Match Count Filter**

Require players to have played multiple matches recently:

```sql
WITH recent_matches AS (
    SELECT 
        player_id,
        COUNT(*) as recent_match_count,
        MAX(date) as last_match
    FROM player_ratings
    WHERE date >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY player_id
    HAVING COUNT(*) >= 5  -- Minimum 5 matches
)
SELECT 
    pl.name,
    lr.elo_rating,
    rm.recent_match_count
FROM recent_matches rm
JOIN latest_ratings lr ON rm.player_id = lr.player_id
JOIN players pl ON rm.player_id = pl.player_id
ORDER BY lr.elo_rating DESC
```

**Pros:**
- ✅ Filters out one-off comeback matches
- ✅ Ensures consistent activity

**Cons:**
- ❌ Might exclude players who just started season
- ❌ Can miss legitimate returnees

---

### 4. **Separate Rankings Lists**

Maintain multiple ranking lists:

```python
rankings = {
    'current': get_active_players(months=6),      # Active rankings
    'all_time': get_all_players(),                # Includes retired players
    'returning': get_semi_active_players()        # Comeback candidates
}
```

**Pros:**
- ✅ Most comprehensive view
- ✅ Can show historical context
- ✅ Useful for different use cases

**Cons:**
- ❌ More complex to maintain
- ❌ Multiple sources of truth

---

## Where It's Already Implemented

Your codebase already uses time-based filtering in several places:

### 1. `scripts/generate_comprehensive_rankings.py`

```python
def generate_combined_rankings(db, year=2024, active_months=6, window_size=50, top_n=20):
    cutoff_date = (datetime.now() - timedelta(days=active_months * 30)).strftime('%Y-%m-%d')
    
    current_rankings = get_current_elo_rankings(db, min_date=cutoff_date, limit=top_n)
    rolling_rankings = get_rolling_average_rankings(db, min_date=cutoff_date, limit=top_n)
```

Currently set to **6 months** (`active_months=6`)

### 2. `scripts/calculate_rolling_elo.py`

```python
def get_rolling_avg_rankings(db, window_size=50, active_within_months=6):
    cutoff_date = datetime.now() - timedelta(days=active_within_months * 30)
```

Also uses **6 months**

---

## Recommended Thresholds

### **For Current Rankings: 6 months** ✅

```python
ACTIVE_THRESHOLD = 6  # months
```

**Why:**
- Includes all players in current season
- Excludes clearly retired players (Federer, Sampras)
- Captures "right now" competition

**Result:** ~400 active players

### **For "All-Time" Rankings: No filter**

```python
# Include everyone for historical context
```

**Why:**
- Allows comparison across eras
- Shows peak performance of legends
- Useful for "GOAT debate"

### **For "Returning Player Watch": 12 months**

```python
SEMI_ACTIVE_THRESHOLD = 12  # months
```

**Why:**
- Catches injured players
- Identifies potential comebacks
- More forgiving for career breaks

---

## Practical Examples

### Example 1: Current Top 10

```python
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta

db = DatabaseManager()
cutoff = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

with db.get_cursor() as cursor:
    cursor.execute("""
        WITH latest_ratings AS (
            SELECT DISTINCT ON (player_id)
                player_id, elo_rating, date
            FROM player_ratings
            WHERE date >= %s
            ORDER BY player_id, date DESC
        )
        SELECT pl.name, lr.elo_rating
        FROM latest_ratings lr
        JOIN players pl ON lr.player_id = pl.player_id
        ORDER BY lr.elo_rating DESC
        LIMIT 10
    """, (cutoff,))
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{i}. {row['name']}: {row['elo_rating']:.1f}")
```

**Output:**
```
1. Jannik Sinner: 3179.6
2. Carlos Alcaraz: 3061.5
3. Novak Djokovic: 2959.2
4. Taylor Fritz: 2915.1
...
```

### Example 2: Split Active/Retired

```python
def get_split_rankings():
    db = DatabaseManager()
    cutoff = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    with db.get_cursor() as cursor:
        # Active players
        cursor.execute("""
            WITH latest_ratings AS (
                SELECT DISTINCT ON (player_id)
                    player_id, elo_rating, date
                FROM player_ratings
                WHERE date >= %s
                ORDER BY player_id, date DESC
            )
            SELECT pl.name, lr.elo_rating, 'ACTIVE' as status
            FROM latest_ratings lr
            JOIN players pl ON lr.player_id = pl.player_id
            ORDER BY lr.elo_rating DESC
        """, (cutoff,))
        
        active = cursor.fetchall()
        
        # Retired players (last played >2 years ago)
        retired_cutoff = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        cursor.execute("""
            WITH latest_ratings AS (
                SELECT DISTINCT ON (player_id)
                    player_id, elo_rating, date
                FROM player_ratings
                WHERE date < %s
                ORDER BY player_id, date DESC
            )
            SELECT pl.name, lr.elo_rating, 'RETIRED' as status
            FROM latest_ratings lr
            JOIN players pl ON lr.player_id = pl.player_id
            WHERE lr.elo_rating >= 2500  -- Only high-level retired players
            ORDER BY lr.elo_rating DESC
        """, (retired_cutoff,))
        
        retired = cursor.fetchall()
    
    return {'active': active, 'retired': retired}
```

---

## For Your API (Phase 3)

When building your API endpoints, provide separate rankings:

```python
# FastAPI endpoints
@app.get("/rankings/current")
def get_current_rankings(min_matches: int = 5):
    """Active players only (6 months)"""
    return get_active_players(months=6, min_matches=min_matches)

@app.get("/rankings/all-time")
def get_all_time_rankings():
    """Include retired legends"""
    return get_all_players()

@app.get("/rankings/returning")
def get_returning_players():
    """Players who might come back (6-12 months)"""
    return get_semi_active_players()
```

---

## Quick Reference

| Use Case | Threshold | SQL Filter |
|----------|-----------|------------|
| **Current Rankings** | 6 months | `WHERE date >= CURRENT_DATE - INTERVAL '6 months'` |
| **Injury/Return Watch** | 12 months | `WHERE date >= CURRENT_DATE - INTERVAL '12 months'` |
| **All-Time Rankings** | None | No filter (include everyone) |
| **Definitely Retired** | >24 months | `WHERE date < CURRENT_DATE - INTERVAL '24 months'` |

---

## Status Emoji Guide

Use these in your UI/reports:

- 🟢 **ACTIVE** - Played in last 6 months
- 🟡 **SEMI-ACTIVE** - Played in last 6-12 months (injury/break)
- 🟠 **INACTIVE** - Played in last 12-24 months (likely done)
- 🔴 **RETIRED** - Last played >24 months ago

---

## Summary

**RECOMMENDED APPROACH:**

1. **Use 6-month cutoff for "Current Rankings"**
2. **Use 12-month cutoff for "Active Rankings" (includes injured)**
3. **No filter for "All-Time Rankings"**
4. **Add minimum match count (5+) to filter one-off comebacks**

This gives you:
- Clean separation of active vs retired
- Objective, automated criteria
- Flexibility for different views
- Already implemented in your scripts!

---

**Already set up in your code!** Just use `active_months=6` parameter in your ranking functions. ✅

