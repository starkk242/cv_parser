#!/usr/bin/env python3

import os
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union

import spacy
import pdfplumber
import docx2txt
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, BaseSettings
from starlette.background import BackgroundTask

class Settings(BaseSettings):
    UPLOAD_DIR: str = "uploads"
    PARSED_DIR: str = "parsed"
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    CLEANUP_FILES: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
nlp = spacy.load("en_core_web_sm")

# Create necessary directories
for directory in [settings.UPLOAD_DIR, settings.PARSED_DIR]:
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

app = FastAPI(
    title="CV Parser API",
    description="API for parsing CV/Resume documents",
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

def extract_information(text: str) -> Dict:
    """Extract relevant information from text using spaCy."""
    doc = nlp(text)
    
    # Extract email addresses
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    
    # Extract phone numbers
    phone_pattern = r"(?:\+91[\s-]?(?:\d{5}\s\d{5}|\d{10}|\d{4}-\d{6}))|(?:\+\d{1,3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4})|(?:\b\d{3}[-\.]?\d{3}[-\.]?\d{4}\b)|(?:\b\d{10}\b)"
    phones = re.findall(phone_pattern, text)
    
    # Extract name (assume first proper noun in document is the name)
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)
    
    # Extract education (look for education-related keywords)
    education = []
    edu_keywords = {"degree", "bachelor", "master", "phd", "diploma", "university", "college"}
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in edu_keywords):
            education.append(sent.text.strip())
    
    # Extract skills (look for technical terms and proper nouns)
    skills = []
    for token in doc:
        if token.pos_ in {"PROPN", "NOUN"} and len(token.text) > 2:
            skills.append(token.text)
    
    # Extract work experience
    experience = []
    exp_keywords = {"experience", "work", "employment", "job", "position"}
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
            if file_path.suffix.lower() == ".pdf":
                text = extract_text_from_pdf(str(file_path))
            else:
                text = extract_text_from_docx(str(file_path))
            
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

@app.get("/")
def root():
    """Check if the API is running."""
    return {
        "message": "CV Parser API is running",
        "version": "1.0.0",
        "status": "healthy"
    }
