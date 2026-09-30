from backend.services.skill_gap import analyze_skill_gap

def test_strong_evidence_is_strong_match():
    resume = """ Built production APIs using FastAPI. """
    job_description = """
    We require FastAPI experience.
    """
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "FastAPI" in result["strong_match"]
    assert "FastAPI" not in result["weak_match"]
    assert "FastAPI" not in result["missing"]


def test_learning_skill_is_weak_match():
    resume = """
    Currently learning Kubernetes.
    """
    job_description = """
    Kubernetes experience is required.
    """
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "Kubernetes" in result["weak_match"]
    assert "Kubernetes" not in result["strong_match"]
    assert "Kubernetes" not in result["missing"]

def test_negative_skill_is_not_a_match():
    resume = """
    No practical experience with AWS.
    """
    job_description = """
    AWS experience is required.
    """
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "AWS" in result["missing"]
    assert "AWS" not in result["strong_match"]
    assert "AWS" not in result["weak_match"]


def test_education_is_weak_match():
    resume = """
    Completed university coursework in Machine Learning.
    """
    job_description = """
    Machine Learning experience required.
    """
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "Machine Learning" in result["weak_match"]
def test_project_experience_is_strong_match():
    resume = """Developed a project using PyTorch for image classification."""
    job_description = """PyTorch experience required."""
    result = analyze_skill_gap(
        resume,
        job_description
    )
    assert "PyTorch" in result["strong_match"]