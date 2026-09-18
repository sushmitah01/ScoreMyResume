import pytest
from unittest.mock import patch, MagicMock
from backend.services.scorer import( extract_keywords,
                                     extract_skills,
                                    keyword_match_score,
                                    semantic_similarity_score,
                                    generate_ai_feedback,
                                    formatting_score,
                                    has_phone_number)



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

SKILLS_DB=  ["Python", "Docker", "Kubernetes", "AWS", "REST API", "Java"] 

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

def test_extract_skills_ignores_partial_word_matches():
    text = "I built an awesome app using JavaScript and TypeScript."

    found = extract_skills(text, SKILLS_DB)

    assert "AWS" not in found
    assert "Java" not in found


def test_extract_keywords_filters_generic_filler_nouns():
    text = "Experience with Python is a plus. Strong communication skills and ability required."

    keywords = extract_keywords(text)

    assert "experience" not in keywords
    assert "plus" not in keywords
    assert "skill" not in keywords
    assert "ability" not in keywords
    assert "python" in keywords

def test_semantic_similarity_identical_text_score_high():
    text="An experienced backend engineer skilled in Python and cloud infrastructure"
    score= semantic_similarity_score(text,text)
    assert score>95.0

def test_semantic_similarity_paraphrased_text_scores_high():
    resume_text= "Built scalable web services using distributed systems"
    jd_text="Looking for someone who can develop distributed backend systems at scale."

    score= semantic_similarity_score(resume_text,jd_text)

    assert score >50.0

def test_semantic_similarity_unrelated_text_scores_low():
    resume_text = "Passionate home baker who loves making sourdough bread."
    jd_text = "Senior DevOps engineer needed for Kubernetes infrastructure management."
    score = semantic_similarity_score(resume_text, jd_text)
    assert score < 40.0

def test_semantic_similarity_returns_float_between_0_and_100():
    score = semantic_similarity_score("Python developer", "Software engineer")
    assert 0.0 <= score <= 100.0

def test_semantic_similarity_paraphrase_scores_higher_than_unrelated():
    paraphrase_score = semantic_similarity_score(
        "Built scalable web services using distributed systems.",
        "Looking for someone who can develop distributed backend systems at scale."
    )
    unrelated_score = semantic_similarity_score(
        "Passionate home baker who loves making sourdough bread.",
        "Senior DevOps engineer needed for Kubernetes infrastructure management."
    )
    assert paraphrase_score > unrelated_score

def test_generate_ai_feedback_returns_a_string():
    mock_response = MagicMock()
    mock_response.choices[0].message.content= "Solid resume. Consider highlighting Kubernetes experience."
    with patch("backend.services.scorer.client.chat.completions.create",return_value= mock_response):
        feedback= generate_ai_feedback(
            matched_keywords=["python", "docker"],
            missing_keywords=["kubernetes"],
            matched_skills=["Python", "Docker"],
            missing_skills=["kubernetes"],
            semantic_score= 72.5,
        )

    assert isinstance(feedback,str)
    assert len(feedback) >0

def test_generate_ai_feedback_missing_skill_in_prompt():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Some feedback text."

    with patch("backend.services.scorer.client.chat.completions.create", return_value=mock_response) as mock_create:
        generate_ai_feedback(
            matched_keywords=["python"],
            missing_keywords=[],
            matched_skills=["Python"],
            missing_skills=["Kubernetes"],
            semantic_score=80.0,
        )

    call_args = mock_create.call_args
    prompt_text = str(call_args)
    assert "Kubernetes" in prompt_text   

def test_generate_ai_feedback_returns_fallback_on_api_error():
    with patch("backend.services.scorer.client.chat.completions.create", side_effect=Exception("API down")):
        feedback = generate_ai_feedback(
            matched_keywords=["python"],
            missing_keywords=["docker"],
            matched_skills=["Python"],
            missing_skills=["Docker"],
            semantic_score=60.0,
        )

    assert isinstance(feedback, str)
    assert len(feedback) > 0

def test_formatting_score_full_marks_for_complete_resume():
    text=""" Nusrat Nodi
    nusrat.nodi@gmail.com | (555) 123-4567
    EXPERIENCE
    - Built scalable backend system
    - Led a team of 5 engineers

    EADUCATION
    -BS Computer Science

    SKILLS
    - Python, Docker, Kubernetes
    """
    score= formatting_score(text)
    assert score==100.0

def test_formatting_score_missing_email_loses_points():
    text="""
    Nowshin Nodi | (555) 123-4567
    EXPERIENCE
    - Built scalable backend system   

    EADUCATION
    -BS Computer Science 
    """

    score= formatting_score(text)
    assert score< 100.0

def test_formatting_score_no_structure_scores_low():
    text = "I am a hardworking person who wants a job and has done many things."
    score = formatting_score(text)
    assert score < 50.0  

def test_formatting_score_empty_text_returns_zero():
    assert formatting_score("") == 0.0  

def test_formatting_score_recognizes_international_phone_formats():
    us_text = "Contact: (555) 123-4567"
    uk_text = "Contact: +44 20 7946 0958"
    bd_text = "Contact: +880 1712-345678"
    india_text = "Contact: +91 98765 43210"
    australia_text = "Contact: +61 4 1234 5678"

    for text in [us_text, uk_text, bd_text, india_text, australia_text]:
        assert has_phone_number(text) is True

