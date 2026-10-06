"""
Main FastAPI application for Professional Attendance Monitoring System.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.database import init_database, get_db
from app.api.routes import router

# Initialize database
init_database()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional Attendance Monitoring System with Face Recognition",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers first
app.include_router(router, prefix="/api", tags=["Attendance Monitoring"])

# Define frontend build directory path
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

# Mount static assets if directory exists
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Serve requested file if it exists, otherwise fallback to index.html
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
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
                "Advanced reporting and analytics"
            ]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
