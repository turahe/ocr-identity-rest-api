import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration for PostgreSQL"""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    username: str = Field(default="postgres")
    password: str = Field(default="")
    database: str = Field(default="ocr_identity_db")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    echo: bool = Field(default=False)
    
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
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: Optional[str] = Field(default=None)
    db: int = Field(default=0)
    max_connections: int = Field(default=10)
    decode_responses: bool = Field(default=True)
    
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
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)
    region_name: str = Field(default="us-east-1")
    bucket_name: Optional[str] = Field(default=None)
    endpoint_url: Optional[str] = Field(default=None)
    use_ssl: bool = Field(default=True)
    verify_ssl: bool = Field(default=True)
    
    class Config:
        env_prefix = "S3_"
        case_sensitive = False


class EmailConfig(BaseSettings):
    """Email configuration"""
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    use_tls: bool = Field(default=True)
    use_ssl: bool = Field(default=False)
    from_email: Optional[str] = Field(default=None)
    from_name: str = Field(default="OCR Identity API")
    
    @field_validator('from_email', mode='after')
    @classmethod
    def validate_from_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('from_email must be a valid email address')
        return v
    
    class Config:
        env_prefix = "EMAIL_"
        case_sensitive = False


class AppConfig(BaseSettings):
    """Main application configuration"""
    # App settings
    app_name: str = Field(default="OCR Identity REST API")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")
    
    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)
    
    # Security
    secret_key: Optional[str] = Field(default=None)
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # File upload settings
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    allowed_file_types: list = Field(default=["image/jpeg", "image/png", "image/jpg"])
    
    # Auth method
    auth_method: str = Field(default="jwt")
    
    # Database
    database: DatabaseConfig = DatabaseConfig()
    
    # Redis
    redis: RedisConfig = RedisConfig()
    
    # S3
    s3: S3Config = S3Config()
    
    # Email
    email: EmailConfig = EmailConfig()
    
    # API Key Auth
    api_key: str = Field(default="")
    api_key_name: str = Field(default="X-API-Key")
    
    @field_validator('environment', mode='after')
    @classmethod
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
