
REQUIREMENT_WEIGHTS = {
    "required": 3.0,
    "preferred": 2.0,
    "unspecified": 1.0,
}


def get_requirement_weight(requirement_level):

    return REQUIREMENT_WEIGHTS[requirement_level]


def calculate_total_weight(requirements):
    
    return sum(
        get_requirement_weight(requirement_level)
        for requirement_level in requirements.values()
    )


def calculate_matched_weight(requirements, matched_skills):
    return sum(
        get_requirement_weight(requirements[skill])
        for skill in matched_skills
        if skill in requirements
    )


def calculate_missing_weight(requirements, matched_skills):
    return calculate_total_weight(requirements) - calculate_matched_weight(
        requirements,
        matched_skills,
    )


def calculate_weighted_match_percentage(requirements, matched_skills):

    total_weight = calculate_total_weight(requirements)

    if total_weight == 0:
        return 0.0

    matched_weight = calculate_matched_weight(
        requirements,
        matched_skills,
    )

    return round((matched_weight / total_weight) * 100, 1)

