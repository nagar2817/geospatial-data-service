from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from config.database_config import DatabaseConfig, RedisConfig, AmazonMQConfig

load_dotenv()

class Settings(BaseSettings):
    """Main application settings."""
    
    app_name: str = "Geospatial Data Service"
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Configuration modules
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    amazon_mq: AmazonMQConfig = AmazonMQConfig()
    
    # Google Earth Engine
    gee_project_id: str = ""
    google_application_credentials: str = ""
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()