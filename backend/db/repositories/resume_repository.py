from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from db.models.resume import Resume, Skill, Education, Experience


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_resume(self, resume_data: Dict[str, Any]) -> Resume:
        """Create a new resume and related entities."""
        # Create resume
        resume = Resume(
            file_name=resume_data["file_name"],
            name=resume_data.get("name"),
            email=resume_data.get("email"),
            phone=resume_data.get("phone"),
            full_text=resume_data.get("full_text", "")
        )
        self.db.add(resume)
        self.db.flush()  # Flush to get the resume ID

        # Create skills
        if "skills" in resume_data and isinstance(resume_data["skills"], list):
            for skill_name in resume_data["skills"]:
                skill = Skill(resume_id=resume.id, name=skill_name)
                self.db.add(skill)

        # Create education entries
        if "education" in resume_data and isinstance(resume_data["education"], list):
            for edu_desc in resume_data["education"]:
                education = Education(resume_id=resume.id, description=edu_desc)
                self.db.add(education)

        # Create experience entries
        if "experience" in resume_data and isinstance(resume_data["experience"], list):
            for exp_item in resume_data["experience"]:
                if isinstance(exp_item, dict) and "description" in exp_item:
                    exp_desc = exp_item["description"]
                elif isinstance(exp_item, str):
                    exp_desc = exp_item
                else:
                    continue
                
                experience = Experience(resume_id=resume.id, description=exp_desc)
                self.db.add(experience)

        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_all_resumes(self) -> List[Resume]:
        """Get all resumes."""
        return self.db.query(Resume).order_by(Resume.created_at.desc()).all()

    def get_resume_by_id(self, resume_id: str) -> Optional[Resume]:
        """Get a resume by ID."""
        return self.db.query(Resume).filter(Resume.id == resume_id).first()

    def delete_resume(self, resume_id: str) -> bool:
        """Delete a resume by ID."""
        resume = self.get_resume_by_id(resume_id)
        if not resume:
            return False
        
        self.db.delete(resume)
        self.db.commit()
        return True

    def format_resume_dict(self, resume: Resume) -> Dict[str, Any]:
        """Format resume object as dictionary."""
        return {
            "id": resume.id,
            "file_name": resume.file_name,
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "skills": [skill.name for skill in resume.skills],
            "education": [edu.description for edu in resume.education],
            "experience": [{"description": exp.description} for exp in resume.experience],
            "parsed_date": resume.created_at.isoformat()
        }