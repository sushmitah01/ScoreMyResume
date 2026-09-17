import pytest
from backend.services.scorer import( extract_keywords, extract_skills, keyword_match_score)



def test_extract_keywords_filters_stop_words():
    text= "The candidate managed a team of engineers."
    keywords= extract_keywords(text)
    assert "the" not in keywords
    assert "of" not in keywords
    assert "a" not in keywords


def test_extract_keywords_returns_lemmaized_nouns():
    text= "Managing databases and building APIs"

    keywords = extract_keywords(text)

    assert "database" in keywords

def test_extract_keywords_empty_string_returns_empty_list():
    assert extract_keywords("")==[]

SKILLS_DB=  ["Python", "Docker", "Kubernetes", "AWS", "REST API"] 

def test_extract_skills_finds_exact_match():
    text= "I have 3 years of experience with Python and Docker."

    found= extract_skills(text, SKILLS_DB)
    assert "Python" in found
    assert "Docker" in found

def test_extract_skills_no_false_positives():
    text= "I enjoy drawing and gardening"

    found = extract_skills(text, SKILLS_DB)
    assert found == []

def test_extract_skills_matches_multiword_phrase():
    text= "Built a REST API for the payments team"

    found= extract_skills(text, SKILLS_DB)
    assert "REST API" in found

def test_keyword_match_score_full_overlap():
    resume_kw = ["python", "docker", "team"]
    jd_kw = ["python", "docker", "team"]
    assert keyword_match_score(resume_kw, jd_kw) == 100.0

def test_keyword_match_score_no_overlap():
    resume_kw = ["cooking", "hiking"]

    jd_kw = ["python", "docker"]
    assert keyword_match_score(resume_kw, jd_kw) == 0.0

def test_keyword_match_score_partial_overlap():
    resume_kw = ["python", "cooking"]
    jd_kw = ["python", "docker"]
    # 1 of 2 JD keywords matched -> 50%
    assert keyword_match_score(resume_kw, jd_kw) == 50.0

def test_keyword_match_score_empty_jd_keywords_returns_zero():
    assert keyword_match_score(["python"], []) == 0.0