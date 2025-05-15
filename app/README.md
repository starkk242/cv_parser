# CV Parser & Job Matching API

A production-ready API for parsing CV/Resume documents and matching them against job descriptions.

## Features

- Parse CV/Resume files (PDF, DOCX, TXT)
- Extract key information:
  - Contact details (name, email, phone)
  - Education history
  - Skills
  - Work experience
- Create and manage job descriptions
- Match resumes against job descriptions with scores for:
  - Overall match
  - Skills match
  - Education match
  - Experience match
  - Keyword match
- Export results to Excel

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Usage
Start the server: uvicorn app.main:app --reload

API will be available at http://localhost:8000

API Documentation available at http://localhost:8000/docs

API Endpoints
CV Processing
POST /upload - Upload and parse CV/Resume files
Job Descriptions
POST /job - Create a new job description
GET /jobs - List all job descriptions
GET /job/{job_id} - Get a specific job description
Matching
POST /match - Match uploaded resumes against a job description
POST /batch-match - Match uploaded resumes against multiple job descriptions
POST /export-matches/{job_id} - Match resumes and export results to Excel