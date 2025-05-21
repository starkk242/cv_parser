from typing import List
from functools import lru_cache
from pydantic import BaseSettings, Field
from pathlib import Path
from dotenv import load_dotenv
import os

# Explicitly load the .env file from project root
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "CV Parser & Job Matching API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for parsing CV/Resume documents and matching them against job descriptions"
    
    # Directory settings
    UPLOAD_DIR: str = "data/uploads"
    PARSED_DIR: str = "data/parsed"
    JD_DIR: str = "data/job_descriptions"
    
    # File settings
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    CLEANUP_FILES: bool = True

    # API Keys
    HUGGING_FACE_TOKEN: str = Field(default=os.environ.get("hugging_face_token"), env="hugging_face_token")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings with caching."""
    return Settings()