import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "forks-and-knife-secret-key-change-in-prod-2026")
    # Compute absolute SQLite URI
    db_env_url = os.environ.get("DATABASE_URL")
    if not db_env_url or "sqlite:///" in db_env_url:
        db_file = (BASE_DIR / "instance" / "restaurant.db").resolve()
        
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file.as_posix()}"
    else:
        SQLALCHEMY_DATABASE_URI = db_env_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit

    # Restaurant defaults
    DEFAULT_CURRENCY = "₹"
    DEFAULT_DELIVERY_FEE = 40.0
    DEFAULT_FREE_DELIVERY_MIN = 500.0


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
