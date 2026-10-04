from backend.services.skill_gap import analyze_skill_gap


def test_required_and_preferred_missing_skills_are_separated():
    resume = """
    Python experience.
    AWS experience.
    """
    job_description = """
    Required Skills:
    - Python
    - FastAPI

    Preferred Skills:
    - AWS
    - Kubernetes
    """

    result = analyze_skill_gap(resume, job_description)

    assert result["required_missing"] == ["FastAPI"]
    assert result["preferred_missing"] == ["Kubernetes"]


def test_required_skill_present_is_not_missing():
    resume = """
    Python experience.
    FastAPI project experience.
    """

    job_description = """
    Required Skills:
    - Python
    - FastAPI

    Preferred Skills:
    - AWS
    """

    result = analyze_skill_gap(resume, job_description)

    assert result["required_missing"] == []
    assert result["preferred_missing"] == ["AWS"]


def test_unspecified_skills_are_not_required_missing():
    resume = """
    Python experience.
    """

    job_description = """
    Python experience.
    PostgreSQL experience.
    """

    result = analyze_skill_gap(resume, job_description)

    assert result["required_missing"] == []
    assert result["preferred_missing"] == []


def test_existing_gap_api_is_preserved():
    resume = """
    Python experience.
    """

    job_description = """
    Required Skills:
    - Python
    - FastAPI

    Preferred Skills:
    - AWS
    """

    result = analyze_skill_gap(resume, job_description)

    assert "matched" in result
    assert "strong_match" in result
    assert "weak_match" in result
    assert "missing" in result
    assert "extra" in result

    assert result["matched"] == ["Python"]
    assert result["strong_match"] == ["Python"]
    assert result["weak_match"] == []
    assert result["missing"] == ["AWS", "FastAPI"]
    assert result["extra"] == []


def test_preferred_and_required_skills_use_canonical_names():
    resume = """
    Python experience.
    """
    job_description = """
    Required Skills:
    - Python
    - FastAPI
    Preferred Skills:
    - Kubernetes
    """

    result = analyze_skill_gap(resume, job_description)
    assert result["required_missing"] == ["FastAPI"]
    assert result["preferred_missing"] == ["Kubernetes"]


def test_skill_gap_calculates_requirement_weight():
    resume = """
    I have experience with Python and AWS.
    """
    job_description = """
    Required:
    - Python
    - FastAPI

    Preferred:
    - AWS
    """
    result = analyze_skill_gap(
        resume,
        job_description,
    )

    assert result["matched"] == ["AWS", "Python"]
    assert result["missing"] == ["FastAPI"]
    assert result["total_requirement_weight"] == 8.0
    assert result["matched_requirement_weight"] == 5.0
    assert result["missing_requirement_weight"] == 3.0
    assert result["weighted_match_percentage"] == 62.5 