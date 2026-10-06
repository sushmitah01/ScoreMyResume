from backend.services.skill_extractor import find_skill_matches
from backend.services.skill_evidence import extract_skill_evidence
from backend.services.skill_requirement import extract_skill_requirements
from backend.services.semantic_matcher import (
    find_best_matching_sentence,
    find_semantic_evidence,
    SEMANTIC_EVIDENCE_THRESHOLD,
)

from backend.services.requirement_weight import (
    calculate_total_weight,
    calculate_matched_weight,
    calculate_missing_weight,
    calculate_weighted_match_percentage,
)
def extract_skill_set(text,skills_db=None):
    """Extract canonical skills from text and return them as a set."""
    matches = find_skill_matches(text, skills_db)
    return {
        canonical_skill
        for canonical_skill, _, _ in matches
    }

def analyze_skill_gap(resume, job_description, skills_db=None):
    """Compare resume skills against skills required by a job description.
    Returns:
        {
            "strong_match": [...],
            "weak_match": [...],
            "missing": [...],
            "extra": [...],
            "total_requirement_weight": float, 
            "matched_requirement_weight": float, 
            "missing_requirement_weight": float, 
            "weighted_match_percentage": float,
        }
    """
    resume_skills = extract_skill_set(resume,skills_db)
    job_skills = extract_skill_set(job_description,skills_db)
    resume_evidence = extract_skill_evidence(resume)
    job_requirements = {skill:requirement_level
                        for skill, requirement_level in extract_skill_requirements(job_description).items()
                        if skill in job_skills}
    semantic_evidence = {}
    for skill in skills_db or []:
        requirement_result = find_best_matching_sentence(
            skill,
            job_description,
        )
        if requirement_result["score"] < SEMANTIC_EVIDENCE_THRESHOLD:
            continue

        requirement_sentence = requirement_result["sentence"]

        resume_result = find_semantic_evidence(
            requirement_sentence,
            resume,
        )

        if resume_result["is_match"]:
            semantic_evidence[skill] = {
                "sentence": resume_result["sentence"],
                "score": resume_result["score"],
                "is_match": resume_result["is_match"],
                "requirement_sentence": requirement_sentence,
                "requirement_score": requirement_result["score"],
            }
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
    total_requirement_weight = calculate_total_weight(
        job_requirements
    )

    matched_requirement_weight = calculate_matched_weight(
        job_requirements,
        matched
    )

    missing_requirement_weight = calculate_missing_weight(
        job_requirements,
        matched
    )

    weighted_match_percentage = calculate_weighted_match_percentage(
        job_requirements,
        matched
    )    
    required_missing = {
        skill
        for skill in missing
        if job_requirements.get(skill) == "required"
    }
    preferred_missing = {
        skill
        for skill in missing
        if job_requirements.get(skill) == "preferred"
}
    return {
        "semantic_evidence": semantic_evidence,
        "matched": sorted(matched),
        "strong_match": sorted(strong_match),
        "weak_match": sorted(weak_match),
        "missing": sorted(missing),
        "required_missing": sorted(required_missing),
        "preferred_missing": sorted(preferred_missing),
        "extra": sorted(extra),
        "total_requirement_weight": total_requirement_weight, 
        "matched_requirement_weight": matched_requirement_weight,
        "missing_requirement_weight": missing_requirement_weight,
        "weighted_match_percentage": weighted_match_percentage,        
    }