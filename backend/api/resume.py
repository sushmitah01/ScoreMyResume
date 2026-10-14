import tempfile
import os
import docx
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from backend.core.security import get_current_user
from backend.core.config import SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_BYTES
from backend.services.parser import parse_resume
from backend.services.scorer import score_resume
from pdfplumber.utils.exceptions import PdfminerException
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
    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty",
        )
    contents = resume.file.read(MAX_FILE_SIZE_BYTES + 1)
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Resume file exceeds the 5 MB size limit",
        )
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(contents)
        tmp_file_path = tmp_file.name
    try:
        try:
            resume_text = parse_resume(tmp_file_path)
        except (PdfminerException, ValueError, docx.opc.exceptions.PackageNotFoundError):
            raise HTTPException(
                status_code=400,
                detail="Unable to parse resume file. Please upload a valid PDF or DOCX file.",
            )
        result = score_resume(resume_text, job_description, DEFAULT_SKILLS_DB, required_years)
    finally:
        os.remove(tmp_file_path)
    return result