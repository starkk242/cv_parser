import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from pathlib import Path
import shutil

from app.config import get_settings
from app.api.dependencies import validate_file
from app.api.models.job import JobDescription
from app.services.text_extraction import extract_text_from_file
from app.services.job_parser import extract_job_information
from app.services.storage import save_job_description, get_job_description, get_job_descriptions

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Job Descriptions"])


@router.post("/job", response_model=JobDescription)
async def create_job_description(
    title: str = Form(...),
    company: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    required_skills: Optional[str] = Form(None),
    preferred_skills: Optional[str] = Form(None),
    education_requirements: Optional[str] = Form(None),
    experience_requirements: Optional[str] = Form(None),
    settings = Depends(get_settings)
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
        validate_file(file, settings)
        
        # Save file temporarily
        file_id = f"{id(file)}"
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text from file
            text = extract_text_from_file(str(file_path))
            
            # Parse job description
            job_data = extract_job_information(text, title, company)
            
            logger.info(f"Successfully processed job description file: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
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
    job_id = save_job_description(job_data, settings)
    job_data["id"] = job_id
    
    logger.info(f"Created job description with ID: {job_id}")
    
    return job_data


@router.get("/jobs", response_model=List[JobDescription])
async def list_job_descriptions(settings = Depends(get_settings)):
    """List all job descriptions."""
    return get_job_descriptions(settings)


@router.get("/job/{job_id}", response_model=JobDescription)
async def get_job(job_id: str, settings = Depends(get_settings)):
    """Get a specific job description by ID."""
    job = get_job_description(job_id, settings)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {job_id} not found"
        )
    
    return job