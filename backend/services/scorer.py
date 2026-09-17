import spacy
from spacy.matcher import PhraseMatcher
from backend.core.config import SPACY_MODEL

nlp = spacy.load(SPACY_MODEL)


def extract_keywords(text):
    if text==" ":
        return []


    doc = nlp(text)
    keywords=[]

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        if token.pos_ in ("NOUN", "PRONOUN"):
            keywords.append (token.lemma_.lower())

    return keywords

def extract_skills(text, skills_db):
    matcher =PhraseMatcher(nlp.vocab, attr="LOWER")

    patterns = [nlp.make_doc(skill)for skill in skills_db]
    matcher.add("SKILLS", patterns )
    doc= nlp(text)

    matches= matcher(doc)

    found_skills= set()

    for match_id,start, end in matches:
        span_text= doc[start:end].text
        for skill in skills_db:
            if skill.lower()== span_text.lower():
                found_skills.add(skill)
    return list(found_skills)

        

def keyword_match_score(resume_keywords, jd_keywords):
    if not jd_keywords:
        return 0.0

    resume_set= set(resume_keywords)
    jd_set=set(jd_keywords)

    matched= resume_set & jd_set
    score= (len(matched)/ len(jd_set))* 100

    return round(score,1)
