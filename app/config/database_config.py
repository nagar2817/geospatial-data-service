import os
from datetime import timedelta
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class DatabaseConfig(BaseSettings):
    """Database configuration for geospatial data service."""
    
    host: str = os.getenv("DB_HOST", "localhost")
    port: str = os.getenv("DB_PORT", "5432")
    name: str = os.getenv("DB_NAME", "postgres")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "postgres")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # PostGIS specific settings
    enable_postgis: bool = True
    
    # Connection timeouts
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @property
    def sync_url(self) -> str:
        """Synchronous database URL for SQLAlchemy."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def async_url(self) -> str:
        """Asynchronous database URL for SQLAlchemy async operations."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_prefix = "DB_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

class RedisConfig(BaseSettings):
    """Redis configuration for caching and sessions."""
    
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "0"))
    password: str = os.getenv("REDIS_PASSWORD", "")
    
    # Cache settings
    default_ttl: int = 3600  # 1 hour
    max_connections: int = 10
    
    @property
    def url(self) -> str:
        """Redis connection URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "REDIS_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

class AmazonMQConfig(BaseSettings):
    """Amazon MQ RabbitMQ configuration for production."""
    
    host: str = os.getenv("RABBITMQ_HOST", "localhost")
    port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    user: str = os.getenv("RABBITMQ_USER", "admin")
    password: str = os.getenv("RABBITMQ_PASSWORD", "")
    vhost: str = os.getenv("RABBITMQ_VHOST", "/")
    
    # Connection settings
    heartbeat: int = 600
    blocked_connection_timeout: int = 300
    
    @property
    def url(self) -> str:
        """RabbitMQ connection URL for Amazon MQ."""
        return f"pyamqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"
    
    class Config:
        env_prefix = "RABBITMQ_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"