import re
import spacy
from typing import Dict, Optional
from datetime import datetime
import json
from openai import OpenAI
from app.config import Settings

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
    try:

        client = OpenAI(
            api_key=Settings.OPEN_AI,
            base_url="https://inference.baseten.co/v1"
        )

        prompt = f"""
        Extract information from this job description text and respond in the following JSON format:
        {{
            "title": "{title}",
            "company": "{company}",
            "description": "{text}",
            "required_skills": ["list of required skills"],
            "preferred_skills": ["list of preferred skills"],
            "education_requirements": ["list of education requirements"],
            "experience_requirements": ["list of experience requirements"],
        }}

        Job description text:
        {text}

        Return only the JSON structure, no other text.
        """

        response = client.chat.completions.create(
            model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        
        # Parse the response content
        content = response.choices[0].message.content
        json_str = content.strip('`json\n').strip()

        while '<think>' in json_str and '</think>' in json_str:
            start = json_str.find('<think>')
            end = json_str.find('</think>') + len('</think>')
            json_str = json_str[:start] + json_str[end:]
        
        result = json.loads(json_str)
        result["created_date"] = datetime.now().isoformat()
        return result
    
    except Exception as e:

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
       