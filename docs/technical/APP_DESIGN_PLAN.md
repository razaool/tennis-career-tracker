# 🎾 Tennis Career Tracker - App Design Plan

**Date:** October 18, 2025  
**Status:** Planning Phase  
**Database:** Complete (5.36M records, 3 rating systems, all metrics)

---

## 🎯 App Vision

**Purpose:** The ultimate tennis analytics platform - track players across eras, compare rating systems, analyze career trajectories, and discover insights from 48 years of tennis history.

**Target Users:**
- Tennis fans wanting player stats
- Sports analysts comparing players
- Bettors analyzing form and matchups
- Data scientists exploring tennis data
- Journalists researching tennis history

---

## 📱 Proposed Pages & Features

### **1. HOME PAGE / DASHBOARD** 🏠

**Purpose:** Overview of current tennis world + navigation hub

**Sections:**
```
┌─────────────────────────────────────────────────────────────┐
│ CURRENT TOP 10 (Live Rankings)                             │
│ ┌────┬───────────────────┬──────┬────────┬──────┬─────────┐│
│ │ #  │ Player            │ ELO  │ Form%  │ Glicko│ Country ││
│ ├────┼───────────────────┼──────┼────────┼──────┼─────────┤│
│ │ 1  │ Jannik Sinner     │ 3379 │ 90%    │ 3372  │ 🇮🇹      ││
│ │ 2  │ Carlos Alcaraz    │ 3198 │ 95%    │ 3006  │ 🇪🇸      ││
│ └────┴───────────────────┴──────┴────────┴──────┴─────────┘│
│                                                             │
│ TRENDING PLAYERS (Biggest form gains this month)           │
│ • Jack Draper: +200 ELO in 30 days                        │
│ • Joao Fonseca: 10-match win streak                       │
│                                                             │
│ HISTORICAL STAT OF THE DAY                                 │
│ "Did you know? Djokovic has been #1 for 428 weeks!"       │
└─────────────────────────────────────────────────────────────┘
```

**API Needs:**
- GET /rankings/current?limit=10
- GET /stats/trending?period=30d
- GET /stats/random-fact

---

### **2. PLAYER PROFILE PAGE** 👤

**Purpose:** Complete player dossier - everything about one player

**URL:** `/player/carlos-alcaraz`

**Sections:**

#### **A. Header / Quick Stats**
```
┌─────────────────────────────────────────────────────────────┐
│ CARLOS ALCARAZ                               🇪🇸            │
│ Age: 22 | Turned Pro: 2018 | Active                        │
├─────────────────────────────────────────────────────────────┤
│ Current Ranking: #2        Peak Ranking: #1 (2024)         │
│ Current ELO: 3,198         Peak ELO: 3,529 (2022)          │
│ Grand Slams: 5             Masters 1000: X                  │
│ Career Matches: 1,584      Win Rate: 73%                   │
└─────────────────────────────────────────────────────────────┘
```

**API:** GET /players/{name}/summary

---

#### **B. Career Trajectory Chart** 📈
```
Interactive line chart:
- X-axis: Time (or match number)
- Y-axis: Rating
- Multiple lines: ELO, TSR Smoothed, Glicko-2
- Shaded area: TSR uncertainty bands
- Markers: Grand Slam wins

User can toggle:
☑ Show ELO
☑ Show TSR with confidence bands
☑ Show Glicko-2
☑ Show major wins
☑ Compare to another player
```

**API:** GET /players/{name}/trajectory?system=all&smooth=true

---

#### **C. Rating Systems Comparison**
```
┌────────────┬─────────┬─────────────┬──────────┐
│ System     │ Current │ Peak        │ When     │
├────────────┼─────────┼─────────────┼──────────┤
│ ELO        │ 3,198   │ 3,529       │ Sep 2022 │
│ TSR        │ 3,198   │ 3,529 ±145  │ Sep 2022 │
│ Glicko-2   │ 3,006   │ 3,319 ±66   │ Aug 2022 │
└────────────┴─────────┴─────────────┴──────────┘
```

**API:** GET /players/{name}/ratings/all-systems

---

#### **D. Surface Breakdown**
```
Surface Performance:
┌────────┬──────────┬──────────┬───────────┐
│Surface │ Current  │ Peak     │ W-L       │
├────────┼──────────┼──────────┼───────────┤
│ Clay   │ 3,100    │ 3,200    │ 45-12     │
│ Grass  │ 3,150    │ 3,317    │ 38-8      │
│ Hard   │ 3,200    │ 3,529    │ 125-40    │
└────────┴──────────┴──────────┴───────────┘

Best Surface: Hard (highest peak)
```

**API:** GET /players/{name}/surfaces

---

#### **E. Form & Performance Metrics**
```
Current Metrics (Last 6 months):
┌────────────────────────┬─────────┬────────────┐
│ Metric                 │ Value   │ Percentile │
├────────────────────────┼─────────┼────────────┤
│ Form Index             │ 95%     │ 99th       │
│ Big Match Rating       │ +1.92   │ 85th       │
│ Tournament Success     │ 82.6    │ 95th       │
└────────────────────────┴─────────┴────────────┘

Recent Results: W-W-W-L-W-W-W-W-W-W (9-1 in last 10)
```

**API:** GET /players/{name}/metrics

---

#### **F. Career Achievements**
```
🏆 GRAND SLAMS (5):
  2022 US Open
  2024 French Open, Wimbledon
  2025 French Open, US Open

🥇 MASTERS 1000 (X wins):
  List of all Masters wins...

📊 CAREER MILESTONES:
  • First top 10 win: vs XXX (date)
  • First Grand Slam: US Open 2022
  • Youngest to reach 3,500 ELO: Yes
  • Weeks at #1: XX weeks
```

**API:** 
- GET /players/{name}/achievements
- GET /players/{name}/grand-slams

---

#### **G. Head-to-Head Records**
```
VS TOP RIVALS:
┌─────────────────────┬─────┬────────────────┐
│ Opponent            │ W-L │ Last Meeting   │
├─────────────────────┼─────┼────────────────┤
│ Novak Djokovic      │ 3-5 │ L (Oct 2024)   │
│ Jannik Sinner       │ 4-4 │ W (Sep 2024)   │
│ Daniil Medvedev     │ 5-2 │ W (Aug 2024)   │
└─────────────────────┴─────┴────────────────┘
```

**API:** GET /players/{name}/head-to-head

---

### **3. PLAYER COMPARISON PAGE** ⚖️

**Purpose:** Side-by-side comparison of 2-5 players

**URL:** `/compare?players=Alcaraz,Sinner,Djokovic`

**Sections:**

#### **A. Rating Comparison Table**
```
┌─────────────────┬──────────┬────────────┬──────────┐
│ Metric          │ Alcaraz  │ Sinner     │ Djokovic │
├─────────────────┼──────────┼────────────┼──────────┤
│ Peak ELO        │ 3,529    │ 3,355      │ 3,419    │
│ Current ELO     │ 3,198    │ 3,379      │ 3,104    │
│ Grand Slams     │ 5        │ 4          │ 24       │
│ Career Matches  │ 1,584    │ 2,034      │ 7,061    │
│ Current Form    │ 95%      │ 90%        │ 85%      │
│ Tournament Succ │ 82.6     │ 73.4       │ 57.9     │
└─────────────────┴──────────┴────────────┴──────────┘
```

**API:** GET /compare?players=Alcaraz,Sinner,Djokovic

---

#### **B. Career Trajectory Overlay**
```
Multi-line chart:
- Same X-axis (match number or age)
- All players' ELO curves overlaid
- Different colors per player
- Shows "at age 22, who was better?"
```

**API:** GET /compare/trajectories?players=...&align_by=age

---

#### **C. Head-to-Head Record**
```
If 2 players selected:
  Alcaraz vs Sinner: 4-4 (even!)
  
  Last 5 meetings:
  • 2024 Beijing: Alcaraz won
  • 2024 Roland Garros: Sinner won
  ...
```

**API:** GET /matchups/{player1}/{player2}

---

### **4. RANKINGS PAGE** 📊

**Purpose:** Browse all-time and current rankings across different metrics

**URL:** `/rankings`

**Tabs:**

#### **A. Current Rankings**
```
As of: October 18, 2025

┌────┬────────────────────┬────────┬────────┬──────────┬────────┐
│ #  │ Player             │ ELO    │ TSR    │ Glicko-2 │ Form%  │
├────┼────────────────────┼────────┼────────┼──────────┼────────┤
│ 1  │ Jannik Sinner      │ 3,379  │ 3,379  │ 3,372    │ 90%    │
│ 2  │ Carlos Alcaraz     │ 3,198  │ 3,198  │ 3,006    │ 95%    │
...

Filters:
☑ Active only
☐ Include retired
☐ Minimum 100 matches
```

**API:** GET /rankings/current?active=true&system=elo

---

#### **B. All-Time Peak Rankings**
```
HIGHEST PEAK ELO - ALL TIME

┌────┬────────────────────┬──────────┬──────────┬──────────────┐
│ #  │ Player             │ Peak ELO │ When     │ Career Span  │
├────┼────────────────────┼──────────┼──────────┼──────────────┤
│ 1  │ Novak Djokovic     │ 3,419    │ Jun 2016 │ 2003-2025    │
│ 2  │ Jannik Sinner      │ 3,355    │ Oct 2024 │ 2018-present │
│ 3  │ Rafael Nadal       │ 3,316    │ May 2014 │ 2001-2024    │
...
```

**API:** GET /rankings/all-time?metric=peak_elo

---

#### **C. Surface Rankings**
```
Tabs: Clay | Grass | Hard

CLAY KINGS - PEAK ELO
1. Rafael Nadal: 3,500+
2. Novak Djokovic: 3,300
...
```

**API:** GET /rankings/surface/{surface}

---

#### **D. Era Rankings**
```
Select Era:
☐ Big 3 Prime (2010-2016)
☐ Big 3 Late (2017-2022)
☑ NextGen (2023-2025)

NEXTGEN ERA RANKINGS:
1. Jannik Sinner: 3,355 (+225 vs peers)
2. Carlos Alcaraz: 3,274 (+145 vs peers)
...
```

**API:** GET /rankings/era/{era_name}

---

### **5. ANALYSIS HUB** 🔬

**Purpose:** Interesting insights and analysis tools

#### **A. Era Comparison Tool**
```
Compare players at same career stage:

Select players:
☑ Novak Djokovic
☑ Carlos Alcaraz

Align by:
○ Match number
○ Age
○ Years on tour

[Chart showing both players aligned]
```

**API:** GET /analysis/era-comparison?players=...&align=age

---

#### **B. GOAT Debate**
```
THE GOAT RACE - BY THE NUMBERS

┌──────────────────┬──────────┬────────┬──────────┐
│ Metric           │ Djokovic │ Nadal  │ Federer  │
├──────────────────┼──────────┼────────┼──────────┤
│ Grand Slams      │ 24 🥇    │ 22     │ 20       │
│ Peak ELO         │ 3,419 🥇 │ 3,316  │ 3,264    │
│ Weeks at #1      │ 428 🥇   │ 209    │ 310      │
│ Masters 1000     │ XX 🥇    │ XX     │ XX       │
│ Era Dominance    │ +252 🥇  │ +149   │ +97      │
└──────────────────┴──────────┴────────┴──────────┘

🏆 Statistical GOAT: Novak Djokovic (5/5 categories)
```

**API:** GET /analysis/goat-debate

---

#### **C. NextGen Tracker**
```
WHO'S THE NEXT GOAT?

Alcaraz vs Sinner - On Pace Comparison:

At Age 22:
  Alcaraz: 5 Grand Slams ⭐
  Nadal at 22: 5 Grand Slams (same!)
  Djokovic at 22: 1 Grand Slam
  
At Age 23:
  Sinner: 4 Grand Slams ⭐
  Federer at 23: 3 Grand Slams
  Djokovic at 23: 1 Grand Slam

Projection: Both on GOAT trajectory! 🚀
```

**API:** GET /analysis/nextgen-tracker

---

#### **D. Upset Tracker**
```
BIGGEST UPSETS (Last 30 days):

Player X (ELO 2,400) beat Player Y (ELO 3,100)
ELO Difference: 700 points
Probability: 1.2%
Match: Paris Masters R32

[List of recent upsets sorted by probability]
```

**API:** GET /analysis/upsets?days=30

---

### **6. SEARCH PAGE** 🔍

**Purpose:** Find any player, match, or statistic

**Features:**
```
Search: [____________] 🔍

Filters:
☐ Active players only
☐ Grand Slam winners only
☐ Peak ELO > 3000
☐ Specific surface
☐ Specific era (2020-2025)

Results:
✓ Players (Carlos Alcaraz, ...)
✓ Matches (Wimbledon 2023 Final: Alcaraz vs Djokovic)
✓ Tournaments (All Wimbledons)
```

**API:** 
- GET /search?q=alcaraz
- GET /players/search?name=alc&active=true
- GET /matches/search?tournament=wimbledon&year=2023

---

### **7. HISTORICAL EXPLORER** 📜

**Purpose:** Browse tennis history by year/era

**Navigation:**
```
Select Year: [2023 ▼]

2023 SEASON OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Grand Slam Winners:
  • Australian Open: Djokovic
  • French Open: Djokovic
  • Wimbledon: Alcaraz 🏆
  • US Open: Djokovic

Year-End #1: Djokovic
Breakout Player: Jannik Sinner
Biggest Mover: +300 ELO gain

[Timeline visualization of 2023]
```

**API:** 
- GET /history/year/{year}
- GET /history/grand-slams?year=2023

---

### **8. MATCH PREDICTOR** 🎯

**Purpose:** Predict outcomes of hypothetical matchups

**Interface:**
```
MATCH PREDICTOR

Player 1: [Carlos Alcaraz ▼]
Player 2: [Jannik Sinner ▼]
Surface:  [Hard ▼]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREDICTION:

Win Probability:
  Alcaraz: 48% ████████░░
  Sinner:  52% ██████████

Based on:
  • Hard court ELO diff: Sinner +150
  • Current form: Alcaraz 95%, Sinner 90%
  • Big match: Alcaraz +1.92, Sinner +1.24
  • H2H record: 4-4 (even)

Expected Score: 2-1 or 1-2 (close match)
```

**API:** GET /predict?player1=Alcaraz&player2=Sinner&surface=hard

---

### **9. LEADERBOARDS** 🏆

**Purpose:** Top X in various categories

**Categories:**

#### **A. Peak Performance**
```
HIGHEST SINGLE-SEASON ELO
1. Djokovic 2015: 3,419
2. Nadal 2013: 3,316
...

MOST DOMINANT SEASON (ERA-ADJUSTED)
1. Djokovic 2015: +252 over peers
2. Sinner 2024: +225 over peers
...
```

---

#### **B. Longevity**
```
MOST WEEKS AT #1
MOST CAREER MATCHES
LONGEST CAREERS
MOST GRAND SLAM FINALS
```

---

#### **C. Specialty Rankings**
```
BIGGEST GIANT KILLERS (Big Match Rating)
1. Jack Draper: +7.45
2. Arthur Fils: +8.02
...

MOST CONSISTENT (Lowest TSR Uncertainty)
1. Roger Federer: ±120.9
2. Novak Djokovic: ±123.0
...

HOTTEST FORM (Last 30 days)
1. Player X: 10-0, 100% form
...
```

**API:** 
- GET /leaderboards/peak-elo
- GET /leaderboards/longevity
- GET /leaderboards/big-match-rating

---

### **10. TOURNAMENT VIEW** 🎾

**Purpose:** See all results for a specific tournament

**URL:** `/tournament/wimbledon/2023`

**Layout:**
```
WIMBLEDON 2023
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Champion: Carlos Alcaraz
Runner-up: Novak Djokovic
Score: 1-6, 7-6(6), 6-1, 3-6, 6-4

📊 Tournament Stats:
  • Matches: 127
  • Upsets: 12
  • Avg ELO of semifinalists: 3,200

🏆 Draw (Interactive bracket):
  [Visual tournament bracket]

📈 ELO Changes:
  • Alcaraz: +157 (2,960 → 3,317)
  • Djokovic: -89 (3,405 → 3,316)
```

**API:** 
- GET /tournaments/{name}/{year}
- GET /tournaments/{name}/{year}/matches

---

### **11. STATISTICS & RECORDS** 📈

**Purpose:** Interesting stats and records

**Sections:**

```
ALL-TIME RECORDS:

Highest Peak ELO:
  Novak Djokovic - 3,419 (June 15, 2016)

Most Dominant Season:
  Djokovic 2015 - +252 over era peers

Fastest Rise:
  Carlos Alcaraz - 1,500 to 3,500 in 420 matches

Most Improved (Last Year):
  Jannik Sinner - +300 ELO gain

Biggest Upset (By ELO):
  Player X (2,100) def. Player Y (3,200) - 1,100 ELO gap
  
Active Streaks:
  • Sinner: 15-match win streak 🔥
  • Player X: 8-match losing streak 😰
```

**API:**
- GET /stats/records/all-time
- GET /stats/records/active-streaks
- GET /stats/biggest-upsets?days=365

---

### **12. ABOUT / METHODOLOGY** ℹ️

**Purpose:** Explain how everything works

**Sections:**
```
• How ELO Works
• What is TSR?
• Glicko-2 Explained
• How We Calculate Metrics
• Era Comparison Methodology
• Data Sources
• FAQ
```

**Static pages** (no API needed - use docs/)

---

## 🎨 Design Mockup Priorities

### **Must-Have Features:**
1. ✅ Current top 10 rankings
2. ✅ Player profile with career chart
3. ✅ Player comparison tool
4. ✅ Search functionality
5. ✅ Mobile-responsive design

### **Nice-to-Have:**
- Historical explorer
- Match predictor
- Leaderboards
- Tournament bracket view
- Advanced filters

### **Future Features:**
- User accounts (save favorite players)
- Notifications (player updates)
- Custom dashboards
- Data export
- API key management

---

## 🔌 API Endpoints Needed (Summary)

### **Core Endpoints:**
```
/players
  GET /players/list
  GET /players/{name}/summary
  GET /players/{name}/trajectory
  GET /players/{name}/ratings
  GET /players/{name}/metrics
  GET /players/{name}/achievements
  GET /players/{name}/head-to-head
  
/rankings
  GET /rankings/current
  GET /rankings/all-time
  GET /rankings/surface/{surface}
  GET /rankings/era/{era}
  
/compare
  GET /compare?players=A,B,C
  GET /compare/trajectories
  
/search
  GET /search?q={query}
  
/analysis
  GET /analysis/goat-debate
  GET /analysis/upsets
  GET /analysis/records
  
/tournaments
  GET /tournaments/{name}/{year}
  GET /tournaments/list
```

**Estimated:** ~20-25 endpoints for full app

---

## 🎯 MVP (Minimum Viable Product)

**For Phase 3A - Build these first (4-6 hours):**

1. ✅ **Current rankings** (top 100)
2. ✅ **Player profile** (summary + trajectory)
3. ✅ **Player comparison** (2-player side-by-side)
4. ✅ **Search players**
5. ✅ **Swagger docs** (auto-generated)

**This gives you:**
- Working API
- Testable endpoints
- Documentation
- Foundation for frontend

Then expand with more endpoints as needed!

---

## 💡 Technology Stack Suggestion

### **Backend (API):**
- **FastAPI** - Modern, fast, auto-docs
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **PostgreSQL** - You already have this
- **Redis** (optional) - Caching for speed

### **Frontend (Later):**
- **React** - If you want full control
- **Streamlit** - If you want fast MVP
- **Next.js** - If you want SEO + SSR

### **Deployment:**
- **Railway** / **Render** - Easy deployment
- **Vercel** - For frontend
- **Docker** - Containerization

---

## 📋 Next Steps

**If you want to proceed with API:**

1. I'll create FastAPI project structure
2. Build first 5 core endpoints
3. Test with Swagger UI
4. Deploy to Railway/Render
5. Build simple frontend

**Estimated for MVP:** 4-6 hours

---

**Does this page plan look good?** Any pages you want to add/remove/change? Or shall we start building the API based on this plan?
