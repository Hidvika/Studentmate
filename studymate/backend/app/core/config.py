from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_env: str = Field(default="dev", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # Database
    postgres_url: str = Field(default="postgresql+asyncpg://test:test@localhost:5432/test", alias="POSTGRES_URL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    
    # S3/MinIO
    s3_endpoint: str = Field(default="http://localhost:9000", alias="S3_ENDPOINT")
    s3_bucket: str = Field(default="test", alias="S3_BUCKET")
    s3_access_key: str = Field(default="test", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="test", alias="S3_SECRET_KEY")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    
    # Embeddings
    embeddings_backend: str = Field(default="sentence-transformers", alias="EMBEDDINGS_BACKEND")
    embeddings_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBEDDINGS_MODEL")
    
    # WatsonX
    watsonx_api_key: Optional[str] = Field(default=None, alias="WATSONX_API_KEY")
    watsonx_project_id: Optional[str] = Field(default=None, alias="WATSONX_PROJECT_ID")
    watsonx_model_id: str = Field(default="granite-13b-instruct-v2", alias="WATSONX_MODEL_ID")
    watsonx_url: str = Field(default="https://us-south.ml.cloud.ibm.com", alias="WATSONX_URL")
    
    # Chunking
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=100, alias="CHUNK_OVERLAP")
    
    # Search
    default_top_k: int = Field(default=5, alias="DEFAULT_TOP_K")
    max_top_k: int = Field(default=20, alias="MAX_TOP_K")
    
    # File upload
    max_file_size_mb: int = Field(default=50, alias="MAX_FILE_SIZE_MB")
    allowed_extensions: list[str] = Field(default=[".pdf"], alias="ALLOWED_EXTENSIONS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
