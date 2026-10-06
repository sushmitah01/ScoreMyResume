

from backend.services.semantic_matcher import semantic_similarity_score


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