import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from backend.core.security import get_current_user
from backend.core.config import SUPPORTED_EXTENSIONS
from backend.services.parser import parse_resume
from backend.services.scorer import score_resume

router = APIRouter(prefix="/resume", tags=["resume"])

DEFAULT_SKILLS_DB = [
    "Python", "Java", "JavaScript", "TypeScript", "SQL", "Docker",
    "Kubernetes", "AWS", "Azure", "GCP", "React", "FastAPI", "Django",
    "Node.js", "PostgreSQL", "MongoDB", "Git", "CI/CD", "REST API",
    "Machine Learning", "Data Analysis",
]


@router.post("/score")
def score_resume_endpoint(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    required_years: int = Form(0),
    current_user: dict = Depends(get_current_user),
):
    file_extension = os.path.splitext(resume.filename)[1].lower()

    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        contents = resume.file.read()
        tmp_file.write(contents)
        tmp_file_path = tmp_file.name

    try:
        resume_text = parse_resume(tmp_file_path)
        result = score_resume(resume_text, job_description, DEFAULT_SKILLS_DB, required_years)
    finally:
        os.remove(tmp_file_path)

    return result