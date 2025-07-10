import os
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration for PostgreSQL"""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    username: str = Field(default="postgres", env="DB_USERNAME")
    password: str = Field(default="", env="DB_PASSWORD")
    database: str = Field(default="ocr_identity_db", env="DB_NAME")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    @property
    def database_url(self) -> str:
        """Generate database URL for asyncpg"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_database_url(self) -> str:
        """Generate async database URL for asyncpg"""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    class Config:
        env_prefix = "DB_"
        case_sensitive = False


class RedisConfig(BaseSettings):
    """Redis configuration"""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    decode_responses: bool = Field(default=True, env="REDIS_DECODE_RESPONSES")
    
    @property
    def redis_url(self) -> str:
        """Generate Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = "REDIS_"
        case_sensitive = False


class S3Config(BaseSettings):
    """AWS S3 configuration"""
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    region_name: str = Field(default="us-east-1", env="AWS_REGION")
    bucket_name: str = Field(..., env="S3_BUCKET_NAME")
    endpoint_url: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")
    use_ssl: bool = Field(default=True, env="S3_USE_SSL")
    verify_ssl: bool = Field(default=True, env="S3_VERIFY_SSL")
    
    class Config:
        env_prefix = "S3_"
        case_sensitive = False


class EmailConfig(BaseSettings):
    """Email configuration"""
    smtp_host: str = Field(default="smtp.gmail.com", env="EMAIL_SMTP_HOST")
    smtp_port: int = Field(default=587, env="EMAIL_SMTP_PORT")
    username: str = Field(..., env="EMAIL_USERNAME")
    password: str = Field(..., env="EMAIL_PASSWORD")
    use_tls: bool = Field(default=True, env="EMAIL_USE_TLS")
    use_ssl: bool = Field(default=False, env="EMAIL_USE_SSL")
    from_email: str = Field(..., env="EMAIL_FROM")
    from_name: str = Field(default="OCR Identity API", env="EMAIL_FROM_NAME")
    
    @validator('from_email')
    def validate_from_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('from_email must be a valid email address')
        return v
    
    class Config:
        env_prefix = "EMAIL_"
        case_sensitive = False


class AppConfig(BaseSettings):
    """Main application configuration"""
    # App settings
    app_name: str = Field(default="OCR Identity REST API", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # File upload settings
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: list = Field(default=["image/jpeg", "image/png", "image/jpg"], env="ALLOWED_FILE_TYPES")
    
    # Database
    database: DatabaseConfig = DatabaseConfig()
    
    # Redis
    redis: RedisConfig = RedisConfig()
    
    # S3
    s3: S3Config = S3Config()
    
    # Email
    email: EmailConfig = EmailConfig()
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f'environment must be one of {allowed}')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a global config instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the application configuration"""
    return config


def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return config.database


def get_redis_config() -> RedisConfig:
    """Get Redis configuration"""
    return config.redis


def get_s3_config() -> S3Config:
    """Get S3 configuration"""
    return config.s3


def get_email_config() -> EmailConfig:
    """Get email configuration"""
    return config.email
