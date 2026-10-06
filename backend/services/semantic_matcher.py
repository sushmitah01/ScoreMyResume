
import spacy
import re
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from backend.core.config import SENTENCE_TRANSFORMER_MODEL
from backend.services.skill_extractor import nlp

sentence_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
SEMANTIC_EVIDENCE_THRESHOLD = 40.0

def semantic_similarity_score(text1, text2):
    embedding1 = sentence_model.encode(text1)
    embedding2 = sentence_model.encode(text2)

    similarity = cos_sim(embedding1, embedding2)
    score = similarity.item() * 100
    return round(score, 1)

#sentece semantically related to a requirement

def split_resume_sentences(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]
    sentences = []
    for line in lines:
        line = re.sub(r"^[-*]\s+", "", line)
        doc = nlp(line)
        for sentence in doc.sents:
            sentence_text = sentence.text.strip()
            if sentence_text:
                sentences.append(sentence_text)
    return sentences

def find_best_matching_sentence(query, text):
    doc = nlp(text)

    sentences = split_resume_sentences(text)
    if not sentences:
        return {
            "sentence": "",
            "score": 0.0,
        }
    query_embedding = sentence_model.encode(query)
    sentence_embeddings = sentence_model.encode(sentences)

    similarities = cos_sim(
        query_embedding,
        sentence_embeddings,
    )[0]
    best_index = similarities.argmax().item()
    best_score = similarities[best_index].item() * 100
    return {
        "sentence": sentences[best_index],
        "score": round(best_score, 1),
    }

def find_semantic_evidence(requirement, resume_text):
    result = find_best_matching_sentence(
        requirement,
        resume_text,
    )
    return {
        "sentence": result["sentence"],
        "score": result["score"],
        "is_match": result ["score"] >=SEMANTIC_EVIDENCE_THRESHOLD,
    }