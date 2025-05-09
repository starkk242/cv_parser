#!/usr/bin/env python3

import os
import re
import shutil
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

import spacy
import pdfplumber
import docx2txt
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings, Field
from starlette.background import BackgroundTask
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Settings(BaseSettings):
    UPLOAD_DIR: str = "uploads"
    PARSED_DIR: str = "parsed"
    JD_DIR: str = "job_descriptions"
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    CLEANUP_FILES: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
nlp = spacy.load("en_core_web_sm")

# Create necessary directories
for directory in [settings.UPLOAD_DIR, settings.PARSED_DIR, settings.JD_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)

class ParsedResume(BaseModel):
    file_name: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    education: List[str] = []
    skills: List[str] = []
    experience: List[Dict[str, str]] = []
    parsed_date: str

class JobDescription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: Optional[str] = None
    description: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education_requirements: List[str] = []
    experience_requirements: List[str] = []
    created_date: str = Field(default_factory=lambda: datetime.now().isoformat())

class MatchScore(BaseModel):
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

app = FastAPI(
    title="CV Parser & Job Matching API",
    description="API for parsing CV/Resume documents and matching them against job descriptions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error extracting text from PDF: {str(e)}"
        )
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from DOCX file."""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error extracting text from DOCX: {str(e)}"
        )

def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats."""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_path)
    elif file_ext == ".txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file_ext}"
        )

def extract_information(text: str) -> Dict:
    """Extract relevant information from text using spaCy."""
    doc = nlp(text)
    
    # Extract email addresses
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    
    # Extract phone numbers
    phone_pattern = r"(?:\+91[\s-]?(?:\d{5}\s\d{5}|\d{10}|\d{4}-\d{6}))|(?:\b\d{10}\b)"
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

def validate_file(file: UploadFile) -> None:
    """Validate file type and size."""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {'.'.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)  # Seek back to start
    
    if size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE/1024/1024}MB"
        )
    
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )

def get_job_description_path() -> Path:
    """Get path for storing job descriptions."""
    return Path(settings.JD_DIR) / "job_descriptions.json"

def save_job_description(job_data: Dict) -> str:
    """Save job description to file."""
    job_file = get_job_description_path()
    
    # Create job ID if not provided
    if "id" not in job_data:
        job_data["id"] = str(uuid.uuid4())
    
    # Load existing jobs or create empty list
    if job_file.exists():
        with open(job_file, "r") as f:
            try:
                jobs = json.load(f)
            except json.JSONDecodeError:
                jobs = []
    else:
        jobs = []
    
    # Add new job
    jobs.append(job_data)
    
    # Save updated jobs list
    with open(job_file, "w") as f:
        json.dump(jobs, f, indent=2)
    
    return job_data["id"]

def get_job_descriptions() -> List[Dict]:
    """Get all job descriptions."""
    job_file = get_job_description_path()
    
    if not job_file.exists():
        return []
    
    with open(job_file, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def get_job_description(job_id: str) -> Optional[Dict]:
    """Get a specific job description by ID."""
    jobs = get_job_descriptions()
    
    for job in jobs:
        if job.get("id") == job_id:
            return job
    
    return None

def calculate_match_score(resume: Dict, job: Dict) -> Dict:
    """Calculate match score between resume and job description."""
    # 1. Calculate skill match score
    resume_skills = set([skill.lower() for skill in resume.get("skills", [])])
    required_skills = set([skill.lower() for skill in job.get("required_skills", [])])
    preferred_skills = set([skill.lower() for skill in job.get("preferred_skills", [])])
    
    # Match skills (accounting for partial matches)
    matched_skills = []
    for job_skill in list(required_skills) + list(preferred_skills):
        for resume_skill in resume_skills:
            # Check for exact match or if job skill is contained in resume skill or vice versa
            if (job_skill == resume_skill or 
                job_skill in resume_skill or 
                resume_skill in job_skill):
                matched_skills.append(job_skill)
                break
    
    matched_skills_set = set(matched_skills)
    missing_skills = required_skills - matched_skills_set
    
    # Calculate skill score (give more weight to required skills)
    req_skill_match = len([s for s in matched_skills if s.lower() in required_skills]) / max(len(required_skills), 1)
    pref_skill_match = len([s for s in matched_skills if s.lower() in preferred_skills]) / max(len(preferred_skills), 1) if preferred_skills else 1.0
    
    # Weight: 70% required skills, 30% preferred skills
    skills_score = (req_skill_match * 0.7) + (pref_skill_match * 0.3)
    
    # 2. Calculate education match score
    resume_edu = " ".join(resume.get("education", [])).lower()
    job_edu_reqs = [req.lower() for req in job.get("education_requirements", [])]
    
    matched_education = []
    for edu_req in job_edu_reqs:
        if edu_req in resume_edu:
            matched_education.append(edu_req)
    
    education_score = len(matched_education) / max(len(job_edu_reqs), 1) if job_edu_reqs else 0.5
    
    # 3. Calculate experience match score
    resume_exp = " ".join([exp.get("description", "") for exp in resume.get("experience", [])]).lower()
    job_exp_reqs = [req.lower() for req in job.get("experience_requirements", [])]
    
    matched_exp_keywords = []
    for exp_req in job_exp_reqs:
        if exp_req in resume_exp:
            matched_exp_keywords.append(exp_req)
    
    experience_score = len(matched_exp_keywords) / max(len(job_exp_reqs), 1) if job_exp_reqs else 0.5
    
    # 4. Calculate keyword match using TF-IDF and cosine similarity
    resume_text = " ".join([
        " ".join(resume.get("skills", [])),
        " ".join(resume.get("education", [])),
        " ".join([exp.get("description", "") for exp in resume.get("experience", [])])
    ]).lower()
    
    job_text = " ".join([
        job.get("description", ""),
        " ".join(job.get("required_skills", [])),
        " ".join(job.get("preferred_skills", [])),
        " ".join(job.get("education_requirements", [])),
        " ".join(job.get("experience_requirements", []))
    ]).lower()
    
    # Calculate text similarity
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        keyword_match_score = max(0, min(cosine_sim, 1.0))  # Ensure score is between 0 and 1
    except:
        # Fallback if vectorization fails (e.g., empty text)
        keyword_match_score = 0.0
    
    # Calculate overall score
    # Weights: Skills 40%, Education 20%, Experience 20%, Keyword match 20%
    overall_score = (
        (skills_score * 0.4) + 
        (education_score * 0.2) + 
        (experience_score * 0.2) + 
        (keyword_match_score * 0.2)
    ) * 100  # Convert to percentage
    
    return {
        "resume_id": resume.get("file_name", "Unknown"),
        "resume_name": resume.get("name", "Unknown"),
        "job_id": job.get("id", "Unknown"),
        "job_title": job.get("title", "Unknown"),
        "overall_score": round(overall_score, 2),
        "skills_score": round(skills_score * 100, 2),
        "education_score": round(education_score * 100, 2),
        "experience_score": round(experience_score * 100, 2),
        "keyword_match_score": round(keyword_match_score * 100, 2),
        "matched_skills": list(matched_skills_set),
        "matched_education": matched_education,
        "matched_experience_keywords": matched_exp_keywords,
        "missing_skills": list(missing_skills)
    }

@app.post("/upload", response_model=List[ParsedResume])
async def upload_cvs(
    files: List[UploadFile] = File(...),
    format: Optional[str] = "json"
):
    """
    Upload and parse CV/Resume files.
    
    - **files**: List of CV/Resume files (PDF or DOCX)
    - **format**: Response format ("json" or "excel", default: "json")
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    parsed_data = []
    
    for file in files:
        validate_file(file)
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        # Ensure upload directory exists
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text based on file type
            text = extract_text_from_file(str(file_path))
            
            # Parse the text
            parsed = extract_information(text)
            parsed["file_name"] = file.filename
            parsed_data.append(parsed)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )
        finally:
            if settings.CLEANUP_FILES and file_path.exists():
                file_path.unlink()
    
    if format.lower() == "excel":
        # Ensure parsed directory exists
        Path(settings.PARSED_DIR).mkdir(parents=True, exist_ok=True)
        
        # Export to Excel
        try:
            # Flatten nested structures for better Excel representation
            flattened_data = []
            for resume in parsed_data:
                flat_resume = {}
                
                # Flatten basic fields
                for key, value in resume.items():
                    if not isinstance(value, (list, dict)):
                        flat_resume[key] = value
                
                # Handle skills list - convert to comma-separated string
                if "skills" in resume and isinstance(resume["skills"], list):
                    # Limit skills to top 15 most relevant to avoid excessive column width
                    top_skills = resume["skills"][:15] if len(resume["skills"]) > 15 else resume["skills"]
                    flat_resume["skills"] = ", ".join(top_skills)
                    if len(resume["skills"]) > 15:
                        flat_resume["skills"] += f" (+ {len(resume['skills']) - 15} more)"
                    
                # Handle education entries
                if "education" in resume and isinstance(resume["education"], list):
                    # For the sample data, education is a list of strings rather than objects
                    if resume["education"] and isinstance(resume["education"][0], str):
                        # Join all education strings with a separator
                        flat_resume["education"] = " | ".join(resume["education"])
                    else:
                        # Handle structured education data if format changes
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
                            # Just store the description directly with a numbered prefix
                            flat_resume[f"experience_{i+1}"] = exp["description"]
                        elif isinstance(exp, dict):
                            prefix = f"experience_{i+1}_"
                            for exp_key, exp_val in exp.items():
                                flat_resume[f"{prefix}{exp_key}"] = exp_val
                        elif isinstance(exp, str):
                            flat_resume[f"experience_{i+1}"] = exp
                
                flattened_data.append(flat_resume)
            
            # Create dataframe from flattened data
            df = pd.DataFrame(flattened_data)
            
            # Generate Excel file
            excel_path = Path(settings.PARSED_DIR) / f"parsed_resumes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(excel_path, index=False)
            
            # Return Excel file
            return FileResponse(
                path=str(excel_path),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=excel_path.name,
                background=BackgroundTask(lambda: excel_path.unlink(missing_ok=True))  # Clean up the file after sending
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating Excel file: {str(e)}"
            )
    
    return parsed_data

@app.post("/job", response_model=JobDescription)
async def create_job_description(
    title: str = Form(...),
    company: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    required_skills: Optional[str] = Form(None),
    preferred_skills: Optional[str] = Form(None),
    education_requirements: Optional[str] = Form(None),
    experience_requirements: Optional[str] = Form(None)
):
    """
    Create a new job description.
    
    - **title**: Job title
    - **company**: Company name (optional)
    - **file**: Job description file (PDF, DOCX, TXT) (optional)
    - **description**: Job description text (optional if file is provided)
    - **required_skills**: Comma-separated list of required skills (optional)
    - **preferred_skills**: Comma-separated list of preferred skills (optional)
    - **education_requirements**: Comma-separated list of education requirements (optional)
    - **experience_requirements**: Comma-separated list of experience requirements (optional)
    """
    # Either file or description must be provided
    if not file and not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file or description must be provided"
        )
    
    job_data = {}
    
    # Process file if provided
    if file:
        validate_file(file)
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text from file
            text = extract_text_from_file(str(file_path))
            
            # Parse job description
            job_data = extract_job_information(text, title, company)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )
        finally:
            if settings.CLEANUP_FILES and file_path.exists():
                file_path.unlink()
    else:
        # Use provided text description
        job_data = extract_job_information(description, title, company)
    
    # Override with manually provided fields if they exist
    if required_skills:
        job_data["required_skills"] = [skill.strip() for skill in required_skills.split(",") if skill.strip()]
    
    if preferred_skills:
        job_data["preferred_skills"] = [skill.strip() for skill in preferred_skills.split(",") if skill.strip()]
    
    if education_requirements:
        job_data["education_requirements"] = [edu.strip() for edu in education_requirements.split(",") if edu.strip()]
    
    if experience_requirements:
        job_data["experience_requirements"] = [exp.strip() for exp in experience_requirements.split(",") if exp.strip()]
    
    # Save job description
    job_id = save_job_description(job_data)
    job_data["id"] = job_id
    
    return job_data

@app.get("/jobs", response_model=List[JobDescription])
async def list_job_descriptions():
    """List all job descriptions."""
    return get_job_descriptions()

@app.get("/job/{job_id}", response_model=JobDescription)
async def get_job(job_id: str):
    """Get a specific job description by ID."""
    job = get_job_description(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {job_id} not found"
        )
    
    return job

@app.post("/match", response_model=List[MatchScore])
async def match_resumes_to_job(
    job_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Match uploaded resumes against a job description.
    
    - **job_id**: ID of the job description to match against
    - **files**: List of CV/Resume files to match
    """
    # Get job description
    job = get_job_description(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {job_id} not found"
        )
    
    # Process resumes
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    match_results = []
    
    for file in files:
        validate_file(file)
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text based on file type
            text = extract_text_from_file(str(file_path))
            
            # Parse the resume
            parsed_resume = extract_information(text)
            parsed_resume["file_name"] = file.filename
            
            # Calculate match score
            match_score = calculate_match_score(parsed_resume, job)
            match_results.append(match_score)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )
        finally:
            if settings.CLEANUP_FILES and file_path.exists():
                file_path.unlink()
    
    # Sort results by overall score (descending)
    match_results.sort(key=lambda x: x["overall_score"], reverse=True)
    
    return match_results

@app.post("/batch-match", response_model=Dict[str, List[MatchScore]])
async def batch_match_resumes_to_jobs(
    files: List[UploadFile] = File(...),
    job_ids: str = Form(...)
):
    """
    Match uploaded resumes against multiple job descriptions.
    
    - **files**: List of CV/Resume files to match
    - **job_ids**: Comma-separated list of job IDs to match against
    """
    # Parse job IDs
    job_id_list = [job_id.strip() for job_id in job_ids.split(",") if job_id.strip()]
    
    if not job_id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No job IDs provided"
        )
    
    # Get job descriptions
    jobs = {}
    for job_id in job_id_list:
        job = get_job_description(job_id)
        if job:
            jobs[job_id] = job
    
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No valid job descriptions found"
        )
    
    # Process resumes
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Parse all resumes first
    parsed_resumes = []
    for file in files:
        validate_file(file)
        
        # Save file temporarily
        file_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text based on file type
            text = extract_text_from_file(str(file_path))
            
            # Parse the resume
            parsed_resume = extract_information(text)
            parsed_resume["file_name"] = file.filename
            parsed_resumes.append(parsed_resume)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )
        finally:
            if settings.CLEANUP_FILES and file_path.exists():
                file_path.unlink()
    
    # Match against each job
    results = {}
    for job_id, job in jobs.items():
        job_matches = []
        for resume in parsed_resumes:
            match_score = calculate_match_score(resume, job)
            job_matches.append(match_score)
        
        # Sort matches by overall score (descending)
        job_matches.sort(key=lambda x: x["overall_score"], reverse=True)
        results[job_id] = job_matches
    
    return results

@app.post("/export-matches/{job_id}")
async def export_matches(
    job_id: str,
    files: List[UploadFile] = File(...)
):
    """
    Match resumes against a job description and export results to Excel.
    
    - **job_id**: ID of the job description to match against
    - **files**: List of CV/Resume files to match
    """
    # Get matches
    try:
        match_results = await match_resumes_to_job(job_id=job_id, files=files)
    except HTTPException as e:
        raise e
    
    # Get job description
    job = get_job_description(job_id)
    
    # Create Excel file
    try:
        # Flatten match results for Excel
        flattened_data = []
        for match in match_results:
            flat_match = {}
            
            # Add basic fields
            flat_match["Resume Name"] = match["resume_name"]
            flat_match["Resume File"] = match["resume_id"]
            flat_match["Job Title"] = match["job_title"]
            flat_match["Overall Match Score"] = f"{match['overall_score']}%"
            flat_match["Skills Score"] = f"{match['skills_score']}%"
            flat_match["Education Score"] = f"{match['education_score']}%"
            flat_match["Experience Score"] = f"{match['experience_score']}%"
            flat_match["Keyword Match"] = f"{match['keyword_match_score']}%"
            
            # Add matched skills
            flat_match["Matched Skills"] = ", ".join(match["matched_skills"])
            
            # Add missing skills
            flat_match["Missing Skills"] = ", ".join(match["missing_skills"])
            
            # Add matched education
            flat_match["Matched Education"] = ", ".join(match["matched_education"])
            
            # Add matched experience
            flat_match["Matched Experience"] = ", ".join(match["matched_experience_keywords"])
            
            flattened_data.append(flat_match)
        
        # Create dataframe
        df = pd.DataFrame(flattened_data)
        
        # Generate Excel file
        excel_path = Path(settings.PARSED_DIR) / f"job_matches_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Write match results to main sheet
            df.to_excel(writer, sheet_name="Match Results", index=False)
            
            # Write job details to second sheet if job exists
            if job:
                job_df = pd.DataFrame({
                    "Field": ["Title", "Company", "Required Skills", "Preferred Skills", "Education Requirements", "Experience Requirements"],
                    "Value": [
                        job.get("title", ""),
                        job.get("company", ""),
                        ", ".join(job.get("required_skills", [])),
                        ", ".join(job.get("preferred_skills", [])),
                        ", ".join(job.get("education_requirements", [])),
                        ", ".join(job.get("experience_requirements", []))
                    ]
                })
                job_df.to_excel(writer, sheet_name="Job Description", index=False)
        
        # Return Excel file
        return FileResponse(
            path=str(excel_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=excel_path.name,
            background=BackgroundTask(lambda: excel_path.unlink(missing_ok=True))  # Clean up the file after sending
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Excel file: {str(e)}"
        )

@app.get("/")
def root():
    """Check if the API is running."""
    return {
        "message": "CV Parser & Job Matching API is running",
        "version": "1.0.0",
        "status": "healthy"
    }