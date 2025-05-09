from pydantic import BaseSettings
import os
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    # API settings
    API_TITLE: str = "CV Parser & Job Matching API"
    API_DESCRIPTION: str = "API for parsing CV/Resume documents and matching them against job descriptions"
    API_VERSION: str = "1.0.0"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./resumes.db"
    
    # File storage settings
    UPLOAD_DIR: str = "uploads"
    PARSED_DIR: str = "parsed"
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    CLEANUP_FILES: bool = True
    
    # NLP model
    NLP_MODEL: str = "en_core_web_sm"
    
    # Match scoring weights
    WEIGHT_REQUIRED_SKILLS: float = 0.7
    WEIGHT_PREFERRED_SKILLS: float = 0.3
    WEIGHT_SKILLS_TOTAL: float = 0.4
    WEIGHT_EDUCATION: float = 0.2
    WEIGHT_EXPERIENCE: float = 0.2
    WEIGHT_KEYWORD_MATCH: float = 0.2

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create instance of settings
settings = Settings()

# Ensure directories exist
for directory in [settings.UPLOAD_DIR, settings.PARSED_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)