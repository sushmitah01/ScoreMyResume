import spacy
from spacy.matcher import PhraseMatcher
from backend.core.config import SPACY_MODEL
from backend.services.skill_taxonomy import SKILL_ALIAS_MAP


nlp = spacy.load(SPACY_MODEL)


def build_skill_lookup(skills_db):
    skill_lookup = {}

    for skill in skills_db:
        skill_lower = skill.lower()

        canonical_skill = SKILL_ALIAS_MAP.get(
            skill_lower,
            skill
        )

        skill_lookup[skill_lower] = canonical_skill

    return skill_lookup


def find_skill_matches(text, skills_db=None):
    """
    Find canonical technical skills in text.

    Returns:
        list of tuples:
        (canonical_skill, start_token, end_token)
    """

    if not text:
        return []

    if skills_db is None:
        skills_db = list(SKILL_ALIAS_MAP.keys())

    skill_lookup = build_skill_lookup(skills_db)

    matcher = PhraseMatcher(
        nlp.vocab,
        attr="LOWER"
    )

    patterns = [
        nlp.make_doc(skill)
        for skill in skills_db
    ]

    matcher.add("SKILLS", patterns)

    doc = nlp(text)

    matches = matcher(doc)

    matched_spans = sorted(
        matches,
        key=lambda match: (
            -(match[2] - match[1]),
            match[1]
        )
    )

    found_matches = []
    occupied_tokens = set()

    for _, start, end in matched_spans:

        if any(
            token_index in occupied_tokens
            for token_index in range(start, end)
        ):
            continue

        matched_text = doc[start:end].text.strip().lower()

        canonical_skill = skill_lookup.get(matched_text)

        if canonical_skill:
            found_matches.append(
                (
                    canonical_skill,
                    start,
                    end
                )
            )

            occupied_tokens.update(
                range(start, end)
            )

    return found_matches