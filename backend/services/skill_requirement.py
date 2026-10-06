import re
from backend.services.skill_extractor import find_skill_matches
from backend.services.skill_extractor import nlp

def classify_skill_requirement(sentence):
    """how important a skill is in a job description.
    Returns:
        required
        preferred
        unspecified"""
    sentence_lower = sentence.lower()

    negated_required_patterns = [
        r"\bnot\s+required\b",
        r"\bnot\s+mandatory\b",
        r"\bnot\s+essential\b",
    ]

    for pattern in negated_required_patterns:
        if re.search(pattern, sentence_lower):
            return "unspecified"

    required_patterns = [
        r"\brequired\b",
        r"\brequires\b",
        r"\brequire\b",
        r"\bmust have\b",
        r"\bmust-have\b",
        r"\bmandatory\b",
        r"\bessential\b",
        r"\bmust be able to\b",
    ]

    preferred_patterns = [
        r"\bpreferred\b",
        r"\bprefer\b",
        r"\bnice to have\b",
        r"\bnice-to-have\b",
        r"\bplus\b",
        r"\bbonus\b",
        r"\bdesired\b",
        r"\bpreferred qualification\b",
        r"\boptional\b"
    ]

    for pattern in required_patterns:
        if re.search(pattern, sentence_lower):
            return "required"

    for pattern in preferred_patterns:
        if re.search(pattern, sentence_lower):
            return "preferred"
    return "unspecified"

def extract_skill_requirement_details(job_description,skills_db=None):
    """
    to extract skills from a job description and level them accordingly.

    Returns:
        {
            "Python": {"level": "required",
            "sentence": "Experience with Python is required."}
        }
    """
    if not job_description:
        return {}
    requirements = {}
    matches = find_skill_matches(job_description, skills_db)
    doc = nlp(job_description)
    lines = job_description.splitlines()
    required_section_patterns = [
        r"\brequired\b",
        r"\bmust[- ]have\b",
        r"\bmandatory\b",
        r"\bessential\b",
        r"\bminimum qualifications?\b",
        r"\bbasic qualifications?\b",
    ]

    preferred_section_patterns = [
        r"\bpreferred\b",
        r"\bnice[- ]to[- ]have\b",
        r"\boptional\b",
        r"\bdesired\b",
    ]

    for canonical_skill, start, end in matches:
        skill_span = doc[start:end]
        skill_line_index = None
        for index, line in enumerate(lines):
            line_start = sum(len(item) + 1 for item in lines[:index])
            line_end = line_start + len(line)

            if line_start <= skill_span.start_char < line_end:
                skill_line_index = index
                break

        if skill_line_index is None:
            requirements[canonical_skill] = { "level":"unspecified",
                                             "sentence": skill_span.sent.text.strip(),}
            continue

        skill_line = lines[skill_line_index].strip()
        semantic_sentence = re.sub(r"^[-*]\s+", "", skill_line)
        is_bullet = (
            skill_line.startswith("- ")
            or skill_line.startswith("* ")
        )

        if not is_bullet:
            sentence = skill_span.sent.text.strip()
            sentence_requirement = classify_skill_requirement(sentence)
            if sentence_requirement != "unspecified":
                requirements[canonical_skill] = {"level":sentence_requirement,
                                                 "sentence": sentence,}
                continue
        section_requirement = "unspecified"
        for index in range(skill_line_index - 1, -1, -1):
            header = lines[index].strip().lower()

            if not header:
                continue
            if header.startswith("- ") or header.startswith("* "):
                continue

            if any(
                re.search(pattern, header)
                for pattern in required_section_patterns
            ):
                section_requirement = "required"
                break
            if any(
                re.search(pattern, header)
                for pattern in preferred_section_patterns
            ):
                section_requirement = "preferred"
                break
        requirements[canonical_skill] = {"level":section_requirement,
                                           "sentence": semantic_sentence,
}
    return requirements


def extract_skill_requirements(job_description, skills_db=None):
    details = extract_skill_requirement_details(job_description, skills_db)

    return {
        skill: data["level"]
        for skill, data in details.items()
    }