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