from backend.services.skill_requirement import (
    classify_skill_requirement,
)


def test_required_skill():
    sentence = "Python experience is required."
    assert classify_skill_requirement(sentence) == "required"


def test_must_have_skill():
    sentence = "Candidates must have experience with FastAPI."
    assert classify_skill_requirement(sentence) == "required"


def test_preferred_skill():
    sentence = "Experience with Kubernetes is preferred."
    assert classify_skill_requirement(sentence) == "preferred"


def test_nice_to_have_skill():
    sentence = "AWS experience is nice to have."
    assert classify_skill_requirement(sentence) == "preferred"


def test_plus_skill():
    sentence = "Knowledge of Docker is a plus."
    assert classify_skill_requirement(sentence) == "preferred"


def test_unspecified_skill():
    sentence = "Experience with PostgreSQL."
    assert classify_skill_requirement(sentence) == "unspecified"


def test_required_takes_precedence():
    sentence = "Python is required, while AWS is preferred."
    assert classify_skill_requirement(sentence) == "required"

def test_not_required_skill():
    sentence = "Python is not required."
    assert classify_skill_requirement(sentence) == "unspecified"

def test_not_mandatory_skill():
    sentence = "AWS is not mandatory."
    assert classify_skill_requirement(sentence) == "unspecified"

def test_not_essential_skill():
    sentence = "Docker is not essential."
    assert classify_skill_requirement(sentence) == "unspecified"

def test_must_be_able_to():
    sentence = "Candidates must be able to work with Python."
    assert classify_skill_requirement(sentence) == "required"


def test_strongly_preferred():
    sentence = "Experience with AWS is strongly preferred."
    assert classify_skill_requirement(sentence) == "preferred"


def test_optional_skill():
    sentence = "Knowledge of Kubernetes is optional."
    assert classify_skill_requirement(sentence) == "preferred"


def test_ideal_candidate():
    sentence = "Python experience is desired for the ideal candidate."
    assert classify_skill_requirement(sentence) == "preferred"