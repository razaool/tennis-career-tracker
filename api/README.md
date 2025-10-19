# 🎾 Tennis Career Tracker API

FastAPI backend for the Tennis Career Tracker application.

## 📁 Project Structure

```
api/
├── __init__.py
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── database.py          # Database connection utilities
├── models/              # Pydantic models for validation
│   ├── player.py
│   ├── rating.py
│   └── ranking.py
├── routes/              # API endpoint handlers
│   ├── players.py       # ✅ Implemented
│   ├── rankings.py      # 🚧 Coming next
│   ├── compare.py
│   ├── dashboard.py
│   ├── analysis.py
│   └── predict.py
├── services/            # Business logic
└── utils/               # Helper functions
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

### 2. Set Environment Variables (Optional)

Create a `.env` file in project root:

```env
# Database (defaults work if you followed setup)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tennis_tracker
DB_USER=razaool
DB_PASSWORD=

# Redis (optional, for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. Run the API

```bash
# From project root
cd tennis-career-tracker

# Run with uvicorn
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or use the built-in runner
python -m api.main
```

### 4. Access the API

- **API Root**: http://localhost:8000/
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Available Endpoints

### ✅ Implemented

#### **GET /**
Welcome message and API info

#### **GET /health**
Health check with database status and stats

#### **GET /api/players**
List all players (paginated)
- Query params: `limit`, `offset`, `active`, `min_elo`, `sort_by`

#### **GET /api/players/{player_name}**
Get complete player profile
- Returns ratings, career stats, achievements, metrics

### 🚧 Coming Next

#### **GET /api/players/{player_name}/trajectory**
Career trajectory data for charts

#### **GET /api/rankings/current**
Current top 100 rankings

#### **GET /api/compare**
Compare multiple players

#### **GET /api/predict/match**
Predict match outcome

## 📝 Example Requests

### Get Player List
```bash
curl "http://localhost:8000/api/players?limit=10&active=true&sort_by=elo"
```

### Get Specific Player
```bash
curl "http://localhost:8000/api/players/Carlos%20Alcaraz"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## 🔧 Development

### Add New Endpoint

1. **Create route in `routes/` directory**
```python
# routes/new_feature.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

2. **Import and include in `main.py`**
```python
from .routes import new_feature
app.include_router(new_feature.router, prefix="/api/feature", tags=["Feature"])
```

### Run Tests
```bash
pytest tests/
```

## 📦 Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **psycopg2**: PostgreSQL adapter
- **SQLAlchemy**: SQL toolkit (optional)

## 🎯 Next Steps

1. ✅ Basic structure complete
2. ✅ Players endpoint working
3. 🚧 Add rankings endpoint
4. 🚧 Add comparison endpoint
5. 🚧 Add prediction endpoint
6. 🚧 Add analysis endpoints
7. 🚧 Add caching with Redis
8. 🚧 Add rate limiting
9. 🚧 Add authentication (if needed)
10. 🚧 Deploy to production

## 📚 Documentation

- Full API specification: `docs/technical/API_ENDPOINTS_DETAILED.md`
- Roadmap: `docs/technical/PHASE3_ROADMAP.md`

