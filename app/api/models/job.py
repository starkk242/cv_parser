from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class JobDescription(BaseModel):
    """Model for job description data."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: Optional[str] = None
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education_requirements: List[str] = []
    experience_requirements: List[str] = []
    created_date: str = Field(default_factory=lambda: datetime.now().isoformat())