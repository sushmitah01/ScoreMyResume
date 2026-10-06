

from backend.services.semantic_matcher import (semantic_similarity_score,
                                               find_best_matching_sentence,
                                               split_resume_sentences,
                                               find_semantic_evidence,
                                               SEMANTIC_EVIDENCE_THRESHOLD)


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


# find semantic evidence for a requirement in resume sentences

def test_semantic_matcher_finds_paraphrased_resume_sentence():
    requirement = (
        "Experience designing scalable distributed backend systems."
    )

    resume_text = """
    Passionate home baker who loves making sourdough bread.
    Architected high-throughput microservices capable of serving millions of requests.
    """
    result = find_best_matching_sentence(
        requirement,
        resume_text,
    )
    assert (
        result["sentence"]
        == "Architected high-throughput microservices capable of serving millions of requests."
    )

def test_semantic_matching_does_not_override_negative_context():
    requirement = "Experience with Kubernetes."
    resume_text = """
    No experience with Kubernetes.
    Experienced with Python and FastAPI.
    """
    result = find_best_matching_sentence(
        requirement,
        resume_text,
    )
    assert "No experience with Kubernetes." in result["sentence"]

def test_resume_lines_are_split_into_separate_sentences():
    resume_text = """
    No experience with Kubernetes.
    Experienced with Python and FastAPI.
    """

    result = split_resume_sentences(resume_text)

    assert result == [
        "No experience with Kubernetes.",
        "Experienced with Python and FastAPI.",
    ]

def test_semantic_evidence_returns_best_sentence_and_score():
    requirement = (
        "Experience designing scalable distributed backend systems."
    )
    resume_text = """Passionate home baker who loves making sourdough bread.
    Architected high-throughput microservices capable of serving millions of requests.
    """
    result = find_semantic_evidence(
        requirement,
        resume_text,
    )
    assert (
        result["sentence"]
        == "Architected high-throughput microservices capable of serving millions of requests."
    )
    assert result["score"] > 0


def test_semantic_evidence_distinguishes_related_and_unrelated_text():
    requirement = (
        "Experience designing scalable distributed backend systems."
    )
    related_resume = """Architected high-throughput microservices capable of serving millions of requests."""
    unrelated_resume = """Passionate home baker who loves making sourdough bread.
    """
    related_result = find_semantic_evidence(
        requirement,
        related_resume,
    )
    unrelated_result = find_semantic_evidence(
        requirement,
        unrelated_resume,
    )
    print("RELATED SCORE:", related_result["score"])
    print("UNRELATED SCORE:", unrelated_result["score"])
    assert related_result["score"] > unrelated_result["score"]


def test_semantic_evidence_requires_meaningful_similarity():
    requirement = (
        "Experience designing scalable distributed backend systems."
    )
    related_resume = """Architected high-throughput microservices capable of serving millions of requests."""
    unrelated_resume = """Passionate home baker who loves making sourdough bread."""
    related_result = find_semantic_evidence(
        requirement,
        related_resume,
    )
    unrelated_result = find_semantic_evidence(
        requirement,
        unrelated_resume,
    )
    assert related_result["score"] >= SEMANTIC_EVIDENCE_THRESHOLD
    assert unrelated_result["score"] < SEMANTIC_EVIDENCE_THRESHOLD

def test_semantic_evidence_reports_match_status():
    requirement = (
        "Experience designing scalable distributed backend systems."
    )
    related_resume = """Architected high-throughput microservices capable of serving millions of requests."""
    unrelated_resume = """Passionate home baker who loves making sourdough bread."""
    related_result = find_semantic_evidence(
        requirement,
        related_resume,
    )
    unrelated_result = find_semantic_evidence(
        requirement,
        unrelated_resume,
    )
    assert related_result["is_match"] is True
    assert unrelated_result["is_match"] is False

def test_semantic_evidence_preserves_negative_context():
    requirement = "Experience with Kubernetes."
    resume_text = """
    No experience with Kubernetes.
    Experienced with Python and FastAPI.
    """
    result = find_semantic_evidence(
        requirement,
        resume_text,
    )
    assert result["is_match"] is True