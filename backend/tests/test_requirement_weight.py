from backend.services.requirement_weight import (
    get_requirement_weight,
    calculate_total_weight,
    calculate_matched_weight,
    calculate_missing_weight,
    calculate_weighted_match_percentage,
)


def test_required_skill_has_highest_weight():
    assert get_requirement_weight("required") > get_requirement_weight("preferred")
    assert get_requirement_weight("required") > get_requirement_weight("unspecified")


def test_preferred_skill_has_medium_weight():
    assert get_requirement_weight("preferred") > get_requirement_weight("unspecified")


def test_unspecified_skill_has_baseline_weight():
    assert get_requirement_weight("unspecified") > 0


def test_requirement_weight_is_deterministic():
    assert get_requirement_weight("required") == get_requirement_weight("required")
    assert get_requirement_weight("preferred") == get_requirement_weight("preferred")
    assert get_requirement_weight("unspecified") == get_requirement_weight("unspecified")


def test_total_requirement_weight():
    requirements = {
        "Python": "required",
        "FastAPI": "required",
        "AWS": "preferred",
    }

    assert calculate_total_weight(requirements) == 8.0


def test_matched_requirement_weight():
    requirements = {
        "Python": "required",
        "FastAPI": "required",
        "AWS": "preferred",
    }

    matched = {"Python", "AWS"}

    assert calculate_matched_weight(requirements, matched) == 5.0


def test_missing_requirement_weight():
    requirements = {
        "Python": "required",
        "FastAPI": "required",
        "AWS": "preferred",
    }

    matched = {"Python", "AWS"}
    assert calculate_missing_weight(requirements, matched) == 3.0


def test_weighted_match_percentage():
    requirements = {
        "Python": "required",
        "FastAPI": "required",
        "AWS": "preferred",
    }
    matched = {"Python", "AWS"}
    assert calculate_weighted_match_percentage(
        requirements,
        matched,
    ) == 62.5


""" edge cases """

def test_empty_requirements_have_zero_total_weight():
    requirements = {}
    assert calculate_total_weight(requirements) == 0.0


def test_no_matched_skills_have_zero_matched_weight():
    requirements = {
        "Python": "required",
        "FastAPI": "preferred",
    }
    matched = set()
    assert calculate_matched_weight(requirements, matched) == 0.0


def test_no_matched_skills_have_full_missing_weight():
    requirements = {
        "Python": "required",
        "FastAPI": "preferred",
    }
    matched = set()
    assert calculate_missing_weight(requirements, matched) == 5.0


def test_all_skills_matched_have_100_percent_weighted_match():
    requirements = {
        "Python": "required",
        "FastAPI": "preferred",
    }
    matched = {"Python", "FastAPI"}
    assert calculate_weighted_match_percentage(
        requirements,
        matched,
    ) == 100.0


def test_empty_requirements_have_zero_weighted_match_percentage():
    requirements = {}
    matched = set()
    assert calculate_weighted_match_percentage(
        requirements,
        matched,
    ) == 0.0


def test_unknown_matched_skill_does_not_affect_weight():
    requirements = {
        "Python": "required",
        "FastAPI": "preferred",
    }
    matched = {"Python", "Docker"}
    assert calculate_matched_weight(requirements, matched) == 3.0


def test_invalid_requirement_level_raises_error():
    requirements = {
        "Python": "mandatory",
    }
    try:
        calculate_total_weight(requirements)
    except KeyError:
        pass
    else:
        raise AssertionError("Expected KeyError for invalid requirement level")





