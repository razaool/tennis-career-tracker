# 🎾 Rating Systems Quick Reference Guide

**TL;DR**: All 3 systems agree on top 3. Use ELO for simplicity, TSR for predictions, Glicko-2 for consistency.

---

## 📊 The Three Systems

| Feature | ELO | TSR | Glicko-2 |
|---------|-----|-----|----------|
| **Scale** | 1200-2900 | 1200-2900 | 1500-2600 |
| **Starting Rating** | 1500 | 1500 ± 350 | 1500 (RD=350) |
| **Complexity** | ⭐ Simple | ⭐⭐ Moderate | ⭐⭐⭐ Complex |
| **Uncertainty** | ❌ No | ✅ Yes (±range) | ✅ Yes (RD) |
| **Volatility** | ❌ No | ❌ No | ✅ Yes |
| **Time Decay** | ❌ No | ❌ No | ✅ Yes |
| **Best For** | Rankings | Predictions | Consistency |

---

## 🏆 Current Top 3 (All Systems Agree)

```
#1  Carlos Alcaraz  
    ELO: 2809  |  TSR: 2809 ± 145  |  Glicko-2: 2542

#2  Jannik Sinner
    ELO: 2704  |  TSR: 2704 ± 124  |  Glicko-2: 2523

#3  Novak Djokovic
    ELO: 2521  |  TSR: 2521 ± 113  |  Glicko-2: 2411
```

---

## 🔍 Quick Comparison

### **Alcaraz vs Sinner**

| Metric | Alcaraz | Sinner | Advantage |
|--------|---------|--------|-----------|
| **ELO Rating** | 2809 | 2704 | Alcaraz +105 🔥 |
| **TSR Uncertainty** | ±145 | ±124 | Sinner (more certain) |
| **Glicko-2** | 2542 | 2523 | Alcaraz +19 |
| **Glicko-2 RD** | 65.0 | 67.9 | Alcaraz (more certain) |
| **Matches Played** | 414 | 452 | Sinner +38 |
| **2025 Record** | 64-6 (91.4%) | ~50+ wins | Alcaraz |
| **2025 H2H** | 4-1 | 1-4 | Alcaraz 🏆 |

**Verdict**: Alcaraz dominates across all metrics despite fewer career matches.

---

## 🎯 Which System To Use?

### **For Your App:**

```
┌─────────────────────────────────────────────────┐
│  Homepage / Leaderboards                        │
│  → ELO (2809)                                   │
│                                                 │
│  Player Profile - Basic View                    │
│  → ELO (2809) with career chart                │
│                                                 │
│  Player Profile - Advanced View                 │
│  → TSR (2809 ± 145) with confidence bands      │
│                                                 │
│  Player Profile - Stats Nerd View               │
│  → Glicko-2 (2542, RD=65, σ=0.06)              │
│                                                 │
│  Match Predictor                                │
│  → TSR (shows win probability range)           │
│                                                 │
│  Consistency Analysis                           │
│  → Glicko-2 volatility tracking                │
└─────────────────────────────────────────────────┘
```

---

## 💡 Key Insights

### **Why ELO and TSR are identical?**
- TSR = ELO + uncertainty estimates
- For experienced players (100+ matches), the core rating is the same
- TSR adds value by showing confidence: "2809 ± 145"

### **Why is Glicko-2 different?**
- Different mathematical foundation
- Uses rating deviation (RD) instead of fixed K-factor
- Incorporates volatility to track consistency
- Lower scale (2542 vs 2809)

### **Which is "correct"?**
- **All three are valid!** They measure slightly different things:
  - **ELO**: Pure skill based on wins/losses
  - **TSR**: Skill + confidence in the measurement
  - **Glicko-2**: Skill + consistency + stability

---

## 📈 Surface Ratings (All Systems Use ELO-Based)

| Player | Clay | Grass | Hard | Best Surface |
|--------|------|-------|------|--------------|
| **Alcaraz** | 2516 | 2037 | 2478 | Clay 🏆 |
| **Sinner** | 2329 | 1988 | 2544 | Hard 🏆 |
| **Djokovic** | 2404 | 2128 | 2321 | Clay |

**Battle of the Generations:**
- Alcaraz dominates clay (+187 over Sinner)
- Sinner edges hard courts (+67 over Alcaraz)
- Alcaraz slightly better on grass (+50)

---

## 🔢 The Math (Simplified)

### **ELO**
```
New Rating = Old Rating + K × (Actual - Expected)
Expected = 1 / (1 + 10^((Opponent - Your Rating)/400))
K = 32-64 (decreases with experience)
```

### **TSR**
```
Rating = ELO
Uncertainty = sqrt(variance from Bayesian model)
Confidence Interval = Rating ± (1.96 × Uncertainty)
```

### **Glicko-2**
```
Rating update based on RD (not fixed K)
RD = rating deviation (uncertainty)
σ = volatility (how erratic the rating is)
```

---

## 📊 Files Available

### **Main Directory** (`data/processed/`)
- `top10_current.csv` - Top 10 by ELO
- `carlos_alcaraz_career.csv` - Full career trajectory
- `big3_comparison.csv` - Djokovic, Nadal, Federer
- `nextgen_comparison.csv` - Alcaraz, Sinner, Rune
- `*_surfaces.csv` - Surface breakdowns

### **ELO Directory** (`data/processed/elo_only/`)
- Pure ELO ratings for all players
- Best for historical comparisons

### **TSR Directory** (`data/processed/tsr_with_bayesian/`)
- ELO + uncertainty estimates
- Best for predictions

### **Glicko-2 Directory** (`data/processed/glicko2/`)
- Advanced ratings with volatility
- Best for consistency analysis

---

## 🎯 Bottom Line

**For 99% of use cases: Use ELO**
- Familiar scale
- Easy to understand
- Industry standard

**For predictions: Use TSR**
- Includes confidence ranges
- Better for "what if" scenarios

**For deep analysis: Use Glicko-2**
- Consistency metrics
- Form tracking
- Volatility detection

**All three systems confirm: Carlos Alcaraz is the #1 player in the world in 2025** 🏆

---

## 📚 Further Reading

- Full comparison: `docs/technical/RATING_SYSTEMS_COMPARISON.md`
- System explanations: `docs/RANKING_SYSTEMS_EXPLAINED.md`
- Data files: `data/processed/` (24 CSV files)

