"""
Tennis Career Tracker API - Main Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
import time

from config import settings
from database import Database

# Import routes
from routes import players, rankings, dashboard, predict, h2h
# from .routes import compare, analysis


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url=None,  # Disable default docs to use custom
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}s"
    return response


# Custom dark mode docs
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with dark mode"""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{app.title} - API Docs</title>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        <style>
            /* Dark Mode CSS */
            body {{
                background-color: #1a1a1a;
                margin: 0;
                padding: 0;
            }}
            
            .swagger-ui {{
                filter: invert(88%) hue-rotate(180deg);
            }}
            
            .swagger-ui .scheme-container {{
                background: #252525;
                box-shadow: 0 1px 2px 0 rgba(255,255,255,.15);
            }}
            
            .swagger-ui .opblock .opblock-summary-description,
            .swagger-ui .opblock .opblock-summary-operation-id,
            .swagger-ui .opblock .opblock-summary-path,
            .swagger-ui .opblock .opblock-summary-path__deprecated {{
                filter: invert(100%) hue-rotate(180deg);
            }}
            
            .swagger-ui .info .title small pre,
            .swagger-ui .info .title small,
            .swagger-ui .info .title {{
                filter: invert(100%) hue-rotate(180deg);
            }}
            
            .swagger-ui img {{
                filter: invert(100%) hue-rotate(180deg);
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {{
                window.ui = SwaggerUIBundle({{
                    url: '{app.openapi_url}',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    syntaxHighlight: {{
                        theme: "monokai"
                    }}
                }});
            }};
        </script>
    </body>
    </html>
    """)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API Root - Welcome message"""
    return {
        "message": "🎾 Tennis Career Tracker API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "status": "running"
    }


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint
    
    Returns API status and database connectivity
    """
    db_connected = Database.test_connection()
    
    # Get basic stats
    if db_connected:
        try:
            stats = Database.execute_one("""
                SELECT 
                    (SELECT COUNT(*) FROM players) as total_players,
                    (SELECT COUNT(*) FROM matches) as total_matches,
                    (SELECT MAX(date) FROM matches) as last_match_date
            """)
        except Exception as e:
            stats = None
    else:
        stats = None
    
    return {
        "status": "healthy" if db_connected else "unhealthy",
        "database": "connected" if db_connected else "disconnected",
        "api_version": settings.API_VERSION,
        "stats": {
            "total_players": stats.get("total_players") if stats else None,
            "total_matches": stats.get("total_matches") if stats else None,
            "last_data_update": str(stats.get("last_match_date")) if stats else None,
        } if stats else None
    }


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(players.router, prefix="/api/players", tags=["Players"])
app.include_router(rankings.router, prefix="/api/rankings", tags=["Rankings"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(predict.router, prefix="/api/predict", tags=["Prediction"])
app.include_router(h2h.router, prefix="/api/h2h", tags=["Head-to-Head"])
# app.include_router(compare.router, prefix="/api/compare", tags=["Comparison"])
# app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on API startup"""
    print("🚀 Starting Tennis Career Tracker API...")
    print(f"📊 Database: {settings.DB_NAME}")
    print(f"🔗 Docs available at: http://localhost:8000/docs")
    
    # Test database connection
    if Database.test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on API shutdown"""
    print("👋 Shutting down Tennis Career Tracker API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

