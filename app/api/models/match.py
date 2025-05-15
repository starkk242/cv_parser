from pydantic import BaseModel
from typing import List, Dict


class MatchScore(BaseModel):
    """Model for resume-job match scoring."""
    resume_id: str
    resume_name: str
    job_id: str
    job_title: str
    overall_score: float
    skills_score: float
    education_score: float
    experience_score: float
    keyword_match_score: float
    matched_skills: List[str] = []
    matched_education: List[str] = []
    matched_experience_keywords: List[str] = []
    missing_skills: List[str] = []


class BatchMatchRequest(BaseModel):
    """Model for batch matching request."""
    job_ids: List[str]


class BatchMatchResult(BaseModel):
    """Model for batch matching result."""
    matches: Dict[str, List[MatchScore]]