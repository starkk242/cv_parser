import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    full_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    matches = relationship("MatchResult", back_populates="resume", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    resume = relationship("Resume", back_populates="skills")


class Education(Base):
    __tablename__ = "education"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=False)
    description = Column(Text, nullable=False)
    
    resume = relationship("Resume", back_populates="education")


class Experience(Base):
    __tablename__ = "experience"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=False)
    description = Column(Text, nullable=False)
    
    resume = relationship("Resume", back_populates="experience")