# 🔌 API Endpoints - Complete Specification

**Version:** 1.0  
**Base URL:** `http://localhost:8000/api` (development)  
**Production:** `https://your-domain.com/api`

---

## 📋 Table of Contents

1. [Players](#players-endpoints) - 5 endpoints
2. [Rankings](#rankings-endpoints) - 4 endpoints
3. [Comparison](#comparison-endpoints) - 2 endpoints
4. [Dashboard](#dashboard-endpoints) - 3 endpoints
5. [Analysis](#analysis-endpoints) - 3 endpoints
6. [Prediction](#prediction-endpoints) - 1 endpoint
7. [Leaderboards](#leaderboards-endpoints) - 4 endpoints
8. [System](#system-endpoints) - 1 endpoint

**Total: 23 endpoints**

---

## 🎾 Players Endpoints

### **1. GET /api/players**

**Purpose:** List all players (paginated)

**Parameters:**
```
?limit=100        # Results per page (default: 100, max: 500)
?offset=0         # Pagination offset
?active=true      # Only active players (played in last 6 months)
?min_matches=100  # Minimum career matches
?sort_by=elo      # Sort by: elo, name, matches, grand_slams
```

**Example Request:**
```bash
GET /api/players?limit=50&active=true&min_matches=500&sort_by=elo
```

**Example Response:**
```json
{
  "total": 1243,
  "limit": 50,
  "offset": 0,
  "players": [
    {
      "name": "Jannik Sinner",
      "current_elo": 3379,
      "peak_elo": 3581,
      "career_matches": 2034,
      "grand_slams": 4,
      "is_active": true,
      "last_match": "2024-10-15"
    },
    {
      "name": "Carlos Alcaraz",
      "current_elo": 3198,
      "peak_elo": 3529,
      "career_matches": 1584,
      "grand_slams": 5,
      "is_active": true,
      "last_match": "2024-10-12"
    }
    // ... 48 more
  ]
}
```

**Use case:** Power the search page, player lists, dropdowns

---

### **2. GET /api/players/{name}**

**Purpose:** Get complete player summary

**Parameters:**
```
{name} = URL-encoded player name
Example: "Carlos Alcaraz" → "Carlos%20Alcaraz"
```

**Example Request:**
```bash
GET /api/players/Carlos%20Alcaraz
```

**Example Response:**
```json
{
  "name": "Carlos Alcaraz",
  "age": 22,
  "country": "ESP",
  "turned_pro": 2018,
  "is_active": true,
  
  "ratings": {
    "current": {
      "elo": 3198,
      "tsr": 3198,
      "tsr_uncertainty": 153,
      "glicko2": 3006,
      "glicko2_rd": 69
    },
    "peak": {
      "elo": 3529,
      "elo_date": "2022-09-11",
      "tsr": 3529,
      "glicko2": 3319
    }
  },
  
  "career_stats": {
    "total_matches": 1584,
    "wins": 1156,
    "losses": 428,
    "win_percentage": 73.0,
    "career_span": "2018-present"
  },
  
  "achievements": {
    "grand_slams": 5,
    "masters_1000": 6,
    "atp_500": 4,
    "atp_250": 2
  },
  
  "current_metrics": {
    "form_index": 95.0,
    "big_match_rating": 1.92,
    "tournament_success": 82.6
  },
  
  "surface_ratings": {
    "clay": {"current": 3100, "peak": 3200},
    "grass": {"current": 3150, "peak": 3317},
    "hard": {"current": 3200, "peak": 3529}
  }
}
```

**Use case:** Player profile page header, quick stats

---

### **3. GET /api/players/{name}/trajectory**

**Purpose:** Get all career data points for charting

**Parameters:**
```
?system=all          # all, elo, tsr, glicko2
?smoothed=true       # Include smoothed values
?start_date=2020-01-01
?end_date=2024-12-31
?min_match=100       # Start from match #100
?max_match=1000      # End at match #1000
```

**Example Request:**
```bash
GET /api/players/Carlos%20Alcaraz/trajectory?system=all&smoothed=true
```

**Example Response:**
```json
{
  "player": "Carlos Alcaraz",
  "total_matches": 1584,
  "data_points": [
    {
      "match_number": 1,
      "date": "2018-02-05",
      "elo": 1500,
      "tsr": 1500,
      "tsr_uncertainty": 200,
      "tsr_smoothed": 1510,
      "glicko2": 1500,
      "glicko2_rd": 80
    },
    {
      "match_number": 2,
      "date": "2018-02-07",
      "elo": 1512,
      "tsr": 1512,
      "tsr_uncertainty": 198,
      "tsr_smoothed": 1515,
      "glicko2": 1510,
      "glicko2_rd": 78
    }
    // ... 1582 more data points
  ]
}
```

**Use case:** 
- Interactive career charts
- Download data for analysis
- Comparing rating systems visually

**Note:** This could be ~1,500 data points - perfect for charts!

---

### **4. GET /api/players/{name}/stats**

**Purpose:** Detailed statistics and metrics

**Example Response:**
```json
{
  "player": "Carlos Alcaraz",
  
  "ratings_summary": {
    "elo": {
      "current": 3198,
      "peak": 3529,
      "peak_date": "2022-09-11",
      "current_rank": 2,
      "peak_rank": 1
    },
    "tsr": {
      "current": 3198,
      "uncertainty": 153,
      "smoothed": 3188,
      "peak": 3529,
      "avg_uncertainty": 145
    },
    "glicko2": {
      "current": 3006,
      "rd": 69,
      "volatility": 0.065,
      "peak": 3319
    }
  },
  
  "surface_breakdown": {
    "clay": {
      "current_elo": 3100,
      "peak_elo": 3200,
      "matches": 312,
      "win_rate": 78.2
    },
    "grass": {
      "current_elo": 3150,
      "peak_elo": 3317,
      "matches": 145,
      "win_rate": 81.4
    },
    "hard": {
      "current_elo": 3200,
      "peak_elo": 3529,
      "matches": 1127,
      "win_rate": 72.1
    }
  },
  
  "form_metrics": {
    "current_form": 95.0,
    "last_20_matches": "W-W-W-W-W-W-W-W-W-W-L-W-W-W-W-W-W-W-W-W",
    "current_streak": "10-match win streak",
    "form_trend": "improving"
  },
  
  "big_match_performance": {
    "rating": 1.92,
    "vs_top_10": "12-8 (60%)",
    "vs_top_20": "28-15 (65%)",
    "grand_slam_finals": "5-0 (100%)"
  },
  
  "achievements": {
    "grand_slams": {
      "total": 5,
      "wins": [
        {"tournament": "US Open", "year": 2022},
        {"tournament": "Wimbledon", "year": 2023},
        {"tournament": "French Open", "year": 2024},
        {"tournament": "Wimbledon", "year": 2024},
        {"tournament": "French Open", "year": 2025},
        {"tournament": "US Open", "year": 2025}
      ]
    },
    "masters_1000": 6,
    "atp_500": 4,
    "total_titles": 17
  },
  
  "career_progression": {
    "years_active": 7,
    "peak_year": 2022,
    "current_trajectory": "rising",
    "projected_peak_age": "24-26"
  }
}
```

**Use case:** Player profile page - complete statistics tab

---

### **5. POST /api/players/search**

**Purpose:** Search for players by name, fuzzy matching

**Request Body:**
```json
{
  "query": "alc",
  "limit": 10,
  "filters": {
    "active": true,
    "min_elo": 2500,
    "has_grand_slams": true
  }
}
```

**Example Response:**
```json
{
  "query": "alc",
  "results": [
    {
      "name": "Carlos Alcaraz",
      "match_score": 0.95,
      "current_elo": 3198,
      "is_active": true,
      "grand_slams": 5
    },
    {
      "name": "Alejandro Davidovich Fokina",
      "match_score": 0.42,
      "current_elo": 2650,
      "is_active": true,
      "grand_slams": 0
    }
  ]
}
```

**Use case:** Search bar with autocomplete

---

## 📊 Rankings Endpoints

### **6. GET /api/rankings/current**

**Purpose:** Current top 100 (or more) players

**Parameters:**
```
?limit=100        # Number of results
?system=elo       # elo, tsr, glicko2
?active=true      # Only active players
?min_date=2024-01-01  # Played since this date
```

**Example Request:**
```bash
GET /api/rankings/current?limit=20&system=elo&active=true
```

**Example Response:**
```json
{
  "as_of_date": "2025-10-18",
  "system": "elo",
  "total_ranked": 1243,
  "rankings": [
    {
      "rank": 1,
      "name": "Jannik Sinner",
      "rating": 3379,
      "uncertainty": 141,  // if TSR
      "form": 90.0,
      "last_match": "2025-10-15",
      "change_7d": +15,    // Rating change last 7 days
      "change_30d": +45
    },
    {
      "rank": 2,
      "name": "Carlos Alcaraz",
      "rating": 3198,
      "uncertainty": 153,
      "form": 95.0,
      "last_match": "2025-10-12",
      "change_7d": +8,
      "change_30d": -22
    }
    // ... 18 more
  ]
}
```

**Use case:** 
- Rankings table on homepage
- Current rankings page
- "Top 10" widgets

---

### **7. GET /api/rankings/all-time**

**Purpose:** All-time peak rankings

**Parameters:**
```
?metric=peak_elo       # peak_elo, peak_tsr, peak_glicko2
?limit=100
?min_matches=500       # Filter out players with few matches
```

**Example Response:**
```json
{
  "metric": "peak_elo",
  "description": "Highest ELO rating ever achieved",
  "rankings": [
    {
      "rank": 1,
      "name": "Novak Djokovic",
      "peak_elo": 3419,
      "peak_date": "2016-06-15",
      "age_at_peak": 29,
      "career_matches": 7061,
      "is_active": true
    },
    {
      "rank": 2,
      "name": "Jannik Sinner",
      "peak_elo": 3355,
      "peak_date": "2024-10-08",
      "age_at_peak": 23,
      "career_matches": 2034,
      "is_active": true
    }
    // ...
  ]
}
```

**Use case:**
- All-time rankings page
- "GOAT debate" comparisons
- Historical analysis

---

### **8. GET /api/rankings/surface/{surface}**

**Purpose:** Rankings by specific surface

**Parameters:**
```
{surface} = clay | grass | hard
?limit=100
?active=true
```

**Example Request:**
```bash
GET /api/rankings/surface/clay?limit=20
```

**Example Response:**
```json
{
  "surface": "clay",
  "as_of_date": "2025-10-18",
  "rankings": [
    {
      "rank": 1,
      "name": "Rafael Nadal",
      "clay_elo": 3512,
      "overall_elo": 3316,
      "clay_advantage": +196,
      "clay_matches": 1842,
      "clay_win_rate": 91.2,
      "french_open_titles": 14
    },
    {
      "rank": 2,
      "name": "Novak Djokovic",
      "clay_elo": 3315,
      "overall_elo": 3419,
      "clay_advantage": -104,
      "clay_matches": 1456,
      "clay_win_rate": 84.3,
      "french_open_titles": 3
    }
    // ...
  ]
}
```

**Use case:**
- Surface specialist rankings
- "King of Clay" debates
- Match predictions on specific surfaces

---

### **9. GET /api/rankings/era/{era}**

**Purpose:** Rankings within a specific era (era-adjusted)

**Parameters:**
```
{era} = big3-prime | big3-late | nextgen | 2010s | 2020s
?metric=dominance  # dominance (vs peers) or peak_elo
```

**Example Request:**
```bash
GET /api/rankings/era/nextgen?metric=dominance
```

**Example Response:**
```json
{
  "era": "nextgen",
  "period": "2023-2025",
  "era_average_elo": 2850,
  "description": "Rankings relative to era competition",
  "rankings": [
    {
      "rank": 1,
      "name": "Jannik Sinner",
      "peak_elo_in_era": 3355,
      "dominance_score": 225,  // Points above era average
      "matches_in_era": 373,
      "explanation": "Dominated 2024 season"
    },
    {
      "rank": 2,
      "name": "Carlos Alcaraz",
      "peak_elo_in_era": 3274,
      "dominance_score": 145,
      "matches_in_era": 348,
      "explanation": "Multiple Slams in era"
    }
    // ...
  ],
  "context": "Sinner's +225 dominance is similar to Djokovic's +252 in Big 3 Prime era"
}
```

**Use case:**
- Era comparison tool
- "Who dominated their era more?" analysis
- Historical context

---

## ⚖️ Comparison Endpoints

### **10. POST /api/compare**

**Purpose:** Compare multiple players side-by-side

**Request Body:**
```json
{
  "players": ["Carlos Alcaraz", "Jannik Sinner", "Novak Djokovic"],
  "metrics": ["all"],  // or specific: ["elo", "grand_slams", "form"]
  "align_by": "age"    // age, matches, or calendar_time
}
```

**Example Response:**
```json
{
  "players": [
    {
      "name": "Carlos Alcaraz",
      "age": 22,
      "current_elo": 3198,
      "peak_elo": 3529,
      "grand_slams": 5,
      "career_matches": 1584,
      "form": 95.0,
      "big_match": 1.92,
      "tournament_success": 82.6,
      "tsr_uncertainty": 153
    },
    {
      "name": "Jannik Sinner",
      "age": 23,
      "current_elo": 3379,
      "peak_elo": 3581,
      "grand_slams": 4,
      "career_matches": 2034,
      "form": 90.0,
      "big_match": 1.24,
      "tournament_success": 73.4,
      "tsr_uncertainty": 141
    },
    {
      "name": "Novak Djokovic",
      "age": 37,
      "current_elo": 3104,
      "peak_elo": 3419,
      "grand_slams": 24,
      "career_matches": 7061,
      "form": 85.0,
      "big_match": -0.79,
      "tournament_success": 57.9,
      "tsr_uncertainty": 123
    }
  ],
  "comparison_insights": [
    "Alcaraz has more Grand Slams at age 22 than Djokovic had at same age",
    "Sinner currently ranked #1 by ELO",
    "Djokovic has lowest uncertainty (most reliable rating)"
  ]
}
```

**Use case:** Comparison page, multi-player charts

---

### **11. GET /api/compare/head-to-head/{player1}/{player2}**

**Purpose:** Head-to-head record between two players

**Example Request:**
```bash
GET /api/compare/head-to-head/Carlos%20Alcaraz/Jannik%20Sinner
```

**Example Response:**
```json
{
  "player1": "Carlos Alcaraz",
  "player2": "Jannik Sinner",
  "overall_record": {
    "player1_wins": 4,
    "player2_wins": 4,
    "total_matches": 8
  },
  "by_surface": {
    "clay": {"p1": 2, "p2": 1},
    "grass": {"p1": 0, "p2": 1},
    "hard": {"p1": 2, "p2": 2}
  },
  "by_tournament_tier": {
    "grand_slam": {"p1": 1, "p2": 1},
    "masters_1000": {"p1": 2, "p2": 1},
    "atp_500": {"p1": 1, "p2": 2}
  },
  "recent_meetings": [
    {
      "date": "2024-10-08",
      "tournament": "Beijing",
      "surface": "hard",
      "round": "F",
      "winner": "Carlos Alcaraz",
      "score": "6-4, 7-6(3)",
      "player1_elo_before": 3180,
      "player2_elo_before": 3350,
      "upset": true
    }
    // ... 7 more matches
  ],
  "stat_summary": {
    "avg_elo_diff": 45,  // Sinner usually rated higher
    "closest_match": "2024 Beijing F",
    "biggest_upset": "2023 Indian Wells",
    "trend": "Even - rivalry is balanced"
  }
}
```

**Use case:** 
- Player profile head-to-head section
- Rivalry analysis
- Match predictions

---

## 🏠 Dashboard Endpoints

### **12. GET /api/dashboard/top10**

**Purpose:** Quick current top 10 for homepage

**Example Response:**
```json
{
  "as_of": "2025-10-18",
  "top10": [
    {
      "rank": 1,
      "name": "Jannik Sinner",
      "elo": 3379,
      "form": 90.0,
      "change_week": "+15 ↑",
      "flag": "🇮🇹"
    }
    // ... 9 more
  ]
}
```

**Use case:** Homepage widget

---

### **13. GET /api/dashboard/trending**

**Purpose:** Players with biggest changes (hot/cold)

**Parameters:**
```
?period=30d      # 7d, 30d, 90d
?metric=elo      # elo, form, ranking_position
?direction=up    # up (trending up), down (trending down), both
```

**Example Response:**
```json
{
  "period": "30 days",
  "trending_up": [
    {
      "name": "Jack Draper",
      "elo_change": +200,
      "elo_current": 2869,
      "form_change": +25,
      "reason": "10-match win streak including ATP 500 title"
    }
    // ...
  ],
  "trending_down": [
    {
      "name": "Player X",
      "elo_change": -150,
      "elo_current": 2450,
      "form_change": -30,
      "reason": "Injured, 0-5 in last 5"
    }
  ]
}
```

**Use case:** Homepage "trending" section, interesting insights

---

### **14. GET /api/dashboard/stat-of-day**

**Purpose:** Random interesting statistic for homepage

**Example Response:**
```json
{
  "stat": "Djokovic has been #1 for 428 weeks - more than anyone in history",
  "category": "longevity",
  "players_mentioned": ["Novak Djokovic"],
  "context": "That's over 8 years at #1!",
  "source": "ATP ranking history 2003-2025"
}
```

**Rotation:** Different stat each day or random selection

**Use case:** Homepage engagement, shareable facts

---

## 🔬 Analysis Endpoints

### **15. GET /api/analysis/goat-debate**

**Purpose:** Big 3 statistical comparison

**Example Response:**
```json
{
  "players": ["Novak Djokovic", "Rafael Nadal", "Roger Federer"],
  "categories": {
    "grand_slams": {
      "winner": "Novak Djokovic",
      "values": {"Djokovic": 24, "Nadal": 22, "Federer": 20}
    },
    "peak_elo": {
      "winner": "Novak Djokovic",
      "values": {"Djokovic": 3419, "Nadal": 3316, "Federer": 3264}
    },
    "weeks_at_1": {
      "winner": "Novak Djokovic",
      "values": {"Djokovic": 428, "Nadal": 209, "Federer": 310}
    },
    "masters_1000": {
      "winner": "Novak Djokovic",
      "values": {"Djokovic": 40, "Nadal": 36, "Federer": 28}
    },
    "era_dominance": {
      "winner": "Novak Djokovic",
      "values": {"Djokovic": 252, "Nadal": 149, "Federer": 97},
      "explanation": "Points above era peers"
    }
  },
  "statistical_goat": "Novak Djokovic",
  "categories_won": {"Djokovic": 5, "Nadal": 0, "Federer": 0},
  "conclusion": "Djokovic leads in all major statistical categories"
}
```

**Use case:** GOAT debate page, settling arguments with data!

---

### **16. GET /api/analysis/nextgen**

**Purpose:** Track Alcaraz vs Sinner vs historical GOATs at same age

**Example Response:**
```json
{
  "current_stars": ["Carlos Alcaraz", "Jannik Sinner"],
  "comparison_at_age_22": {
    "carlos_alcaraz": {
      "grand_slams": 5,
      "peak_elo": 3529,
      "career_matches": 990
    },
    "rafael_nadal_at_22": {
      "grand_slams": 5,
      "peak_elo": 3144,
      "career_matches": 1200
    },
    "novak_djokovic_at_22": {
      "grand_slams": 1,
      "peak_elo": 2950,
      "career_matches": 980
    },
    "roger_federer_at_22": {
      "grand_slams": 0,
      "peak_elo": 2800,
      "career_matches": 850
    }
  },
  "verdict": "Alcaraz is matching Nadal's GOAT pace!",
  "projections": {
    "alcaraz_projected_slams_at_30": "18-25 (if maintains pace)",
    "sinner_projected_slams_at_30": "15-20"
  }
}
```

**Use case:** NextGen tracker page, future GOAT speculation

---

### **17. GET /api/analysis/era-comparison**

**Purpose:** Compare players from different eras fairly

**Parameters:**
```
?players=Djokovic,Sinner
?metric=dominance  # dominance, achievements, peak_elo
```

**Example Response:**
```json
{
  "players": [
    {
      "name": "Novak Djokovic",
      "era": "Big 3 Prime (2010-2016)",
      "peak_elo": 3419,
      "era_average": 2850,
      "dominance": 252,
      "rank_in_era": 1
    },
    {
      "name": "Jannik Sinner",
      "era": "NextGen (2023-2025)",
      "peak_elo": 3355,
      "era_average": 2825,
      "dominance": 225,
      "rank_in_era": 1
    }
  ],
  "comparison": {
    "raw_elo_winner": "Djokovic (+64 ELO)",
    "era_dominance_winner": "Djokovic (+27 dominance)",
    "conclusion": "Both dominated their eras similarly",
    "fair_comparison": "Sinner is dominating 2024 like Djokovic dominated 2015"
  },
  "caveat": "Raw ELO comparisons across eras are invalid. Compare dominance instead."
}
```

**Use case:** 
- Era comparison tool
- "Can we compare Federer to Alcaraz?" questions
- Historical context

---

## 🎯 Prediction Endpoints

### **18. GET /api/predict/match**

**Purpose:** Predict outcome of any hypothetical match ⭐

**Parameters:**
```
?player1=Carlos%20Alcaraz
?player2=Jannik%20Sinner
?surface=hard         # clay, grass, hard
?tournament_tier=grand_slam  # Optional: grand_slam, masters_1000, etc.
```

**Example Request:**
```bash
GET /api/predict/match?player1=Carlos%20Alcaraz&player2=Jannik%20Sinner&surface=hard
```

**Example Response:**
```json
{
  "player1": {
    "name": "Carlos Alcaraz",
    "current_elo": 3198,
    "surface_elo": 3200,
    "form": 95.0,
    "big_match_rating": 1.92
  },
  "player2": {
    "name": "Jannik Sinner",
    "current_elo": 3379,
    "surface_elo": 3350,
    "form": 90.0,
    "big_match_rating": 1.24
  },
  "prediction": {
    "player1_win_probability": 42.3,
    "player2_win_probability": 57.7,
    "confidence": "medium",
    "expected_closeness": "close_match"
  },
  "factors": {
    "elo_advantage": "Sinner +181",
    "surface_advantage": "Sinner +150",
    "form_advantage": "Alcaraz +5%",
    "big_match_advantage": "Alcaraz +0.68",
    "head_to_head": "4-4 (even)"
  },
  "breakdown": {
    "base_probability": 35.0,  // Based on ELO alone
    "surface_adjusted": 38.0,   // Adjusted for surface
    "form_adjusted": 42.0,      // Adjusted for current form
    "final": 42.3
  },
  "expected_score": "2-1 or 1-2 (tight match)",
  "betting_suggestion": "Slight edge to Sinner but Alcaraz's form makes it close",
  "similar_past_matches": [
    {
      "date": "2024-10-08",
      "winner": "Alcaraz",
      "elo_diff": 170,
      "actual_result": "Alcaraz won despite being underdog"
    }
  ]
}
```

**Algorithm:**
```python
# Simplified prediction formula:
base_prob = 1 / (1 + 10^(-elo_diff/400))

# Adjust for surface
surface_adjusted = apply_surface_elo(base_prob)

# Adjust for form
if form_diff > 10:
    form_adjusted += 5%

# Adjust for big match rating (if both in top 20)
if big_match_diff > 2:
    add bonus

# Final probability
final = weighted_average(elo, surface, form, big_match)
```

**Use case:**
- Match predictor page ⭐
- "Who would win?" questions
- Betting insights
- Hypothetical matchups

---

## 🏆 Leaderboards Endpoints

### **19. GET /api/leaderboards/giant-killers**

**Purpose:** Players with highest big match ratings

**Example Response:**
```json
{
  "title": "Biggest Giant Killers",
  "metric": "big_match_rating",
  "description": "Players who most consistently beat higher-ranked opponents",
  "leaderboard": [
    {
      "rank": 1,
      "name": "Arthur Fils",
      "big_match_rating": 8.02,
      "current_elo": 2895,
      "explanation": "Beats players 200+ ELO higher regularly",
      "notable_wins": ["Beat Djokovic (3200) at Paris 2024"]
    },
    {
      "rank": 2,
      "name": "Jack Draper",
      "big_match_rating": 7.45,
      "current_elo": 2869,
      "explanation": "Massive overperformer vs top 20"
    }
    // ...
  ]
}
```

**Use case:** Finding dangerous underdogs, upset specials

---

### **20. GET /api/leaderboards/most-consistent**

**Purpose:** Players with lowest TSR uncertainty

**Example Response:**
```json
{
  "title": "Most Consistent Players",
  "metric": "tsr_uncertainty",
  "description": "Players with most reliable ratings (lowest uncertainty)",
  "leaderboard": [
    {
      "rank": 1,
      "name": "Roger Federer",
      "tsr_uncertainty": 120.9,
      "career_matches": 7663,
      "peak_elo": 3587,
      "explanation": "Decades of consistent performance"
    },
    {
      "rank": 2,
      "name": "Novak Djokovic",
      "tsr_uncertainty": 123.0,
      "career_matches": 7061,
      "peak_elo": 3727
    }
    // ...
  ],
  "insight": "Veterans with 4000+ matches have lowest uncertainty"
}
```

**Use case:** Finding reliable players, understanding rating confidence

---

### **21. GET /api/leaderboards/peak-elo**

**Purpose:** Highest peaks ever (same as all-time rankings but different format)

---

### **22. GET /api/leaderboards/hot-streak**

**Purpose:** Players with best current form

**Example Response:**
```json
{
  "title": "Hottest Players (Last 30 days)",
  "players": [
    {
      "rank": 1,
      "name": "Carlos Alcaraz",
      "form": 95.0,
      "streak": "19-1 in last 20",
      "current_streak": "10-match win streak",
      "elo_change_30d": +120
    }
    // ...
  ]
}
```

**Use case:** "Who's hot right now?" for betting/predictions

---

## 🔧 System Endpoints

### **23. GET /api/health**

**Purpose:** API health check

**Example Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "total_players": 25811,
  "total_matches": 1076839,
  "last_data_update": "2025-10-18",
  "api_version": "1.0.0"
}
```

**Use case:** Monitoring, status page

---

## 📝 Common Patterns

### **Pagination:**
```
All list endpoints support:
?limit=100    # Results per page
?offset=0     # Skip N results
```

### **Filtering:**
```
?active=true         # Only active players
?min_matches=100     # Minimum career matches
?min_elo=2500        # Minimum ELO
?date_from=2020-01-01
?date_to=2024-12-31
```

### **Sorting:**
```
?sort_by=elo         # Field to sort by
?order=desc          # asc or desc
```

### **Response Format:**
```json
{
  "data": { ... },           // Main data
  "metadata": {              // Always included
    "timestamp": "2025-10-18T21:00:00Z",
    "execution_time_ms": 45,
    "cached": false
  }
}
```

---

## 🎯 MVP Priority Order

**Build these first (Phase 3A - 4-6 hours):**

1. ✅ `/api/players/{name}` - Player summary
2. ✅ `/api/players/{name}/trajectory` - For charts
3. ✅ `/api/rankings/current` - Top 100
4. ✅ `/api/compare` - Comparison tool
5. ✅ `/api/players/search` - Search
6. ✅ `/api/dashboard/top10` - Homepage

**Then add (Phase 3B - 3-4 hours):**

7. ✅ `/api/predict/match` ⭐ - Your favorite!
8. ✅ `/api/leaderboards/*` - Various leaderboards
9. ✅ `/api/analysis/goat-debate` - Big 3 stats
10. ✅ `/api/compare/head-to-head` - H2H records

---

## 💡 Notes

**Authentication:** Not needed for MVP (public data)

**Rate Limiting:** Can add later if needed

**Caching:** 
- Cache expensive queries (trajectories, rankings)
- TTL: 1 hour for current data, 1 day for historical

**CORS:**
- Enable for frontend development
- Restrict in production if needed

---

## ❓ Questions Before We Start?

1. **Endpoint priorities look good?**
2. **Any endpoints you'd add/remove?**
3. **Match predictor algorithm makes sense?**
4. **Response format looks useful?**

**Say "let's build it" and I'll start creating the FastAPI structure!** 🚀

