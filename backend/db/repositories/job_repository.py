from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from db.models.job import (
    JobDescription, 
    RequiredSkill, 
    PreferredSkill, 
    EducationRequirement, 
    ExperienceRequirement
)


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job_data: Dict[str, Any]) -> JobDescription:
        """Create a new job description and related entities."""
        # Create job description
        job = JobDescription(
            title=job_data["title"],
            company=job_data.get("company"),
            description=job_data["description"]
        )
        self.db.add(job)
        self.db.flush()  # Flush to get the job ID

        # Create required skills
        if "required_skills" in job_data and isinstance(job_data["required_skills"], list):
            for skill_name in job_data["required_skills"]:
                skill = RequiredSkill(job_id=job.id, name=skill_name)
                self.db.add(skill)

        # Create preferred skills
        if "preferred_skills" in job_data and isinstance(job_data["preferred_skills"], list):
            for skill_name in job_data["preferred_skills"]:
                skill = PreferredSkill(job_id=job.id, name=skill_name)
                self.db.add(skill)

        # Create education requirements
        if "education_requirements" in job_data and isinstance(job_data["education_requirements"], list):
            for edu_desc in job_data["education_requirements"]:
                education = EducationRequirement(job_id=job.id, description=edu_desc)
                self.db.add(education)

        # Create experience requirements
        if "experience_requirements" in job_data and isinstance(job_data["experience_requirements"], list):
            for exp_desc in job_data["experience_requirements"]:
                experience = ExperienceRequirement(job_id=job.id, description=exp_desc)
                self.db.add(experience)

        self.db.commit()
        self.db.refresh(job)
        return job

    def get_all_jobs(self) -> List[JobDescription]:
        """Get all job descriptions."""
        return self.db.query(JobDescription).order_by(JobDescription.created_at.desc()).all()

    def get_job_by_id(self, job_id: str) -> Optional[JobDescription]:
        """Get a job description by ID."""
        return self.db.query(JobDescription).filter(JobDescription.id == job_id).first()

    def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Optional[JobDescription]:
        """Update a job description."""
        job = self.get_job_by_id(job_id)
        if not job:
            return None

        # Update basic fields
        if "title" in job_data:
            job.title = job_data["title"]
        if "company" in job_data:
            job.company = job_data["company"]
        if "description" in job_data:
            job.description = job_data["description"]
        
        # Handle related entities if provided
        # Required skills
        if "required_skills" in job_data:
            # Delete existing skills
            self.db.query(RequiredSkill).filter(RequiredSkill.job_id == job_id).delete()
            # Add new skills
            for skill_name in job_data["required_skills"]:
                skill = RequiredSkill(job_id=job.id, name=skill_name)
                self.db.add(skill)
        
        # Preferred skills
        if "preferred_skills" in job_data:
            # Delete existing skills
            self.db.query(PreferredSkill).filter(PreferredSkill.job_id == job_id).delete()
            # Add new skills
            for skill_name in job_data["preferred_skills"]:
                skill = PreferredSkill(job_id=job.id, name=skill_name)
                self.db.add(skill)
        
        # Education requirements
        if "education_requirements" in job_data:
            # Delete existing requirements
            self.db.query(EducationRequirement).filter(EducationRequirement.job_id == job_id).delete()
            # Add new requirements
            for edu_desc in job_data["education_requirements"]:
                education = EducationRequirement(job_id=job.id, description=edu_desc)
                self.db.add(education)
        
        # Experience requirements
        if "experience_requirements" in job_data:
            # Delete existing requirements
            self.db.query(ExperienceRequirement).filter(ExperienceRequirement.job_id == job_id).delete()
            # Add new requirements
            for exp_desc in job_data["experience_requirements"]:
                experience = ExperienceRequirement(job_id=job.id, description=exp_desc)
                self.db.add(experience)
        
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job_id: str) -> bool:
        """Delete a job description by ID."""
        job = self.get_job_by_id(job_id)
        if not job:
            return False
        
        self.db.delete(job)
        self.db.commit()
        return True

    def format_job_dict(self, job: JobDescription) -> Dict[str, Any]:
        """Format job description object as dictionary."""
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "required_skills": [skill.name for skill in job.required_skills],
            "preferred_skills": [skill.name for skill in job.preferred_skills],
            "education_requirements": [edu.description for edu in job.education_requirements],
            "experience_requirements": [exp.description for exp in job.experience_requirements],
            "created_date": job.created_at.isoformat()
        }