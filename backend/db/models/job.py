import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    required_skills = relationship("RequiredSkill", back_populates="job", cascade="all, delete-orphan")
    preferred_skills = relationship("PreferredSkill", back_populates="job", cascade="all, delete-orphan")
    education_requirements = relationship("EducationRequirement", back_populates="job", cascade="all, delete-orphan")
    experience_requirements = relationship("ExperienceRequirement", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")


class RequiredSkill(Base):
    __tablename__ = "required_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    job = relationship("JobDescription", back_populates="required_skills")


class PreferredSkill(Base):
    __tablename__ = "preferred_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    job = relationship("JobDescription", back_populates="preferred_skills")


class EducationRequirement(Base):
    __tablename__ = "education_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    description = Column(Text, nullable=False)
    
    job = relationship("JobDescription", back_populates="education_requirements")


class ExperienceRequirement(Base):
    __tablename__ = "experience_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    description = Column(Text, nullable=False)
    
    job = relationship("JobDescription", back_populates="experience_requirements")