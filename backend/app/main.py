"""
Main FastAPI application for Professional Attendance Monitoring System.
"""
import os
import sys
import logging
from contextlib import asynccontextmanager

# Ensure project root directory is in Python path for absolute imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import init_database
from backend.app.api.routes import router

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs AFTER the server starts listening on the port.
    If the database is unreachable, the app still starts (no 504 timeout)
    and the error is visible in the Log stream.
    """
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    yield


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional Attendance Monitoring System with Face Recognition",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Lightweight health check (does not touch DB or ML models)
@app.get("/healthz", include_in_schema=False)
async def healthz():
    return {"status": "ok"}


# Include API routers first
app.include_router(router, prefix="/api", tags=["Attendance Monitoring"])

# Define frontend build directory path
frontend_dist = os.path.abspath(os.path.join(PROJECT_ROOT, "frontend", "dist"))
assets_dir = os.path.join(frontend_dist, "assets")

if os.path.isdir(frontend_dist):
    # Mount static assets only if the assets folder exists
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        # Unknown API paths should return a proper 404, not index.html
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Serve requested file if it exists, otherwise fallback to index.html
        file_path = os.path.abspath(os.path.join(frontend_dist, full_path))
        # Prevent path traversal outside frontend_dist
        if file_path.startswith(frontend_dist) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root():
        """Fallback root endpoint when frontend build is not found."""
        return {
            "message": "Welcome to Professional Attendance Monitoring System",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/api/health/",
            "features": [
                "Real-time face recognition",
                "Professional attendance tracking",
                "MySQL database integration",
                "Advanced reporting and analytics",
            ],
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
