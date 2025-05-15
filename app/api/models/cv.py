from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class Experience(BaseModel):
    """Model for work experience in a resume."""
    description: str


class Education(BaseModel):
    """Model for education in a resume."""
    description: str


class ParsedResume(BaseModel):
    """Model for parsed resume data."""
    file_name: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[str] = []
    skills: List[str] = []
    experience: List[Dict[str, str]] = []
    parsed_date: str = Field(default_factory=lambda: datetime.now().isoformat())