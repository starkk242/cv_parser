import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from app.config import Settings


def get_job_description_path(settings: Settings) -> Path:
    """Get path for storing job descriptions."""
    # Ensure directory exists
    Path(settings.JD_DIR).mkdir(parents=True, exist_ok=True)
    return Path(settings.JD_DIR) / "job_descriptions.json"


def save_job_description(job_data: Dict, settings: Settings) -> str:
    """Save job description to file."""
    job_file = get_job_description_path(settings)
    
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


def get_job_descriptions(settings: Settings) -> List[Dict]:
    """Get all job descriptions."""
    job_file = get_job_description_path(settings)
    
    if not job_file.exists():
        return []
    
    with open(job_file, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def get_job_description(job_id: str, settings: Settings) -> Optional[Dict]:
    """Get a specific job description by ID."""
    jobs = get_job_descriptions(settings)
    
    for job in jobs:
        if job.get("id") == job_id:
            return job
    
    return None


def update_job_description(job_id: str, updated_data: Dict, settings: Settings) -> bool:
    """Update an existing job description."""
    job_file = get_job_description_path(settings)
    
    if not job_file.exists():
        return False
    
    with open(job_file, "r") as f:
        try:
            jobs = json.load(f)
        except json.JSONDecodeError:
            return False
    
    # Find and update the job
    for i, job in enumerate(jobs):
        if job.get("id") == job_id:
            # Update all fields except id
            for key, value in updated_data.items():
                if key != "id":
                    job[key] = value
            
            # Save updated list
            with open(job_file, "w") as f:
                json.dump(jobs, f, indent=2)
            
            return True
    
    # Job not found
    return False


def delete_job_description(job_id: str, settings: Settings) -> bool:
    """Delete a job description."""
    job_file = get_job_description_path(settings)
    
    if not job_file.exists():
        return False
    
    with open(job_file, "r") as f:
        try:
            jobs = json.load(f)
        except json.JSONDecodeError:
            return False
    
    # Find and remove the job
    initial_count = len(jobs)
    jobs = [job for job in jobs if job.get("id") != job_id]
    
    if len(jobs) < initial_count:
        # Save updated list
        with open(job_file, "w") as f:
            json.dump(jobs, f, indent=2)
        return True
    
    # Job not found
    return False