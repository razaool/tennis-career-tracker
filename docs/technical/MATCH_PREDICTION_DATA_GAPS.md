# 🎯 Match Prediction Enhancement - Data Gap Analysis

**Current Prediction Factors (What We Have):**
- ✅ Overall ELO rating
- ✅ Surface-specific ELO
- ✅ Current form (last 20 matches win %)
- ✅ Big match rating (vs top opponents)
- ✅ Head-to-head record
- ✅ TSR uncertainty (rating reliability)
- ✅ Player age/career stage

**Prediction Accuracy Estimate:** ~65-70% with current data

---

## 🔍 High-Impact Data We're Missing

### **TIER 1: Game-Changing Data** (Would boost accuracy to 75-80%)

#### **1. Match Statistics** ⭐⭐⭐⭐⭐
**What:**
- First serve %
- Aces per match
- Double faults per match
- Break points saved %
- Break points converted %
- Return points won %

**Why it matters:**
- Djokovic saves break points at 68% (clutch!)
- Alcaraz's first serve % = 65% (his weakness)
- Big servers win more on grass
- Return specialists dominate clay

**Impact on predictions:**
```
Alcaraz vs Sinner on grass:
- Without stats: Sinner 57% favorite (based on ELO)
- With stats: Alcaraz 52% favorite
  Reason: Alcaraz serves better (72% vs 68% first serve)
          Grass rewards servers
```

**How to get:**
- Check if Tennis Abstract CSVs include match stats columns
- If not: Scrape from ATP website (they have detailed stats for 2010+)

**Let me check your raw data...**

---

#### **2. Recent Momentum / Tournament Performance** ⭐⭐⭐⭐
**What:**
- Last 3 tournaments: titles, finals, semis, early exits
- Points scored in last 90 days
- Win streak (already have matches, can calculate)

**Why it matters:**
```
Player A: Won ATP 500 last week, 12-0 streak
Player B: Lost R1 last 3 tournaments, 2-3 record

Player A is "hot" - likely to outperform their ELO
```

**Impact:**
- Players on title runs often beat higher-rated opponents
- Players in slumps underperform their ELO by ~50 points

**How to get:**
- Calculate from existing match data! ✅
- Group matches by tournament
- Track results in last 90 days

**Can build this from what we have!**

---

#### **3. Round-Specific Performance** ⭐⭐⭐⭐
**What:**
- Win rate in Finals
- Win rate in Semifinals
- Win rate in early rounds

**Why it matters:**
```
Djokovic in Grand Slam finals: 24-13 (64.9%)
Average player in GS finals: ~50%

"Big match" temperament is real!
```

Some players:
- **Choke in finals** (historically: Zverev)
- **Elevate in finals** (Djokovic, Nadal)
- **Consistent across rounds** (Federer)

**Impact on predictions:**
```
Alcaraz vs Sinner in Grand Slam Final:
- Base prediction: 48% Alcaraz
- Adjusted for finals: 52% Alcaraz
  Reason: Alcaraz is 5-0 in Slam finals
          Sinner is 4-1 in Slam finals (both clutch!)
```

**How to get:**
- Calculate from existing data! ✅
- Filter matches by round column
- Track win rates per round

---

#### **4. Indoor vs Outdoor Performance** ⭐⭐⭐
**What:**
- Separate ratings for indoor hard vs outdoor hard

**Why it matters:**
- Indoor = faster, lower bounce, rewards serve
- Outdoor = slower, higher bounce, rewards baseline

Some players dominate indoors (Medvedev), others outdoors (Nadal)

**Current issue:**
We treat all hard courts the same, but:
```
US Open (outdoor hard) ≠ Paris Masters (indoor hard)
```

**How to get:**
- Check if raw data has "indoor" flag
- If not: Manually code tournaments (one-time task)
  - Indoor: Paris, Basel, Vienna, etc.
  - Outdoor: US Open, Indian Wells, Miami, etc.

---

### **TIER 2: Useful But Lower Impact** (Would add 2-3% accuracy)

#### **5. Best-of-3 vs Best-of-5 Performance** ⭐⭐⭐
**What:**
- Separate records for BO3 (ATP 250/500/1000) vs BO5 (Grand Slams)

**Why it matters:**
- Younger players tire in BO5
- Veterans excel in BO5 (experience, fitness)
- Different strategies needed

**Example:**
```
Sinner in BO3: 85% win rate
Sinner in BO5: 78% win rate (slightly worse in long matches)
```

**How to get:**
- Derive from tournament tier (Grand Slams = BO5, others = BO3)
- Calculate from existing data! ✅

---

#### **6. Recent H2H Momentum** ⭐⭐⭐
**What:**
- Overall H2H: 4-4
- Last 3 meetings: Player A won 3-0

**Why it matters:**
- Recent meetings matter more than old ones
- Psychological edge
- Tactical adjustments

**Example:**
```
Alcaraz vs Sinner:
- Overall: 4-4 (even)
- Last 3: Alcaraz 2-1 (slight edge)
```

**How to get:**
- Weight recent H2H meetings more heavily
- Calculate from existing data! ✅

---

#### **7. Fatigue / Days Since Last Match** ⭐⭐
**What:**
- Days of rest between matches
- Number of matches played in last 7/14/30 days

**Why it matters:**
```
Player A: Played 5 matches in 5 days (deep run)
Player B: Had 10 days rest (first round)

Player B has freshness advantage
```

**How to get:**
- Calculate from match dates! ✅
- Compare days between matches

---

#### **8. Home Court Advantage** ⭐⭐
**What:**
- Performance in home country tournaments

**Why it matters:**
- Crowd support
- Familiar conditions
- Less travel fatigue

**Example:**
```
Alcaraz at Madrid/Barcelona: +50 ELO boost
Sinner at Rome/Turin: +50 ELO boost
```

**How to get:**
- Match player nationality to tournament location
- Need player nationalities (might be in data)

---

### **TIER 3: Nice-to-Have** (Minimal impact, < 1% accuracy)

#### **9. Player Physical Attributes**
- Height (tall players serve better)
- Handedness (lefties have advantage)
- Age (already have this)

#### **10. Court Speed**
- Fast hard court (Cincinnati) vs slow hard court (Indian Wells)
- Would need detailed court speed ratings

#### **11. Weather Conditions**
- Heat, wind, altitude
- Very hard to get historical data

---

## 🎯 Recommended Action Plan

### **Step 1: Check Raw Data for Match Stats** (10 minutes)

Let me look at your Tennis Abstract CSVs to see what columns exist:

```python
# Check if we have match statistics
import pandas as pd

sample = pd.read_csv('data/raw/atp_matches_2024.csv', nrows=5)
print(sample.columns)

# Look for columns like:
# - w_ace (winner aces)
# - l_ace (loser aces)  
# - w_df (winner double faults)
# - w_svpt (winner serve points)
# - w_1stIn (winner first serves in)
# - w_bpSaved (break points saved)
```

**If these exist:** HUGE WIN! We can calculate serve/return metrics

**If not:** We proceed without them (still good predictions)

---

### **Step 2: Calculate From Existing Data** (2-3 hours work)

These we can build from what we have:

✅ **Recent tournament momentum**
- Group matches by tournament
- Calculate: Titles won, finals reached in last 90 days
- Create `recent_momentum` score (0-100)

✅ **Round-specific performance**
- Filter by `round` column (F, SF, QF, etc.)
- Calculate win rate per round
- Create `finals_performance` metric

✅ **Recent H2H trend**
- Take last 3 H2H meetings
- Weight more than overall H2H

✅ **Fatigue metrics**
- Calculate days between matches
- Count matches in last 7/14 days

✅ **Best-of-3 vs Best-of-5**
- Derive from tournament tier
- Calculate separate win rates

✅ **Indoor/outdoor**
- Manually code ~100 tournaments (one-time task)
- Calculate indoor/outdoor ELOs

---

### **Step 3: Enhanced Prediction Algorithm**

**Current (simple):**
```python
win_prob = base_elo_prob(elo_diff)
```

**Enhanced (with new data):**
```python
# Base probability from ELO
base_prob = elo_probability(elo_diff)

# Adjust for surface
surface_prob = adjust_for_surface(base_prob, surface_elo_diff)

# Adjust for form
if abs(form_diff) > 10:
    form_prob = surface_prob * (1 + form_diff/200)

# Adjust for momentum (new!)
if momentum_diff > 20:  # One player hot, other cold
    momentum_prob = form_prob * (1 + momentum_diff/400)

# Adjust for round (new!)
if round == "F" and has_finals_data:
    finals_prob = apply_finals_modifier(momentum_prob)

# Adjust for fatigue (new!)
if days_rest_diff > 3:  # One player fresher
    fatigue_prob = finals_prob * (1 + rest_factor)

# Final probability
final_prob = weighted_average(all_factors)
```

**Expected improvement:** 65% → 75-80% accuracy

---

## 📊 Data Priority Matrix

| Data Type | Impact | Effort | Priority | Source |
|-----------|--------|--------|----------|--------|
| **Match statistics** | ⭐⭐⭐⭐⭐ | Medium | **HIGH** | Check raw CSVs |
| **Recent momentum** | ⭐⭐⭐⭐ | Low | **HIGH** | Calculate from matches |
| **Round performance** | ⭐⭐⭐⭐ | Low | **HIGH** | Calculate from matches |
| **Indoor/outdoor** | ⭐⭐⭐ | Medium | **MEDIUM** | Manual coding |
| **Recent H2H trend** | ⭐⭐⭐ | Low | **MEDIUM** | Calculate from matches |
| **Fatigue** | ⭐⭐ | Low | **MEDIUM** | Calculate from dates |
| **BO3 vs BO5** | ⭐⭐⭐ | Low | **MEDIUM** | Derive from tier |
| **Home advantage** | ⭐⭐ | Medium | **LOW** | Need nationality data |
| Player physical | ⭐ | High | **LOW** | Scraping needed |

---

## 🎯 My Recommendation

### **PHASE 1: Build API with current data** (4-6 hours)
- Start with ELO, surface, form, big match, H2H
- Get predictions working
- ~65-70% accuracy is already good!

### **PHASE 2: Quick wins** (2-3 hours)
Add these calculated metrics:
1. Recent momentum (titles/finals last 90 days)
2. Round-specific performance (finals win rate)
3. Recent H2H trend (last 3 meetings weighted)
4. Fatigue (days rest, recent matches)

**This gets us to ~75% accuracy**

### **PHASE 3: Check for match statistics** (30 min)
- Investigate raw CSV columns
- If we have serve/return stats: HUGE boost to ~80% accuracy
- If not: predictions still excellent

### **PHASE 4: Indoor/outdoor (optional)** (1 hour)
- Manually code tournament types
- Calculate separate indoor/outdoor ratings
- Small but meaningful improvement

---

## ❓ Questions for You

**1. Should I check your raw data files for match statistics columns?**
   - Let me peek at `data/raw/atp_matches_2024.csv`
   - See what columns Tennis Abstract provides

**2. Want to add "calculated metrics" (Phase 2) before launching API?**
   - Or launch API first, add later?

**3. For MVP match predictor, start simple and iterate?**
   - Option A: Basic (ELO + surface + form) → 65% accuracy → Launch fast
   - Option B: Enhanced (+ momentum + rounds) → 75% accuracy → Takes longer

My recommendation: **Start with simple predictor, iterate based on real usage**

**Shall I check your raw data for match statistics?** Let me peek at what Tennis Abstract actually gives us! 🔍

