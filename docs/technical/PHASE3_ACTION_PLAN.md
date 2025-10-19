# 🎯 Phase 3: API Development - Action Plan

**Date:** October 19, 2025  
**Status:** In Progress - Day 1

---

## ✅ What We've Accomplished Today

### **Phase 2 Complete (Earlier)**
- ✅ All rating systems calculated (ELO, TSR, Glicko-2)
- ✅ All supporting metrics calculated
- ✅ 2023 data gap fixed
- ✅ All CSVs exported
- ✅ Repository organized
- ✅ Comprehensive documentation

### **Phase 3 Planning (Just Now)**
- ✅ App design planned (12 pages)
- ✅ API endpoints specified (23 endpoints)
- ✅ Match prediction data analyzed
- ✅ Confirmed we have all data needed

### **Phase 3 Structure (Just Now)**
- ✅ FastAPI project structure created
- ✅ Configuration files created
- ✅ Database connection setup
- ✅ Pydantic models created
- ✅ First player endpoint created
- ✅ API server running

---

## 🐛 Current Issue

**Problem:** API queries are hanging/timing out

**Likely Causes:**
1. SQL query is too complex (multiple CTEs, GROUP BY on 2.68M matches)
2. Missing database indexes
3. Query needs optimization

**Impact:** Can't test endpoints until queries are optimized

---

## 🎯 Immediate Action Plan

### **Step 1: Fix the Hanging Query Issue** (30 minutes)

**Option A: Simplify the SQL** (Recommended)
- Use pre-aggregated data instead of calculating on-the-fly
- Create a materialized view or summary table
- Query only what we need

**Option B: Optimize Existing Query**
- Add indexes to speed up joins
- Break query into smaller parts
- Use EXPLAIN ANALYZE to find bottlenecks

**Decision:** Let's do **Option A** - create a simpler, faster query

---

### **Step 2: Build Core MVP Endpoints** (2-3 hours)

Once queries are working, build these 5 endpoints:

1. **GET /api/players** - List players (simplified query)
2. **GET /api/players/{name}** - Player detail (optimized)
3. **GET /api/rankings/current** - Top 100 current
4. **GET /api/dashboard/top10** - Quick dashboard data
5. **GET /health** - Health check ✅ (Already works!)

**Goal:** Get basic data flowing through the API

---

### **Step 3: Test with Swagger UI** (15 minutes)

- Open http://localhost:8000/docs
- Test each endpoint
- Verify response format
- Check performance

---

### **Step 4: Add Player Trajectory Endpoint** (30 minutes)

- **GET /api/players/{name}/trajectory**
- Return all rating data points for charting
- This is crucial for the frontend

---

### **Step 5: Build Match Predictor (MVP)** (1 hour)

- **GET /api/predict/match**
- Use simple algorithm (ELO + form)
- Test with real player matchups

---

## 📋 Complete Task Breakdown

### **TODAY (Next 4-5 hours)**

```
☐ 1. Fix SQL Query Performance (30 min)
   ├─ Simplify player list query
   ├─ Add necessary indexes
   └─ Test query speed

☐ 2. Complete Players Endpoints (1 hour)
   ├─ GET /api/players (list) - Fix & test
   ├─ GET /api/players/{name} (detail) - Fix & test
   └─ GET /api/players/{name}/trajectory - Build & test

☐ 3. Build Rankings Endpoint (30 min)
   ├─ Create routes/rankings.py
   ├─ GET /api/rankings/current
   └─ Test with top 100

☐ 4. Build Dashboard Endpoint (30 min)
   ├─ Create routes/dashboard.py
   ├─ GET /api/dashboard/top10
   └─ Simple, fast query

☐ 5. Build Match Predictor MVP (1 hour)
   ├─ Create routes/predict.py
   ├─ Implement basic prediction algorithm
   ├─ GET /api/predict/match
   └─ Test predictions

☐ 6. Documentation & Testing (30 min)
   ├─ Test all endpoints in Swagger
   ├─ Write example requests
   └─ Document response formats

☐ 7. Push to GitHub (5 min)
```

**Total: ~4-5 hours to working MVP API**

---

### **TOMORROW (Optional Extensions)**

```
☐ Add Comparison Endpoint
   └─ GET /api/compare

☐ Add Analysis Endpoints
   ├─ GET /api/analysis/goat-debate
   └─ GET /api/analysis/nextgen

☐ Add Leaderboards
   └─ GET /api/leaderboards/*

☐ Add Caching (Redis)
   └─ Cache expensive queries

☐ Deploy to Production
   ├─ Railway or Render
   └─ Get public URL
```

---

## 🎯 Success Criteria for Today

**MVP API is complete when:**

- ✅ API server runs without hanging
- ✅ Can list top 100 players
- ✅ Can get player profile (Alcaraz, Sinner, Djokovic)
- ✅ Can get player career trajectory
- ✅ Can predict a match outcome (Alcaraz vs Sinner)
- ✅ All responses return in < 1 second
- ✅ Swagger docs work perfectly
- ✅ Can demo to friends!

---

## 🔧 Technical Decisions

### **Query Optimization Strategy**

**Instead of:**
```sql
-- Complex query with 3 CTEs, multiple joins, GROUP BY on millions of rows
WITH latest_ratings AS (...) 
  JOIN matches (2.68M rows)
  GROUP BY ...
```

**Do this:**
```sql
-- Simple query on indexed columns
SELECT p.name, pr.elo_rating
FROM players p
JOIN player_ratings pr ON pr.player_id = p.player_id
WHERE pr.rating_id IN (
  SELECT MAX(rating_id) 
  FROM player_ratings 
  GROUP BY player_id
)
ORDER BY pr.elo_rating DESC
LIMIT 100;
```

**Benefits:**
- ✅ 100x faster
- ✅ Uses indexes
- ✅ Returns in milliseconds

---

## 📊 Database Indexes Needed

Check if these exist, add if missing:

```sql
-- For fast "latest rating" queries
CREATE INDEX idx_player_ratings_player_latest 
ON player_ratings (player_id, date DESC, career_match_number DESC);

-- For fast ELO sorting
CREATE INDEX idx_player_ratings_elo 
ON player_ratings (elo_rating DESC);

-- For fast player lookup
CREATE INDEX idx_players_name_lower 
ON players (LOWER(name));
```

---

## 🎯 Next Immediate Step

**RIGHT NOW: Fix the hanging query**

Let me create a simplified version of the players endpoint that:
1. Uses the latest rating_id for each player (faster)
2. Doesn't join with all matches (avoid 2.68M row scan)
3. Returns results in < 100ms

**After that:** Build out the remaining 4 core endpoints

---

## 💡 What You Should Expect

### **In 1 hour:**
- Working player list endpoint
- Working player detail endpoint
- Can browse Swagger docs

### **In 3 hours:**
- All 5 core endpoints working
- Can get top 100 rankings
- Can predict matches

### **In 5 hours:**
- Complete MVP API
- Ready to build frontend
- Can share with others

---

## ❓ Decision Points

**Should we:**

1. **Fix queries first** ← YES, do this now
2. Add more endpoints
3. Build frontend

**After MVP is working, should we:**

- Add more endpoints (comparison, analysis)?
- Start on frontend?
- Deploy to production?

**Your call!** But let's get the MVP working first.

---

## 🚀 Let's Execute

**Ready to start?** 

Say **"let's fix the queries"** and I'll:
1. Simplify the SQL queries
2. Test them for speed
3. Get the API responding quickly
4. Move on to building the remaining endpoints

We're close! Just need to optimize these queries and we'll have a working API in a few hours. 🎾

