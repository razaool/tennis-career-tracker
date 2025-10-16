# Tennis Ranking Systems - Three Complementary Metrics

## 🎯 Overview

This project uses **three different ELO-based metrics** to capture different aspects of player performance. Each metric serves a distinct purpose and tells a different story about player ability.

---

## 📊 The Three Metrics

### 1. **Current ELO** - Form & Momentum
**What it shows:** Player's immediate form based on their last match  
**Use cases:**
- Match predictions and betting odds
- Identifying hot/cold streaks
- Real-time form assessment

**Characteristics:**
- ✅ Reflects latest performance
- ✅ Useful for near-term predictions
- ❌ Highly volatile
- ❌ Can be misleading (one bad loss tanks rating)

**Example:**
```
Carlos Alcaraz after losing to Ruud: 2520.8
(Down from 2878.6 peak - doesn't reflect his Grand Slam wins)
```

---

### 2. **Rolling Average ELO (50 matches)** - Consistency
**What it shows:** Player's sustained performance over last 50 matches  
**Use cases:**
- "Who's better?" questions
- Overall skill assessment
- Filtering out volatility

**Characteristics:**
- ✅ Smooths out bad/good days
- ✅ Rewards consistency
- ✅ More stable than current ELO
- ❌ Slower to react to form changes
- ❌ Requires sufficient match history

**Example:**
```
Carlos Alcaraz:
- Current ELO: 2520.8 (after losses)
- 50-match avg: 2696.1 (includes Wimbledon + French Open wins)
The average is a better representation of his true skill
```

---

### 3. **Peak ELO (Time Period)** - Achievement
**What it shows:** Highest rating achieved in a time period (e.g., 2024)  
**Use cases:**
- Year-end awards and rankings
- Career milestones
- Capturing Grand Slam performances

**Characteristics:**
- ✅ Captures best moments
- ✅ Rewards tournament success
- ✅ Fair for year-end comparisons
- ❌ May not reflect current ability
- ❌ Can be achieved with one great run

**Example:**
```
Carlos Alcaraz Peak 2024: 2878.6
(Achieved after winning Wimbledon - his best moment of the year)
```

---

## 🔥 Key Insights from 2024 Rankings

### Top 5 by Each Metric:

| Rank | Current ELO | Rolling Avg-50 | Peak 2024 |
|------|-------------|----------------|-----------|
| 1 | Sinner 2940.6 | Sinner 2847.5 | Sinner 2940.6 |
| 2 | Djokovic 2751.8 | Alcaraz 2696.1 ⭐ | **Alcaraz 2878.6** ⭐ |
| 3 | Fritz 2683.3 | Djokovic 2689.3 | Djokovic 2822.2 |
| 4 | Zverev 2650.9 | Fritz 2592.8 | Zverev 2701.8 |
| 5 | Draper 2577.9 | Zverev 2580.5 | Medvedev 2701.6 |

**⭐ Key Finding:** Alcaraz ranks **#8** by current ELO but **#2** by rolling average and peak The current ELO is misleading due to end-of-season losses.

---

## 🧊 Hot & Cold Streaks

### 🔥 Hot Streaks (Current > Avg by 50+)
Players performing above their average:
- **Sinner**: +93 points (on fire)
- **Draper**: +118 points (career-best form)
- **Fritz**: +91 points (late-season surge)
- **Zverev**: +70 points (upward trajectory)
- **Djokovic**: +62 points (late resurgence)

### ❄️ Cold Streaks (Current < Avg by 50+)
Players struggling below their average:
- **Alcaraz**: -175 points (post-Slam slump)
- **Musetti**: -164 points (rough patch)
- **Nakashima**: -125 points (declining form)
- **Tommy Paul**: -121 points (end-season dip)
- **Hurkacz**: -121 points (injury/form issues)

---

## 📈 When to Use Each Metric

### Use **Current ELO** when:
- Predicting upcoming matches
- Setting betting odds
- Assessing immediate form
- Tracking momentum

### Use **Rolling Average** when:
- Comparing player skill levels
- Answering "who's better?" questions
- Making roster/seeding decisions
- Filtering out noise/volatility

### Use **Peak ELO** when:
- Year-end rankings and awards
- Comparing achievements
- Historical analysis
- Celebrating milestones

---

## 🚨 The Nick Kyrgios Problem

**Issue:** Inactive players maintain their last rating  
**Example:**
- Nick Kyrgios: Current ELO = 2531.5
- Last match: October 2022 (2+ years ago)
- He ranks #7 but hasn't played in 2024

**Solution:** Always filter by activity date
```sql
WHERE last_match_date >= '2024-06-01'  -- Active in last 6 months
```

---

## 🔬 Cross-Era Comparison Issues

### The Problem:
ELO ratings are relative to the opponent pool. Comparing across eras is problematic:

```
Djokovic 2016: 2930.6 (faced Federer, Nadal, Murray)
vs
Sinner 2024:   2940.6 (faces Alcaraz, Zverev, but no Big 3)
```

**Is Sinner > Djokovic?** Not necessarily The 2024 field may be weaker.

### The Solution:
1. **Use Peak ELO only within same era** (compare 2024 players to each other)
2. **Use Rolling Average for current rankings** (smooths volatility)
3. **Build Bayesian model with era adjustment** (Phase 2, Script 2) 🔜
4. **Compare percentile rankings**, not absolute ELO

---

## 📁 Exported Data Files

All rankings are exported to `data/processed/`:

| File | Contents |
|------|----------|
| `rankings_all_three_metrics.csv` | All 3 metrics side-by-side |
| `big3_comparison.csv` | Djokovic, Nadal, Federer careers |
| `nextgen_comparison.csv` | Alcaraz, Sinner, Rune careers |
| `top10_current.csv` | Top 10 by current ELO |
| Individual player files | Full career trajectories |

---

## 🎯 Recommendations

### For Your DARKO-Style Visualization:

**Best Approach:** Use **Rolling Average (50 matches)** as the main line

**Why?**
- ✅ Smooth enough for clean visualization
- ✅ Captures sustained performance
- ✅ Filters out single-match volatility
- ✅ Still responsive to form changes

**Additional Layers:**
- Show **Peak ELO** as dots/markers (milestones)
- Show **Current ELO** as latest point (with indicator if hot/cold)
- Add shaded region for ±1 std dev (uncertainty band)

**Example Chart:**
```
ELO Rating
   3000 |                    
        |              ⭐ Peak (Wimbledon)
   2800 |            /  \
        |           /    \_____ Rolling Avg-50
   2600 |          /              \
        |         /                 \
   2400 |________/                   \● Current (cold streak)
        |
        +------------------------------------ Career Match #
          0    100   200   300   400   500
```

---

## 🔜 Next Steps (Phase 2)

1. **Bayesian TSR Model** - Add uncertainty estimates
2. **Era Adjustment** - Normalize ratings across time periods
3. **Strength of Schedule** - Weight opponent quality
4. **Surface Smoothing** - Gaussian process for trajectories
5. **Supporting Metrics** - Big match performance, momentum index

---

## 💡 Key Takeaways

1. **No single metric tells the full story** - use all three
2. **Current ELO is volatile** - use for predictions, not overall assessment
3. **Rolling Average is most reliable** - use for "who's better" questions
4. **Peak ELO captures greatness** - use for achievements and awards
5. **Always filter inactive players** - avoid the Kyrgios problem
6. **Cross-era comparisons are tricky** - need Bayesian adjustment (Phase 2)

---

## 📊 Quick Reference

| Question | Best Metric |
|----------|-------------|
| "Who will win the next match?" | Current ELO |
| "Who's the better player?" | Rolling Avg-50 |
| "Who had the best year?" | Peak ELO (year) |
| "Who's the GOAT?" | Bayesian TSR (Phase 2) |
| "Who's in form right now?" | Current vs Rolling Avg |
| "Who's most consistent?" | Rolling Avg variance |

---

**Generated:** 2024-10-14  
**Data Coverage:** 1978-2024 (828K matches, 25K players)  
**Last Update:** December 18, 2024

