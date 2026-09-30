from backend.services.skill_extractor import find_skill_matches
from backend.services.skill_evidence import extract_skill_evidence

def extract_skill_set(text):
    """Extract canonical skills from text and return them as a set."""
    matches = find_skill_matches(text)
    return {
        canonical_skill
        for canonical_skill, _, _ in matches
    }

def analyze_skill_gap(resume, job_description):
    """Compare resume skills against skills required by a job description.
    Returns:
        {
            "strong_matched": [...],
            "weak_match": [...],
            "missing": [...],
            "extra": [...]
        }
    """
    resume_skills = extract_skill_set(resume)
    job_skills = extract_skill_set(job_description)
    resume_evidence = extract_skill_evidence(resume)
    strong_match = set()
    weak_match = set()  
    
    for skill in resume_skills & job_skills:
        evidence = resume_evidence.get(skill, {})
        context = evidence.get("context")
        if context == "negative":
            continue
        if context in {"learning", "weak"}:
            weak_match.add(skill)
        else:
            strong_match.add(skill)

    missing = (
        job_skills
        - strong_match
        - weak_match
    )
    extra = resume_skills - job_skills
    matched = strong_match | weak_match
    return {
        "matched": sorted(matched),
        "strong_match": sorted(strong_match),
        "weak_match": sorted(weak_match),
        "missing": sorted(missing),
        "extra": sorted(extra),
    }