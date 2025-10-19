# ⚖️ Rating Systems Comparison: ELO vs TSR vs Glicko-2

**Last Updated**: October 19, 2025  
**Database**: 743,928 matches | 25,840 players | Complete 2025 season

---

## 📊 Quick Summary

### **Top 3 Rankings (All Systems Agree)**

| Rank | Player | ELO | TSR | Glicko-2 | Matches |
|------|--------|-----|-----|----------|---------|
| 1 | **Carlos Alcaraz** | 2809.0 | 2809.0 | 2541.8 | 414 |
| 2 | **Jannik Sinner** | 2704.0 | 2704.0 | 2523.2 | 452 |
| 3 | **Novak Djokovic** | 2520.9 | 2520.9 | 2410.8 | 1444 |

---

## 🔬 Methodology Comparison

### **1. ELO Rating**

**Formula**: `New Rating = Old Rating + K × (Actual - Expected)`

- **Origin**: Chess (Arpad Elo, 1960s)
- **Starting Rating**: 1500
- **K-Factor**: 32-64 (decreases with experience)
- **Range**: ~1200-2900
- **Update**: After every match

**Pros:**
- ✅ Simple and interpretable
- ✅ Fast calculation
- ✅ Proven over decades
- ✅ Easy to compare across eras

**Cons:**
- ❌ No uncertainty measure
- ❌ Doesn't account for rating confidence
- ❌ No volatility tracking

---

### **2. TSR (Tennis Skill Rating with Bayesian Uncertainty)**

**Formula**: `Rating = ELO ± Uncertainty`

- **Origin**: ELO enhanced with Bayesian statistics
- **Starting Rating**: 1500 ± 350
- **Base**: Same as ELO
- **Uncertainty**: Bayesian 95% confidence interval
- **Update**: After every match (rating + uncertainty)

**Pros:**
- ✅ Includes confidence intervals
- ✅ Better for comparing players with different experience
- ✅ Statistical rigor
- ✅ Same scale as ELO

**Cons:**
- ❌ More complex calculations
- ❌ Requires more computational resources
- ❌ Uncertainty can be confusing for casual users

**Example:**
- Alcaraz: 2809 ± 145 → **True skill likely between 2664-2954**
- Djokovic: 2521 ± 113 → **True skill likely between 2408-2634** (more certain due to 1444 matches)

---

### **3. Glicko-2 Rating**

**Formula**: `Rating + RD (Rating Deviation) + σ (Volatility)`

- **Origin**: Mark Glickman (1999, updated 2001)
- **Starting Rating**: 1500
- **RD (Rating Deviation)**: 350 (new player) → ~60 (experienced)
- **Volatility (σ)**: Measures rating stability
- **Range**: ~1500-2600
- **Update**: After rating periods (time-based)

**Pros:**
- ✅ Tracks rating stability/consistency
- ✅ Handles inactive periods well
- ✅ Measures player volatility
- ✅ Dynamic K-factor based on RD

**Cons:**
- ❌ Different scale from ELO (harder to compare)
- ❌ More parameters to tune
- ❌ Less intuitive for general audience

**Metrics:**
- **RD (Rating Deviation)**: 57-68 = very confident, >100 = uncertain
- **σ (Volatility)**: 0.06 = stable, >0.10 = erratic

---

## 📈 Top 10 Rankings - System Comparison

### **Consensus Rankings (All 3 Systems)**

**Positions 1-3: IDENTICAL**
1. Carlos Alcaraz
2. Jannik Sinner  
3. Novak Djokovic

**Positions 4-10: Minor Variations**

| Rank | ELO/TSR | Glicko-2 |
|------|---------|----------|
| 4 | Arthur Fils | Taylor Fritz |
| 5 | Taylor Fritz | Alexander Zverev |
| 6 | Alex De Minaur | Jack Draper |
| 7 | Jiri Lehecka | Alex De Minaur |
| 8 | Jack Draper | Hubert Hurkacz |
| 9 | Lorenzo Musetti | Grigor Dimitrov |
| 10 | Grigor Dimitrov | Lorenzo Musetti |

### **Key Differences (Positions 4-10)**

**Only in ELO/TSR Top 10:**
- Arthur Fils (high rating, fewer matches)
- Jiri Lehecka (strong recent form)

**Only in Glicko-2 Top 10:**
- Alexander Zverev (752 matches, consistent)
- Hubert Hurkacz (445 matches, stable)

---

## 🔍 Uncertainty & Confidence Metrics

### **TSR Uncertainty (95% Confidence Intervals)**

| Player | Rating | Uncertainty | Range | Matches |
|--------|--------|-------------|-------|---------|
| Novak Djokovic | 2521 | ±113.0 | 2408-2634 | 1444 |
| Jannik Sinner | 2704 | ±123.9 | 2580-2828 | 452 |
| Alex De Minaur | 2374 | ±125.6 | 2248-2500 | 492 |
| Grigor Dimitrov | 2326 | ±126.8 | 2199-2453 | 841 |
| Lorenzo Musetti | 2349 | ±127.3 | 2222-2476 | 387 |
| Taylor Fritz | 2381 | ±128.0 | 2253-2509 | 552 |
| Jiri Lehecka | 2373 | ±128.6 | 2244-2501 | 350 |
| Jack Draper | 2357 | ±137.8 | 2220-2495 | 315 |
| Arthur Fils | 2387 | ±139.1 | 2248-2526 | 260 |
| **Carlos Alcaraz** | **2809** | **±145.2** | **2664-2954** | **414** |

**Insights:**
- 💡 **Djokovic has lowest uncertainty** (±113) - most reliable rating
- 💡 **Alcaraz has highest uncertainty** (±145) - still establishing peak
- 💡 More matches = lower uncertainty (experience matters)

### **Glicko-2 Deviation & Volatility**

| Player | Rating | RD | Volatility | Confidence |
|--------|--------|-----|-----------|------------|
| Arthur Fils | 2194.4 | 57.1 | 0.06 | Very High |
| Grigor Dimitrov | 2211.2 | 58.8 | 0.06 | Very High |
| Lorenzo Musetti | 2205.1 | 58.8 | 0.06 | Very High |
| Jiri Lehecka | 2200.2 | 59.5 | 0.06 | Very High |
| Jack Draper | 2253.8 | 60.0 | 0.06 | High |
| Alex De Minaur | 2247.9 | 60.4 | 0.06 | High |
| Taylor Fritz | 2280.9 | 61.2 | 0.06 | High |
| Novak Djokovic | 2410.8 | 64.7 | 0.06 | High |
| Carlos Alcaraz | 2541.8 | 65.0 | 0.06 | High |
| Jannik Sinner | 2523.2 | 67.9 | 0.06 | High |

**Insights:**
- 💡 **All players have low volatility** (0.06) - consistent performers
- 💡 **Lower RD = more certain** (57-68 = very confident)
- 💡 Glicko-2 confidence independent of match count (based on recent performance)

---

## 🎯 When To Use Each System

### **Use ELO for:**
✅ Homepage rankings  
✅ General audience visualizations  
✅ Historical comparisons (Big 3 vs NextGen)  
✅ Simple, interpretable numbers  
✅ Era-adjusted analysis  

### **Use TSR for:**
✅ Match predictions with confidence ranges  
✅ Statistical analysis  
✅ Comparing players with vastly different experience  
✅ Risk-adjusted rankings  
✅ "What if" scenarios  

### **Use Glicko-2 for:**
✅ Consistency tracking  
✅ Form analysis  
✅ Volatility detection (hot streaks vs slumps)  
✅ Advanced statistical modeling  
✅ Handling inactive players  

---

## 🏆 Recommendation for Tennis Career Tracker

### **Primary System: ELO**
- Most familiar to users
- Industry standard
- Easy to understand and visualize

### **Secondary System: TSR**
- For match predictions
- Show confidence ranges
- Statistical deep dives

### **Tertiary System: Glicko-2**
- "Advanced Stats" section
- Consistency metrics
- Volatility analysis

### **UI Implementation:**

**Homepage:**
```
Top 10 Rankings (ELO)
1. Carlos Alcaraz    2809  [View Profile]
2. Jannik Sinner     2704  [View Profile]
...
```

**Player Profile:**
```
Tabs: [ELO] [TSR] [Glicko-2]

ELO Tab:
- Current: 2809 (#1 in world)
- Career trajectory chart

TSR Tab:  
- Rating: 2809 ± 145
- 95% confidence: 2664-2954
- Uncertainty vs peers chart

Glicko-2 Tab:
- Rating: 2542
- Deviation: 65 (High confidence)
- Volatility: 0.06 (Stable)
- Consistency chart
```

**Match Predictor:**
```
Alcaraz (2809 ± 145) vs Sinner (2704 ± 124)
Win Probability: 65-85% Alcaraz
(Uses TSR with uncertainty)
```

---

## 📊 Data Files Generated

All three systems have dedicated CSV exports:

```
data/processed/
├── elo_only/
│   ├── top10_current.csv
│   ├── carlos_alcaraz_career.csv
│   ├── jannik_sinner_career.csv
│   └── ...
│
├── tsr_with_bayesian/
│   ├── top10_current.csv
│   ├── carlos_alcaraz_career.csv
│   └── ...
│
└── glicko2/
    ├── top10_current.csv
    ├── carlos_alcaraz_career.csv
    └── ...
```

---

## 🎯 Bottom Line

**All three systems confirm:**
- 🥇 Carlos Alcaraz is #1 (2025 dominant season: 64-6, 8 titles)
- 🥈 Jannik Sinner is #2 (hard court specialist)
- 🥉 Novak Djokovic is #3 (generational transition underway)

**For your app:**
- **Primary**: ELO (simple, familiar)
- **Advanced**: TSR (predictions, confidence)
- **Deep Dive**: Glicko-2 (consistency, volatility)

**All three add value - use them for different purposes!** 🎾

