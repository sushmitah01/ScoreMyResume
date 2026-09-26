import pytest
from unittest.mock import patch, MagicMock
from backend.services.scorer import( extract_keywords,
                                     extract_skills,
                                    keyword_match_score,
                                    semantic_similarity_score,
                                    generate_ai_feedback,
                                    formatting_score,
                                    has_phone_number,
                                    experience_score,
                                    extract_years_of_experience,
                                    score_resume,
                                    extract_skill_evidence)

from backend.services.skill_taxonomy import (
                                    SKILL_TAXONOMY,
                                    SKILL_ALIAS_MAP)

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

def test_extract_keywords_ignores_locations():
    text = """
    We are looking for a software engineer in Dhaka,
    Panthapath, Bangladesh.
    """
    keywords = extract_keywords(text)
    assert "dhaka" not in keywords
    assert "panthapath" not in keywords
    assert "bangladesh" not in keywords

def test_extract_keywords_ignores_person_names():
    text = """
    Contact Nuruzzaman Qazi for more information.
    """
    keywords = extract_keywords(text)
    assert "nuruzzaman" not in keywords
    assert "qazi" not in keywords

def test_extract_keywords_ignores_job_roles():
    text = """
    We are looking for a software engineer
    and backend developer.
    """
    keywords = extract_keywords(text)
    assert "engineer" not in keywords
    assert "developer" not in keywords
def test_extract_keywords_ignores_generic_business_words():
    text = """
    The employee will work with the company to solve
    business problems and improve quality.
    """
    keywords = extract_keywords(text)
    assert "employee" not in keywords
    assert "work" not in keywords
    assert "company" not in keywords
    assert "business" not in keywords
    assert "problem" not in keywords
    assert "quality" not in keywords

def test_extract_keywords_keeps_useful_technical_concepts():
    text = """
    Experience with database architecture, debugging,
    deployment, and microservices.
    """
    keywords = extract_keywords(text)
    assert "database" in keywords
    assert "architecture" in keywords
    assert "debugging" in keywords
    assert "deployment" in keywords
    assert "microservice" in keywords

def test_extract_keywords_filters_generic_filler_nouns():
    text = "Experience with Python is a plus. Strong communication skills and ability required."

    keywords = extract_keywords(text)

    assert "experience" not in keywords
    assert "plus" not in keywords
    assert "skill" not in keywords
    assert "ability" not in keywords
    assert "python" in keywords

def test_extract_keywords_removes_real_world_resume_noise():
    text = """
    Power Dapper proficiency engineer sick Qazi nature passion
    heights awards year ADO.NET quality media Nuruzzaman problem
    field understanding additional expertise architecture employee
    development data support BSc responsibilities services industry
    OOP database telecommunication debugging procedure career
    designing course festival testing communication deliverable
    west company work code million summary web microservice yearly
    server view pressure organization requirements ASP.NET product
    Uttam job application async Panthapath description software
    deadline service hand object process practice LINQ deployment issue
    component BD Sarak Dhaka-1205 information query business.
    """

    keywords = extract_keywords(text)

    forbidden = {
        "engineer","qazi","nuruzzaman","employee","company","work","career",
        "job","application","deadline","dhaka","panthapath","bd","year",
        "yearly","bsc","business","information","description","responsibilities",
    }

    assert not forbidden.intersection(keywords)

def test_extract_skills_finds_real_technical_terms():
    text = """
    Experience with ADO.NET, ASP.NET, OOP, LINQ,
    databases, debugging and microservices.
    """

    skills_db = [
        "ADO.NET","ASP.NET","OOP","LINQ","Database","Debugging","Microservices",
    ]

    found = extract_skills(text, skills_db)

    assert "ADO.NET" in found
    assert "ASP.NET" in found
    assert "Object-Oriented Programming" in found
    assert "LINQ" in found
def test_extract_keywords_filters_jd_boilerplate():
    text = """
    We offer competitive salary and annual bonuses. Weekly holidays are
    Friday and Saturday. This is a great opportunity to join our team
    and work with PostgreSQL and MongoDB in a collaborative office environment.
    """

    keywords = extract_keywords(text)

    assert "friday" not in keywords
    assert "saturday" not in keywords
    assert "bonus" not in keywords
    assert "salary" not in keywords
    assert "opportunity" not in keywords
    assert "office" not in keywords
    assert "postgresql" in keywords
    assert "mongodb" in keywords

def test_extract_keywords_returns_sorted_unique_keywords():
    text = """
    Python databases databases Docker systems systems
    """
    keywords = extract_keywords(text)
    assert keywords == sorted(set(keywords))

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
#ai feedback using groq mock test
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
#formatting
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

#expeience
def test_extract_years_of_experience_finds_simple_number():
    text = "I have 5 years of experience in backend development."
    assert extract_years_of_experience(text) == 5


def test_extract_years_of_experience_finds_plus_notation():
    text = "Looking for someone with 7+ years of experience."
    assert extract_years_of_experience(text) == 7


def test_extract_years_of_experience_takes_maximum_when_multiple_mentions():
    text = "3 years at Company A, followed by 6 years at Company B."
    assert extract_years_of_experience(text) == 6


def test_extract_years_of_experience_returns_zero_when_not_mentioned():
    text = "Skilled backend engineer with strong Python knowledge."
    assert extract_years_of_experience(text) == 0

def test_experience_score_meets_requirement_scores_full():
    assert experience_score(resume_years=6, required_years=5) == 100.0

def test_experience_score_exact_match_scores_full():
    assert experience_score(resume_years=5, required_years=5) == 100.0

def test_experience_score_under_requirement_scores_proportionally():
    assert experience_score(resume_years=3, required_years=5) == 60.0

def test_experience_score_zero_required_years_scores_full():
    assert experience_score(resume_years=2, required_years=0) == 100.0


def test_score_resume_returns_all_expected_keys():
    resume_text = """
    Nusrat Nodi
    nusrat.nodi@gmail.com | (555) 123-4567

    EXPERIENCE
    - 5 years of experience building Python backend systems with Docker

    SKILLS
    - Python, Docker, AWS
    """
    jd_text = "Looking for a backend engineer with Python and Docker experience. 3+ years required."
    skills_db = ["Python", "Docker", "Kubernetes", "AWS"]

    result = score_resume(resume_text, jd_text, skills_db, required_years=3)

    expected_keys = {
        "overall_score", "breakdown", "matched_keywords", "missing_keywords",
        "matched_skills", "missing_skills", "ai_feedback",
    }
    assert expected_keys.issubset(result.keys())


def test_score_resume_overall_score_is_weighted_average():
    resume_text = "Python Docker AWS experience"
    jd_text = "Python Docker AWS experience"
    skills_db = ["Python", "Docker", "AWS"]

    result = score_resume(resume_text, jd_text, skills_db, required_years=0)

    assert 0.0 <= result["overall_score"] <= 100.0


def test_score_resume_breakdown_matches_score_weights_keys():
    resume_text = "Python developer"
    jd_text = "Python developer needed"
    skills_db = ["Python"]

    result = score_resume(resume_text, jd_text, skills_db, required_years=0)

    assert set(result["breakdown"].keys()) == {
        "keywords", "semantic", "skills", "formatting", "experience"
    }


def test_score_resume_missing_skills_reflects_jd_gap():
    resume_text = "I know Python well."
    jd_text = "Must have Python and Kubernetes experience."
    skills_db = ["Python", "Kubernetes"]

    result = score_resume(resume_text, jd_text, skills_db, required_years=0)

    assert "Kubernetes" in result["missing_skills"]
    assert "Python" not in result["missing_skills"]


#SKILL MATCH TEST 

def test_skill_aliases_are_canonicalized():
    text = """
    Experience with Python, K8s, Postgres,
    RESTful APIs, ML and NLP.
    """
    skills = extract_skills(text)
    assert "Python" in skills
    assert "Kubernetes" in skills
    assert "PostgreSQL" in skills
    assert "REST API" in skills
    assert "Machine Learning" in skills
    assert "Natural Language Processing" in skills
#TEST JAVA as Javascript
def test_java_and_javascript_are_distinct():
    text = "Experienced JavaScript developer."
    skills = extract_skills(
        text,
        ["Java", "JavaScript"],
    )
    assert "JavaScript" in skills
    assert "Java" not in skills
#TEST react as react native
def test_react_and_react_native_are_distinct():
    text = "Built applications using React Native."
    skills = extract_skills(
        text,
        ["React", "React Native"],
    )
    assert "React Native" in skills
    assert "React" not in skills
# postgre sql
def test_postgresql_aliases():
    text = """
    Worked with PostgreSQL and Postgres databases.
    """

    skills = extract_skills(
        text,
        ["PostgreSQL", "Postgres"],
    )
    assert "PostgreSQL" in skills
#kubernates
def test_kubernetes_aliases():
    text = """
    Deployed services using Kubernetes and K8s.
    """

    skills = extract_skills(
        text,
        ["Kubernetes", "K8s"],
    )
    assert "Kubernetes" in skills
#ml aliases test
def test_machine_learning_aliases():
    text = """
    Built machine learning models using ML techniques.
    """
    skills = extract_skills(
        text,
        ["Machine Learning", "ML"],
    )
    assert "Machine Learning" in skills
#taxonomy canonical test
def test_skill_taxonomy_contains_canonical_skills():
    assert "Python" in SKILL_TAXONOMY
    assert "Kubernetes" in SKILL_TAXONOMY
    assert "PostgreSQL" in SKILL_TAXONOMY
    assert "Machine Learning" in SKILL_TAXONOMY   
#correct mapping test
def test_skill_alias_map():
    assert SKILL_ALIAS_MAP["k8s"] == "Kubernetes"
    assert SKILL_ALIAS_MAP["postgres"] == "PostgreSQL"
    assert SKILL_ALIAS_MAP["ml"] == "Machine Learning"
    assert SKILL_ALIAS_MAP["nlp"] == "Natural Language Processing"


# evidence based testing for context aware skill matching

def test_extract_skill_evidence():
    text = """
    Built a FastAPI backend and containerized the application using Docker.
    """
    evidence = extract_skill_evidence(text)
    assert evidence["FastAPI"]
    assert evidence["Docker"]

def test_skill_evidence_contains_source_sentence():
    text = """
    Built a FastAPI backend and containerized the application using Docker.
    """
    evidence = extract_skill_evidence(text)
    assert (evidence["FastAPI"]== "Built a FastAPI backend and containerized the application using Docker.")
    assert (evidence["Docker"]== "Built a FastAPI backend and containerized the application using Docker.")

def test_extract_skill_evidence_finds_multiple_skills():
    text = """
    Developed a REST API using Python and FastAPI with PostgreSQL.
    """
    evidence = extract_skill_evidence(text)
    assert "Python" in evidence
    assert "FastAPI" in evidence
    assert "PostgreSQL" in evidence
    assert "REST API" in evidence

def test_skill_evidence_canonicalizes_aliases():
    text = """
    Deployed the application using K8s and Postgres.
    """
    evidence = extract_skill_evidence(text)
    assert "Kubernetes" in evidence
    assert "PostgreSQL" in evidence
    assert "K8s" not in evidence
    assert "Postgres" not in evidence