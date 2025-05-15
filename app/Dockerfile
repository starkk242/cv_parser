FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads data/parsed data/job_descriptions

EXPOSE 8000

# Run the application
CMD ["cd", ".."]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]