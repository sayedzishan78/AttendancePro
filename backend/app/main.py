"""
Main FastAPI application for Professional Attendance Monitoring System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Include routers
app.include_router(router, prefix="/api", tags=["Attendance Monitoring"])


@app.get("/")
async def root():
    """Root endpoint."""
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
