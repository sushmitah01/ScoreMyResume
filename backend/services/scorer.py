import re
from groq import Groq
from backend.core.config import GROQ_API_KEY, GROQ_MODEL, SCORE_WEIGHTS
from backend.services.skill_taxonomy import SKILL_ALIAS_MAP
from backend.services.skill_extractor import find_skill_matches, nlp
from backend.services.skill_evidence import (
    classify_skill_context,
    classify_evidence_type,
    classify_evidence_confidence,
    extract_skill_evidence
)
from backend.services.skill_gap import analyze_skill_gap
from backend.services.semantic_matcher import semantic_similarity_score

def calculate_overall_score(breakdown):
    total = 0.0
    for component, weight in SCORE_WEIGHTS.items():
        total += breakdown[component] * (weight / 100)
    return round(total, 1)

client = Groq(api_key=GROQ_API_KEY)

GENERIC_FILLER_WORDS = {
    "experience","skill",
    "skills","ability","abilities","plus","environment","requirement","requirements","responsibility","responsibilities","candidate",
    "role","team","work","working","company","organization",
    "organizations", "career", "job","position","employee","employer","business","industry","field","method","methods","process","processes","practice","practices","service","services","support","quality",
    "problem","problems","need","needs","level","knowledge","understanding","expertise",
    "development","application","applications","information","description","deliverable","deliverables","performance",
    "technique","techniques","procedure","procedures","component","components",
    "object","objects","query", "queries","data","code","product","products","organization","organizations",
}

JD_BOILERPLATE_WORDS = {
    "monday","tuesday","wednesday","thursday","friday","saturday","sunday","salary","bonus",
    "bonuses","benefit","benefits","holiday","holidays","leave","opportunity","office","week","weekly","annual",
    "annually","yearly","compensation","review","workplace","location","site","day","recognition","wellness","outing",
    "premises","deadline",
}

JOB_ROLE_WORDS = {
    "engineer","engineers","developer","developers","programmer","programmers",
    "architect","architects","manager","managers","designer","designers","analyst",
    "analysts","intern","interns","professional","professionals",
}
KNOWN_LOCATION_WORDS = {
    "dhaka","panthapath","bangladesh","uttam","sarak","bd",
}
KNOWN_PERSON_NAMES = {
    "nuruzzaman",
    "qazi",
}

RESUME_METADATA_WORDS = {
    "year","years","bsc","msc","phd","contact","address","phone","email",
}

EXCLUDED_ENTITY_TYPES = {
    "PERSON","GPE","LOC","FAC","DATE","TIME","MONEY","CARDINAL","ORDINAL","PERCENT",
}

def extract_keywords(text):
    if not text:
        return []


    doc = nlp(text)
    keywords=set()

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        if token.ent_type_ in EXCLUDED_ENTITY_TYPES:
            continue
        lemma = token.lemma_.lower().strip()
        if not lemma:
            continue
        if lemma in KNOWN_LOCATION_WORDS:
            continue
        if lemma in KNOWN_PERSON_NAMES:
            continue
        if lemma in GENERIC_FILLER_WORDS:
            continue
        if lemma in JD_BOILERPLATE_WORDS:
            continue
        if lemma in JOB_ROLE_WORDS:
            continue
        if lemma in RESUME_METADATA_WORDS:
            continue
        if token.pos_ not in {"NOUN", "PROPN"}:
            continue
        keywords.add(lemma)
        

    return sorted(keywords)

def extract_skills(text, skills_db= None):

    if not text :
        return []

    matches= find_skill_matches(text,skills_db)
    return sorted({
        canonical_skill for canonical_skill, _, _ in matches})



def keyword_match_score(resume_keywords, jd_keywords):
    if not jd_keywords:
        return 0.0

    resume_set= set(resume_keywords)
    jd_set=set(jd_keywords)

    matched= resume_set & jd_set
    score= (len(matched)/ len(jd_set))* 100

    return round(score,1)



def generate_ai_feedback(matched_keywords, missing_keywords, matched_skills, missing_skills, semantic_score):
    prompt= f"""You are a resume coach. Based on this  ATS scoring data,write 2-3 sentences of constructive feedback for the candidate. 
Matched keywords: {', '.join(matched_keywords) if matched_keywords else 'none'}
Missing keywords: {', '.join(missing_keywords) if missing_keywords else 'none'}
Matched skills: {', '.join(matched_skills) if matched_skills else 'none'}
Missing skills: {', '.join(missing_skills) if missing_skills else 'none'}
Semantic similarity score: {semantic_score}/100

Keep it encouraging but specific about what to improve."""
    try:
        response= client.chat.completions.create(
            model= GROQ_MODEL,
        messages=[{"role":"user", "content":prompt}],

        )
        return response.choices[0].message.content
    except Exception:
        return "We couldn't generate personalized AI feedback right now, but your score breakdown above still reflects your resume's match this job description."


SECTION_HEADERS = ["experience", "education", "skills", "projects", "summary"]
def has_phone_number(text):
    candidates = re.findall(r"\+?[\d][\d\-.\s()]{6,}\d", text)

    for candidate in candidates:
        digits_only = re.sub(r"\D", "", candidate)
        if 7 <= len(digits_only) <= 15:
            return True

    return False

def formatting_score(text):
    if text.strip()=="":
        return 0.0

    score=0.0
    lower_text= text.lower()

    has_email= bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+",text))
    if has_email:
        score +=25

    if has_phone_number(text):
        score+=25
    
    headers_found= [h for h in SECTION_HEADERS if h in lower_text]  
    if len(headers_found) >= 2:
        score += 25

    has_bullets = bool(re.search(r"^\s*[-•]", text, re.MULTILINE))
    if has_bullets:
        score += 25

    return round(score, 1)


def extract_years_of_experience(text):
    matches = re.findall(r"(\d+)\+?\s*years?", text, re.IGNORECASE)

    if not matches:
        return 0

    years= [int(m) for m in matches]
    return max(years)

def experience_score(resume_years, required_years):
    if required_years == 0:
        return 100.0

    if resume_years >= required_years:
        return 100.0

    score = (resume_years / required_years) * 100
    return round(score, 1)

def score_resume(resume_text, jd_text, skills_db, required_years):
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    # resume_skills = extract_skills(resume_text, skills_db)
    # jd_skills = extract_skills(jd_text, skills_db)

    matched_keywords = sorted(set(resume_keywords) & set(jd_keywords))
    missing_keywords = sorted(set(jd_keywords) - set(resume_keywords))
    skill_gap = analyze_skill_gap(resume_text, jd_text,skills_db)
    matched_skills = skill_gap["matched"]
    missing_skills = skill_gap["missing"]

    keywords_score = keyword_match_score(resume_keywords, jd_keywords)
    semantic_score = semantic_similarity_score(resume_text, jd_text)

    skills_score = skill_gap["weighted_match_percentage"]

    format_score = formatting_score(resume_text)

    resume_years = extract_years_of_experience(resume_text)
    exp_score = experience_score(resume_years, required_years)

    breakdown = {
        "keywords": keywords_score,
        "semantic": semantic_score,
        "skills": skills_score,
        "formatting": format_score,
        "experience": exp_score,
    }

    overall = calculate_overall_score(breakdown)

    ai_feedback = generate_ai_feedback(
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        semantic_score=semantic_score,
    )

    return {
        "overall_score": overall,
        "breakdown": breakdown,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_missing": skill_gap["required_missing"],
        "preferred_missing": skill_gap["preferred_missing"],
        "total_requirement_weight": skill_gap["total_requirement_weight"],
        "matched_requirement_weight": skill_gap["matched_requirement_weight"],
        "missing_requirement_weight": skill_gap["missing_requirement_weight"],
        "weighted_match_percentage": skill_gap["weighted_match_percentage"],
        "ai_feedback": ai_feedback,
    }