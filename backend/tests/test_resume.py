import pytest
import docx
from fpdf import FPDF
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import create_access_token

client = TestClient(app)


@pytest.fixture
def auth_headers():
    token = create_access_token({"user_id": "test-user-123", "email": "test@example.com"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_resume_pdf(tmp_path):
    pdf_path = tmp_path / "resume.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="Jane Doe - Python developer with 5 years of experience using Docker and AWS.")
    pdf.output(str(pdf_path))
    return str(pdf_path)


def test_score_endpoint_rejects_missing_auth(sample_resume_pdf):
    with open(sample_resume_pdf, "rb") as f:
        response = client.post(
            "/resume/score",
            files={"resume": ("resume.pdf", f, "application/pdf")},
            data={"job_description": "Looking for a Python developer with 3+ years experience."},
        )
    assert response.status_code == 401


def test_score_endpoint_returns_score_with_valid_auth(sample_resume_pdf, auth_headers):
    with open(sample_resume_pdf, "rb") as f:
        response = client.post(
            "/resume/score",
            files={"resume": ("resume.pdf", f, "application/pdf")},
            data={"job_description": "Looking for a Python developer with 3+ years experience in Docker."},
            headers=auth_headers,
        )
    assert response.status_code == 200
    body = response.json()
    assert "overall_score" in body
    assert "breakdown" in body


def test_score_endpoint_rejects_unsupported_file_type(auth_headers, tmp_path):
    txt_path = tmp_path / "resume.txt"
    txt_path.write_text("plain text resume")

    with open(txt_path, "rb") as f:
        response = client.post(
            "/resume/score",
            files={"resume": ("resume.txt", f, "text/plain")},
            data={"job_description": "Looking for a Python developer with 3+ years experience."},
            headers=auth_headers,
        )
    assert response.status_code == 400