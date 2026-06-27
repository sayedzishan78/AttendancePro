"""
Configuration settings for the application.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Multiface Recognition API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:Mirzak%40123@localhost:3306/attendance_system"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "change-me-please"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12
    JWT_ALGORITHM: str = "HS256"
    
    # Admin bootstrap
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    
    # Face Recognition
    RECOGNITION_THRESHOLD: float = 0.4
    DETECTION_SIZE: int = 640
    LIVE_RECOGNITION_STRIDE: int = 2
    LIVE_RECOGNITION_WIDTH: int = 480
    
    # File Storage
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE_MB: int = 10
    
    # Base directory
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    @property
    def output_path(self) -> Path:
        """Get the output directory path."""
        path = self.BASE_DIR / self.OUTPUT_DIR
        path.mkdir(exist_ok=True)
        return path


settings = Settings()
