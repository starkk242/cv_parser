from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

def flatten_resume_data(resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten nested resume data structure for Excel export with improved formatting.
    """
    flat_resume = {}
    
    # Handle basic fields with proper formatting
    basic_fields = ['name', 'email', 'phone', 'location']
    for field in basic_fields:
        flat_resume[field.capitalize()] = resume.get(field, '')
    
    # Format skills with categories if available
    if "skills" in resume and isinstance(resume["skills"], list):
        skills_by_category = {}
        for skill in resume["skills"]:
            if isinstance(skill, dict):
                category = skill.get('category', 'Other')
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill.get('name', ''))
            else:
                if 'Other' not in skills_by_category:
                    skills_by_category['Other'] = []
                skills_by_category['Other'].append(skill)
        
        # Format skills by category
        for category, skills in skills_by_category.items():
            flat_resume[f"Skills - {category}"] = ", ".join(skills)
    
    # Format education with structured information
    if "education" in resume and isinstance(resume["education"], list):
        for i, edu in enumerate(resume["education"], 1):
            if isinstance(edu, dict):
                edu_info = []
                if 'degree' in edu:
                    edu_info.append(edu['degree'])
                if 'institution' in edu:
                    edu_info.append(edu['institution'])
                if 'year' in edu:
                    edu_info.append(str(edu['year']))
                flat_resume[f"Education {i}"] = " - ".join(filter(None, edu_info))
            elif isinstance(edu, str):
                flat_resume[f"Education {i}"] = edu
    
    # Format experience with detailed information
    if "experience" in resume and isinstance(resume["experience"], list):
        for i, exp in enumerate(resume["experience"], 1):
            if isinstance(exp, dict):
                exp_info = []
                if 'title' in exp:
                    exp_info.append(exp['title'])
                if 'company' in exp:
                    exp_info.append(exp['company'])
                if 'duration' in exp:
                    exp_info.append(exp['duration'])
                if 'description' in exp:
                    flat_resume[f"Experience {i} - Details"] = exp['description']
                flat_resume[f"Experience {i}"] = " | ".join(filter(None, exp_info))
            elif isinstance(exp, str):
                flat_resume[f"Experience {i}"] = exp
    
    # Add additional relevant fields
    if "languages" in resume:
        flat_resume["Languages"] = ", ".join(resume["languages"]) if isinstance(resume["languages"], list) else resume["languages"]
    
    if "certifications" in resume:
        flat_resume["Certifications"] = ", ".join(resume["certifications"]) if isinstance(resume["certifications"], list) else resume["certifications"]
    
    return flat_resume

def export_to_excel(parsed_data: List[Dict[str, Any]], output_dir: Path) -> FileResponse:
    """
    Export parsed resume data to Excel file with improved formatting.
    """
    # Create flattened data
    flattened_data = [flatten_resume_data(resume) for resume in parsed_data]
    
    # Create dataframe with ordered columns
    df = pd.DataFrame(flattened_data)
    
    # Reorder columns for better readability
    column_order = (
        ['Name', 'Email', 'Phone', 'Location'] +
        [col for col in df.columns if col.startswith('Skills')] +
        [col for col in df.columns if col.startswith('Education')] +
        [col for col in df.columns if col.startswith('Experience')] +
        [col for col in df.columns if col not in df.columns[:4] and 
         not col.startswith(('Skills', 'Education', 'Experience'))]
    )
    
    # Reorder and filter existing columns only
    final_columns = [col for col in column_order if col in df.columns]
    df = df[final_columns]
    
    # Generate Excel file path
    excel_path = output_dir / f"parsed_resumes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Export to Excel with improved formatting
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Parsed Resumes')
        worksheet = writer.sheets['Parsed Resumes']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = min(adjusted_width, 50)
    
    return FileResponse(
        path=str(excel_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=excel_path.name,
        background=BackgroundTask(lambda: excel_path.unlink(missing_ok=True))
    )