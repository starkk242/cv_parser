import re
import spacy
from typing import Dict, Optional

# Initialize spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not available, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


def extract_job_information(text: str, title: str, company: Optional[str] = None) -> Dict:
    """Extract relevant information from job description text."""
    doc = nlp(text)
    
    # Extract required skills
    required_skills = []
    skill_patterns = [
        r"required skills[:]?\s*(.+?)(?=\n\n|\Z)",
        r"requirements[:]?\s*(.+?)(?=\n\n|\Z)",
        r"qualifications[:]?\s*(.+?)(?=\n\n|\Z)",
        r"technical skills[:]?\s*(.+?)(?=\n\n|\Z)",
        r"must have[:]?\s*(.+?)(?=\n\n|\Z)"
    ]
    
    for pattern in skill_patterns:
        matches = re.search(pattern, text.lower(), re.DOTALL)
        if matches:
            skills_text = matches.group(1)
            # Look for bullet points or numbered list
            skills_list = re.findall(r"(?:•|-|\d+\.)\s*([^•\n]+)", skills_text)
            if skills_list:
                required_skills.extend([skill.strip() for skill in skills_list])
            else:
                # Just split by commas or new lines if no bullet points found
                skills_list = re.split(r",|\n", skills_text)
                required_skills.extend([skill.strip() for skill in skills_list if skill.strip()])
    
    # Extract preferred skills
    preferred_skills = []
    pref_patterns = [
        r"preferred skills[:]?\s*(.+?)(?=\n\n|\Z)",
        r"nice to have[:]?\s*(.+?)(?=\n\n|\Z)",
        r"preferred qualifications[:]?\s*(.+?)(?=\n\n|\Z)",
        r"desirable[:]?\s*(.+?)(?=\n\n|\Z)"
    ]
    
    for pattern in pref_patterns:
        matches = re.search(pattern, text.lower(), re.DOTALL)
        if matches:
            skills_text = matches.group(1)
            skills_list = re.findall(r"(?:•|-|\d+\.)\s*([^•\n]+)", skills_text)
            if skills_list:
                preferred_skills.extend([skill.strip() for skill in skills_list])
            else:
                skills_list = re.split(r",|\n", skills_text)
                preferred_skills.extend([skill.strip() for skill in skills_list if skill.strip()])
    
    # Extract education requirements
    education_requirements = []
    edu_patterns = [
        r"education[:]?\s*(.+?)(?=\n\n|\Z)",
        r"academic requirements[:]?\s*(.+?)(?=\n\n|\Z)",
        r"degree[:]?\s*(.+?)(?=\n\n|\Z)"
    ]
    
    for pattern in edu_patterns:
        matches = re.search(pattern, text.lower(), re.DOTALL)
        if matches:
            edu_text = matches.group(1)
            edu_list = re.findall(r"(?:•|-|\d+\.)\s*([^•\n]+)", edu_text)
            if edu_list:
                education_requirements.extend([edu.strip() for edu in edu_list])
            else:
                edu_list = re.split(r",|\n", edu_text)
                education_requirements.extend([edu.strip() for edu in edu_list if edu.strip()])
    
    # Extract experience requirements
    experience_requirements = []
    exp_patterns = [
        r"experience[:]?\s*(.+?)(?=\n\n|\Z)",
        r"work experience[:]?\s*(.+?)(?=\n\n|\Z)",
        r"years of experience[:]?\s*(.+?)(?=\n\n|\Z)"
    ]
    
    for pattern in exp_patterns:
        matches = re.search(pattern, text.lower(), re.DOTALL)
        if matches:
            exp_text = matches.group(1)
            exp_list = re.findall(r"(?:•|-|\d+\.)\s*([^•\n]+)", exp_text)
            if exp_list:
                experience_requirements.extend([exp.strip() for exp in exp_list])
            else:
                exp_list = re.split(r",|\n", exp_text)
                experience_requirements.extend([exp.strip() for exp in exp_list if exp.strip()])

    # If we didn't find any structured data, use NLP to extract key information
    if not required_skills:
        # Extract nouns and proper nouns that might be skills
        for token in doc:
            if token.pos_ in {"PROPN", "NOUN"} and len(token.text) > 2 and token.text.lower() not in {"the", "and", "for", "with"}:
                if any(keyword in text.lower() for keyword in ["require", "must", "need", "skill"]):
                    required_skills.append(token.text)
                else:
                    preferred_skills.append(token.text)
    
    # Ensure no duplicates
    required_skills = list(set([s for s in required_skills if s]))
    preferred_skills = list(set([s for s in preferred_skills if s and s not in required_skills]))
    education_requirements = list(set([e for e in education_requirements if e]))
    experience_requirements = list(set([e for e in experience_requirements if e]))
    
    # Create the job data dictionary
    from datetime import datetime
    
    return {
        "title": title,
        "company": company,
        "description": text,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "education_requirements": education_requirements,
        "experience_requirements": experience_requirements,
        "created_date": datetime.now().isoformat()
    }