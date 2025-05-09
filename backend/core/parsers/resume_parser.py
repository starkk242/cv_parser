from pathlib import Path
import shutil
from typing import List, Dict, Any
from utils.file_utils import validate_file
from utils.export_utils import extract_text_from_file

class ResumeParser:
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse a single resume file and extract information."""
        # Extract text from file
        text = extract_text_from_file(file_path)
        
        # Parse the text and extract information
        parsed = extract_information(text)
        return parsed

    def parse_resumes(self, files: List[str]) -> List[Dict[str, Any]]:
        """Parse multiple resume files and return extracted information."""
        parsed_data = []
        
        for file_path in files:
            parsed = self.parse_resume(file_path)
            parsed["file_name"] = Path(file_path).name
            parsed_data.append(parsed)
            
        return parsed_data

    def flatten_resume_data(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flatten nested resume data structure for export."""
        flattened_data = []
        
        for resume in parsed_data:
            flat_resume = {}
            
            # Flatten basic fields
            for key, value in resume.items():
                if not isinstance(value, (list, dict)):
                    flat_resume[key] = value
            
            # Handle skills list
            if "skills" in resume and isinstance(resume["skills"], list):
                top_skills = resume["skills"][:15] if len(resume["skills"]) > 15 else resume["skills"]
                flat_resume["skills"] = ", ".join(top_skills)
                if len(resume["skills"]) > 15:
                    flat_resume["skills"] += f" (+ {len(resume['skills']) - 15} more)"
                
            # Handle education entries
            if "education" in resume and isinstance(resume["education"], list):
                if resume["education"] and isinstance(resume["education"][0], str):
                    flat_resume["education"] = " | ".join(resume["education"])
                else:
                    for i, edu in enumerate(resume["education"]):
                        if isinstance(edu, dict):
                            prefix = f"education_{i+1}_"
                            for edu_key, edu_val in edu.items():
                                flat_resume[f"{prefix}{edu_key}"] = edu_val
                        elif isinstance(edu, str):
                            flat_resume[f"education_{i+1}"] = edu
            
            # Handle experience list
            if "experience" in resume and isinstance(resume["experience"], list):
                for i, exp in enumerate(resume["experience"]):
                    if isinstance(exp, dict) and "description" in exp:
                        flat_resume[f"experience_{i+1}"] = exp["description"]
                    elif isinstance(exp, dict):
                        prefix = f"experience_{i+1}_"
                        for exp_key, exp_val in exp.items():
                            flat_resume[f"{prefix}{exp_key}"] = exp_val
                    elif isinstance(exp, str):
                        flat_resume[f"experience_{i+1}"] = exp
            
            flattened_data.append(flat_resume)
        
        return flattened_data
