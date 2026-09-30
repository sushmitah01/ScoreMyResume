from backend.services.skill_extractor import find_skill_matches


def test_find_skill_matches_detects_skill():
    text = """
    Built an API using FastAPI.
    """
    matches = find_skill_matches(text)
    skills = [match[0] for match in matches]
    assert "FastAPI" in skills


def test_find_skill_matches_canonicalizes_alias():
    text = """Deployed the application using K8s and Postgres.
    """
    matches = find_skill_matches(text)
    skills = [match[0] for match in matches]
    assert "Kubernetes" in skills
    assert "PostgreSQL" in skills

def test_find_skill_matches_prefers_longest_match():
    text = """Built a mobile application using React Native.
    """
    matches = find_skill_matches(text)
    skills = [match[0] for match in matches]
    assert "React Native" in skills
    assert "React" not in skills

def test_find_skill_matches_empty_text():
    assert find_skill_matches("") == []