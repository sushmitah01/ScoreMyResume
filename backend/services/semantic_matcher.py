from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from backend.core.config import SENTENCE_TRANSFORMER_MODEL


sentence_model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)


def semantic_similarity_score(text1, text2):
    embedding1 = sentence_model.encode(text1)
    embedding2 = sentence_model.encode(text2)

    similarity = cos_sim(embedding1, embedding2)
    score = similarity.item() * 100

    return round(score, 1)