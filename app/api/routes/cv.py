import logging
from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path
import pandas as pd
from datetime import datetime
import shutil

from app.config import get_settings
from app.api.dependencies import validate_file
from app.api.models.cv import ParsedResume
from app.services.text_extraction import extract_text_from_file
from app.services.cv_parser import extract_information

logger = logging.getLogger(__name__)

router = APIRouter(tags=["CV Processing"])


def cleanup_file(file_path: Path):
    """Helper function to clean up temporary files"""
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")


@router.post("/upload", response_model=List[ParsedResume])
async def upload_cvs(
    files: List[UploadFile] = File(...),
    format: Optional[str] = Form("json"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    settings = Depends(get_settings)
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
        validate_file(file, settings)
        
        # Save file temporarily
        file_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{id(file)}"
        file_path = Path(settings.UPLOAD_DIR) / f"{file_id}_{file.filename}"
        
        # Ensure upload directory exists
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text based on file type
            text = extract_text_from_file(str(file_path))
            
            # Parse the text
            parsed = extract_information(text, settings)
            parsed["file_name"] = file.filename
            parsed_data.append(parsed)
            
            logger.info(f"Successfully processed file: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing file {file.filename}: {str(e)}"
            )
        finally:
            if settings.CLEANUP_FILES and file_path.exists():
                file_path.unlink()
    
    if format.lower() == "excel":
        # Export to Excel
        try:
            # Ensure parsed directory exists
            Path(settings.PARSED_DIR).mkdir(parents=True, exist_ok=True)
            
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
            
            # Schedule cleanup of the Excel file after response is sent
            background_tasks.add_task(cleanup_file, excel_path)
            
            # Return Excel file
            return FileResponse(
                path=str(excel_path),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=excel_path.name
            )
        except Exception as e:
            logger.error(f"Error generating Excel file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating Excel file: {str(e)}"
            )
    
    return parsed_data