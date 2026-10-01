from backend.services.skill_requirement import extract_skill_requirements


def test_required_skill_requirement():
    text = "Python experience is required."
    result = extract_skill_requirements(text)
    assert result["Python"] == "required"

def test_preferred_skill_requirement():
    text = "Experience with Kubernetes is preferred."
    result = extract_skill_requirements(text)
    assert result["Kubernetes"] == "preferred"

def test_unspecified_skill_requirement():
    text = "Experience with PostgreSQL."
    result = extract_skill_requirements(text)
    assert result["PostgreSQL"] == "unspecified"


def test_multiple_skill_requirements():
    text = (
        "Python and FastAPI experience are required. "
        "AWS knowledge is preferred."
    )

    result = extract_skill_requirements(text)

    assert result["Python"] == "required"
    assert result["FastAPI"] == "required"
    assert result["AWS"] == "preferred"


def test_requirement_belongs_to_specific_skill():
    text = (
        "Python experience is required. "
        "AWS experience is preferred."
    )

    result = extract_skill_requirements(text)

    assert result["Python"] == "required"
    assert result["AWS"] == "preferred"

def test_required_section():
    text = """
    Required Skills:
    - Python
    - FastAPI
    - Docker
    """
    result = extract_skill_requirements(text)
    assert result["Python"] == "required"
    assert result["FastAPI"] == "required"
    assert result["Docker"] == "required"


def test_preferred_section():
    text = """
    Preferred Skills:
    - AWS
    - Kubernetes
    """
    result = extract_skill_requirements(text)
    assert result["AWS"] == "preferred"
    assert result["Kubernetes"] == "preferred"


def test_required_and_preferred_sections():
    text = """
    Required:
    - Python
    - FastAPI
    Preferred:
    - AWS
    - Kubernetes
    """
    result = extract_skill_requirements(text)
    assert result["Python"] == "required"
    assert result["FastAPI"] == "required"
    assert result["AWS"] == "preferred"
    assert result["Kubernetes"] == "preferred"

def test_required_skills_heading():
    text = """
    Required Skills
    - Python
    - FastAPI
    """
    result = extract_skill_requirements(text)
    assert result["Python"] == "required"
    assert result["FastAPI"] == "required"


def test_must_have_skills_heading():
    text = """
    Must-Have Skills
    - Docker
    - Kubernetes
    """
    result = extract_skill_requirements(text)
    assert result["Docker"] == "required"
    assert result["Kubernetes"] == "required"


def test_minimum_qualifications_heading():
    text = """
    Minimum Qualifications
    - Python
    - PostgreSQL
    """

    result = extract_skill_requirements(text)
    assert result["Python"] == "required"
    assert result["PostgreSQL"] == "required"


def test_preferred_skills_heading():
    text = """
    Preferred Skills
    - AWS
    - Kubernetes
    """
    result = extract_skill_requirements(text)
    assert result["AWS"] == "preferred"
    assert result["Kubernetes"] == "preferred"

def test_nice_to_have_skills_heading():
    text = """
    Nice-to-Have Skills
    - Docker
    - AWS
    """
    result = extract_skill_requirements(text)
    assert result["Docker"] == "preferred"
    assert result["AWS"] == "preferred"