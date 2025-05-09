import os
import shutil
from pathlib import Path
from typing import List
from fastapi import UploadFile, HTTPException, status
from datetime import datetime

# Supported file types and their MIME types
SUPPORTED_MIMETYPES = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/msword': '.doc'
}

def validate_file(file: UploadFile) -> None:
    """
    Validate if the uploaded file is of supported type and size.
    
    Args:
        file (UploadFile): The file to validate
    
    Raises:
        HTTPException: If file type is not supported or file is too large
    """
    # Check file type
    if file.content_type not in SUPPORTED_MIMETYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Supported types are PDF and DOCX."
        )
    
    # You might want to add file size validation
    # This example limits files to 10MB
    if file.size > 10 * 1024 * 1024:  # 10MB in bytes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 10MB."
        )

def save_upload_file(file: UploadFile, upload_dir: str) -> Path:
    """
    Save an uploaded file to the specified directory.
    
    Args:
        file (UploadFile): The file to save
        upload_dir (str): Directory where to save the file
    
    Returns:
        Path: Path to the saved file
    """
    # Create directory if it doesn't exist
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = Path(upload_dir) / safe_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

def cleanup_file(file_path: Path, missing_ok: bool = True) -> None:
    """
    Delete a file if it exists.
    
    Args:
        file_path (Path): Path to the file to delete
        missing_ok (bool): If True, don't raise an error if the file is missing
    """
    try:
        file_path.unlink(missing_ok=missing_ok)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {str(e)}")

def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory (str): Directory path to ensure exists
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_file_extension(file: UploadFile) -> str:
    """
    Get the appropriate file extension based on content type.
    
    Args:
        file (UploadFile): The file to get extension for
    
    Returns:
        str: File extension including the dot
    """
    return SUPPORTED_MIMETYPES.get(file.content_type, '')