import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship

from database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    overall_score = Column(Float, nullable=False)
    skills_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    keyword_match_score = Column(Float, nullable=False)
    matched_skills = Column(JSON, nullable=True)  # Store as JSON array
    missing_skills = Column(JSON, nullable=True)  # Store as JSON array
    matched_education = Column(JSON, nullable=True)  # Store as JSON array
    matched_experience_keywords = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("JobDescription", back_populates="matches")