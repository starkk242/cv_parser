import uuid
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import Settings
import json


def get_db_connection(settings: Settings):
    """Establish a connection to the database."""
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_DATABASE,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD
    )


def save_job_description(job_data: Dict, settings: Settings) -> str:
    """Save job description to the database."""
    if "id" not in job_data:
        job_data["id"] = str(uuid.uuid4())
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id UUID PRIMARY KEY,
        data JSONB NOT NULL
    )
    """
    
    insert_query = """
    INSERT INTO job_descriptions (id, data)
    VALUES (%s, %s)
    """
    
    with get_db_connection(settings) as conn:
        with conn.cursor() as cur:
            # Ensure the table exists
            cur.execute(create_table_query)
            # Insert the job description
            cur.execute(insert_query, (job_data["id"], json.dumps(job_data)))
            conn.commit()
    
    return job_data["id"]


def get_job_descriptions(settings: Settings) -> List[Dict]:
    """Get all job descriptions from the database."""
    query = "SELECT data FROM job_descriptions"
    with get_db_connection(settings) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [row["data"] for row in rows]


def get_job_description(job_id: str, settings: Settings) -> Optional[Dict]:
    """Get a specific job description by ID."""
    query = "SELECT data FROM job_descriptions WHERE id = %s"
    with get_db_connection(settings) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (job_id,))
            row = cur.fetchone()
            return row["data"] if row else None


def update_job_description(job_id: str, updated_data: Dict, settings: Settings) -> bool:
    """Update an existing job description."""
    query = """
    UPDATE job_descriptions
    SET data = data || %s
    WHERE id = %s
    """
    with get_db_connection(settings) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (updated_data, job_id))
            conn.commit()
            return cur.rowcount > 0


def delete_job_description(job_id: str, settings: Settings) -> bool:
    """Delete a job description."""
    query = "DELETE FROM job_descriptions WHERE id = %s"
    with get_db_connection(settings) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (job_id,))
            conn.commit()
            return cur.rowcount > 0
