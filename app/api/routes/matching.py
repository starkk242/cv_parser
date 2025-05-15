import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Dict
from pathlib import Path
import pandas as pd
from datetime import datetime
import shutil

from app.config import get_settings
from app.api.dependencies import validate_file
from app.api.models.match import MatchScore
from app.services.text_extraction import extract_text_from_file
from app.services.cv_parser import extract_information
from app.services.matcher import calculate_match_score
from app.services.storage import get_job_description, get_job_descriptions

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Resume-Job Matching"])


@router.post("/match", response_model=List[MatchScore])
async def match_resumes_to_job(
    job_id: str = Form(...),
    files: List[UploadFile] = File(...),
    settings = Depends(get_settings)
):
    """
    Match uploaded resumes against a job description.
    
    - **job_id**: ID of the job description to match against
    - **files**: List of CV/Resume files to match
    """
    # Get job description
    job = get_job_description(job_id, settings)
    
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
        validate_file(file, settings)
        
        # Save file temporarily
        file_id = f"{id(file)}"
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text based on file type
                        # Extract text based on file type
            text = extract_text_from_file(str(file_path))
            
            # Parse the resume
            parsed_resume = extract_information(text)
            parsed_resume["file_name"] = file.filename
            
            # Calculate match score
            match_score = calculate_match_score(parsed_resume, job)
            match_results.append(match_score)
            
            logger.info(f"Successfully matched resume {file.filename} with job {job_id}")
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
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


@router.post("/batch-match", response_model=Dict[str, List[MatchScore]])
async def batch_match_resumes_to_jobs(
    files: List[UploadFile] = File(...),
    job_ids: str = Form(...),
    settings = Depends(get_settings)
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
        job = get_job_description(job_id, settings)
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
        validate_file(file, settings)
        
        # Save file temporarily
        file_id = f"{id(file)}"
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
            
            logger.info(f"Successfully parsed resume: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
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
        
        logger.info(f"Completed matching {len(parsed_resumes)} resumes against job {job_id}")
    
    return results


@router.post("/export-matches/{job_id}")
async def export_matches(
    job_id: str,
    files: List[UploadFile] = File(...),
    settings = Depends(get_settings)
):
    """
    Match resumes against a job description and export results to Excel.
    
    - **job_id**: ID of the job description to match against
    - **files**: List of CV/Resume files to match
    """
    # Get matches
    try:
        match_results = await match_resumes_to_job(job_id=job_id, files=files, settings=settings)
    except HTTPException as e:
        raise e
    
    # Get job description
    job = get_job_description(job_id, settings)
    
    # Create Excel file
    try:
        # Ensure parsed directory exists
        Path(settings.PARSED_DIR).mkdir(parents=True, exist_ok=True)
        
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
        
        logger.info(f"Generated Excel report for job {job_id} with {len(match_results)} matches")
        
        # Return Excel file
        return FileResponse(
            path=str(excel_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=excel_path.name,
            background=BackgroundTasks(lambda: excel_path.unlink(missing_ok=True))  # Clean up the file after sending
        )
    except Exception as e:
        logger.error(f"Error generating Excel file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Excel file: {str(e)}"
        )