import spacy
from spacy.matcher import PhraseMatcher
from backend.core.config import SPACY_MODEL
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from backend.core.config import SENTENCE_TRANSFORMER_MODEL
from groq import Groq
from backend.core.config import GROQ_API_KEY, GROQ_MODEL

nlp = spacy.load(SPACY_MODEL)
sentence_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
client = Groq(api_key=GROQ_API_KEY)

GENERIC_FILLER_WORDS = {
    "experience", "skill", "ability", "plus", "environment",
    "requirement", "responsibility", "candidate", "role", "team",
}
def extract_keywords(text):
    if text=="":
        return []


    doc = nlp(text)
    keywords=[]

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        if token.pos_ in ("NOUN", "PROPN"):
            lemma= token.lemma_.lower()
            if lemma in GENERIC_FILLER_WORDS:
                continue
            keywords.append(lemma)

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

def semantic_similarity_score(text1, text2):
    embedding1 = sentence_model.encode(text1)
    embedding2 = sentence_model.encode(text2)

    similarity = cos_sim(embedding1, embedding2)
    score = similarity.item() * 100

    return round(score, 1)


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