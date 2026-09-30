from backend.services.skill_evidence import (
    classify_skill_context,
    classify_evidence_type,
    classify_evidence_confidence,
)


def test_classify_strong_skill_context():
    sentence = "Built production APIs using FastAPI."

    assert classify_skill_context(sentence) == "strong"


def test_classify_learning_skill_context():
    sentence = "Currently learning Kubernetes."

    assert classify_skill_context(sentence) == "learning"


def test_classify_negative_skill_context():
    sentence = "No practical experience with AWS."

    assert classify_skill_context(sentence) == "negative"


def test_classify_weak_skill_context():
    sentence = "Familiar with Docker."

    assert classify_skill_context(sentence) == "weak"


def test_classify_project_evidence():
    sentence = "Developed a project using PyTorch."

    assert classify_evidence_type(sentence) == "project"


def test_classify_work_evidence():
    sentence = "Worked as a backend engineer using FastAPI."

    assert classify_evidence_type(sentence) == "work_experience"


def test_classify_education_evidence():
    sentence = "Completed university coursework in Machine Learning."

    assert classify_evidence_type(sentence) == "education"


def test_classify_certification_evidence():
    sentence = "Completed a certification in AWS."

    assert classify_evidence_type(sentence) == "certification"


def test_project_evidence_has_high_confidence():
    assert classify_evidence_confidence("project") == "high"


def test_work_evidence_has_high_confidence():
    assert classify_evidence_confidence("work_experience") == "high"


def test_education_evidence_has_medium_confidence():
    assert classify_evidence_confidence("education") == "medium"


def test_certification_evidence_has_medium_confidence():
    assert classify_evidence_confidence("certification") == "medium"


def test_generic_evidence_has_low_confidence():
    assert classify_evidence_confidence("generic") == "low"