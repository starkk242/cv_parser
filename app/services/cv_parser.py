import re
import spacy
from typing import Dict
from datetime import datetime

# Initialize spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model is not available, download it
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


def extract_information(text: str) -> Dict:
    """Extract relevant information from resume text using spaCy."""
    doc = nlp(text)
    
    # Extract email addresses
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    
    # Extract phone numbers - expanded pattern to catch more formats
    phone_pattern = r"(?:\+91[\s-]?(?:\d{5}\s\d{5}|\d{10}|\d{4}-\d{6}))|(?:\+\d{1,3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4})|(?:\b\d{3}[-\.]?\d{3}[-\.]?\d{4}\b)|(?:\b\d{10}\b)"
    phones = re.findall(phone_pattern, text)
    
    # Extract name (assume first proper noun in document is the name)
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)
    
    # Extract education (look for education-related keywords)
    education = []
    edu_keywords = {"degree", "bachelor", "master", "phd", "diploma", "university", "college", "school", "certification"}
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in edu_keywords):
            education.append(sent.text.strip())
    
    # Extract skills (look for technical terms and proper nouns)
    skills = []
    for token in doc:
        if token.pos_ in {"PROPN", "NOUN"} and len(token.text) > 2 and token.text.lower() not in {"the", "and", "for", "with"}:
            skills.append(token.text)
    
    # Extract work experience
    experience = []
    exp_keywords = {"experience", "work", "employment", "job", "position", "role", "career", "professional"}
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in exp_keywords):
            experience.append({"description": sent.text.strip()})
    
    return {
        "name": name,
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "education": list(set(education)),
        "skills": list(set(skills)),
        "experience": experience[:5],  # Limit to last 5 experiences
        "parsed_date": datetime.now().isoformat()
    }