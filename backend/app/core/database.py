"""
Database configuration and session management for MySQL.
"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

db_url = make_url(settings.DATABASE_URL)

# Create database engine (MySQL or SQLite)
engine_kwargs = dict(
    pool_pre_ping=True,   # Verify connections are valid
    pool_recycle=3600,    # Recycle connections every hour
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

if db_url.drivername.startswith("sqlite"):
    # SQLite doesn't support the same pooling options as MySQL and needs this for FastAPI threads.
    engine_kwargs.pop("pool_recycle", None)
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """
    Initialize database with all tables.
    """
    try:
        from backend.app.models import attendance, user  # noqa: F401
        from backend.app.models.user import AdminUser
        from backend.app.core.security import hash_password

        db_name = db_url.database
        if not db_name and not db_url.drivername.startswith("sqlite"):
            raise ValueError("DATABASE_URL is missing a database name")

        # Create database if it doesn't exist (MySQL only)
        if db_url.drivername.startswith("mysql"):
            import pymysql
            # Connect without selecting a database to create it if missing
            conn = pymysql.connect(
                host=db_url.host or "localhost",
                user=db_url.username or "root",
                password=db_url.password or "",
                port=db_url.port or 3306,
                charset="utf8mb4",
                autocommit=True,
            )
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
            finally:
                conn.close()

        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Bootstrap admin user if missing
        db = SessionLocal()
        try:
            existing = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
            if not existing:
                admin = AdminUser(
                    username=settings.ADMIN_USERNAME,
                    password_hash=hash_password(settings.ADMIN_PASSWORD),
                )
                db.add(admin)
                db.commit()
                logger.info("✅ Default admin user created")
        finally:
            db.close()
        logger.info("✅ Database initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
