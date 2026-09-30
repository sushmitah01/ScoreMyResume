from backend.services.skill_gap import analyze_skill_gap


def test_skill_gap_finds_missing_skills():
    resume = """Built APIs using Python and FastAPI. Used PostgreSQL and Docker in projects.
    """
    job_description = """We are looking for Python, FastAPI, PostgreSQL,Docker, Kubernetes, and AWS experience."""
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "Python" in result["matched"]
    assert "FastAPI" in result["matched"]
    assert "PostgreSQL" in result["matched"]
    assert "Docker" in result["matched"]

    assert "Kubernetes" in result["missing"]
    assert "AWS" in result["missing"]


def test_skill_gap_returns_empty_missing_when_all_skills_match():
    resume = """
    Experienced with Python, FastAPI, PostgreSQL and Docker.
    """

    job_description = """Required skills: Python, FastAPI, PostgreSQL and Docker."""
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert result["missing"] == []


def test_skill_gap_canonicalizes_aliases():
    resume = """Built backend services using Python, K8s and Postgres."""
    job_description = """
    Required: Python, Kubernetes and PostgreSQL.
    """
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "Kubernetes" in result["matched"]
    assert "PostgreSQL" in result["matched"]
    assert result["missing"] == []


def test_skill_gap_detects_extra_resume_skills():
    resume = """Worked with Python, FastAPI, Docker and Redis."""
    job_description = """Required skills: Python, FastAPI and Docker."""
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "Redis" in result["extra"]