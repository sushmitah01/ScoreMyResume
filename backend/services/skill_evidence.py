import re
from backend.services.skill_extractor import find_skill_matches, nlp
def classify_skill_context(sentence):
    """Classify how strongly a resume sentence supports a skill.
    Returns:
        strong
        weak
        learning
        negative
    """
    """ using regex """
    sentence_lower = sentence.lower()
    negative_patterns = [
        r"\bno experience\b",
        r"\bno practical experience\b",
        r"\bno hands-on experience\b",
        r"\bwithout experience\b",
        r"\black experience\b",
        r"\black of experience\b",
        r"\bnot experienced\b",
        r"\bnever used\b",
    ]
    learning_patterns = [
        r"\binterested in learning\b",
        r"\blearning\b",
        r"\bcurrently learning\b",
        r"\bstudying\b",
        r"\bcurrently studying\b",
        r"\blooking to learn\b",
        r"\bwant to learn\b",
        r"\bwilling to learn\b",
    ]

    strong_patterns = [
        r"\bstrong knowledge\b",
        r"\bstrong understanding\b",
        r"\bhands-on experience\b",
        r"\bpractical experience\b",
        r"\bproduction experience\b",
        r"\bextensive experience\b",
        r"\bextensive knowledge\b",
        r"\bexpertise in\b",
    ]

    weak_patterns = [
        r"\bfamiliar with\b",
        r"\bbasic knowledge of\b",
        r"\bbasic understanding of\b",
        r"\bworking knowledge of\b",
        r"\blimited experience\b",
        r"\blimited knowledge\b",
        r"\bexposure to\b",
        r"\bknowledge of\b",
        r"\bunderstanding of\b",
    ]

    for pattern in negative_patterns:
        if re.search(pattern, sentence_lower):
            return "negative"

    for pattern in learning_patterns:
        if re.search(pattern, sentence_lower):
            return "learning"

    for pattern in strong_patterns:
        if re.search(pattern, sentence_lower):
            return "strong"

    for pattern in weak_patterns:
        if re.search(pattern, sentence_lower):
            return "weak"

    return "strong"


def classify_evidence_type(sentence):
    """
    Classify where the skill evidence comes from.

    Returns:
        project
        work_experience
        education
        certification
        generic
    """

    sentence_lower = sentence.lower()

    project_patterns = [
        r"\bbuilt\b",
        r"\bdeveloped\b",
        r"\bimplemented\b",
        r"\bcreated\b",
        r"\bdesigned\b",
        r"\bengineered\b",
        r"\bdeployed\b",
        r"\bintegrated\b",
        r"\bdeveloped a project\b",
        r"\bbuilt a project\b",
    ]

    work_patterns = [
        r"\bworked as\b",
        r"\bworking as\b",
        r"\bworked at\b",
        r"\bworking at\b",
        r"\bemployment\b",
        r"\bjob\b",
        r"\binternship\b",
        r"\bintern\b",
        r"\bprofessional experience\b",
        r"\bwork experience\b",
    ]

    education_patterns = [
        r"\bcoursework\b",
        r"\bcourse\b",
        r"\buniversity\b",
        r"\bcollege\b",
        r"\bdegree\b",
        r"\bstudied\b",
        r"\bacademic\b",
        r"\bbachelor\b",
        r"\bmaster\b",
        r"\bb\.sc\b",
        r"\bbsc\b",
        r"\bm\.sc\b",
        r"\bmsc\b",
    ]

    certification_patterns = [
        r"\bcertification\b",
        r"\bcertified\b",
        r"\bcertificate\b",
        r"\bcredential\b",
        r"\bcompleted training\b",
        r"\bprofessional training\b",
    ]

    for pattern in certification_patterns:
        if re.search(pattern, sentence_lower):
            return "certification"

    for pattern in work_patterns:
        if re.search(pattern, sentence_lower):
            return "work_experience"

    for pattern in education_patterns:
        if re.search(pattern, sentence_lower):
            return "education"

    for pattern in project_patterns:
        if re.search(pattern, sentence_lower):
            return "project"

    return "generic"


def classify_evidence_confidence(evidence_type):
    """confidence based on evidence type.
    Returns:
        high
        medium
        low
    """

    if evidence_type in {
        "project",
        "work_experience",
    }:
        return "high"
    if evidence_type in {
        "education",
        "certification",
    }:
        return "medium"
    return "low"

def extract_skill_evidence(text, skills_db= None):

    if not text :
        return {}

    doc= nlp(text)

    matches= find_skill_matches(text, skills_db)
    evidence= {}

    for canonical_skill,start,end in matches:
        sentence = doc[start:end].sent.text.strip()
        context= classify_skill_context(sentence)
        evidence_type = classify_evidence_type(sentence)
        confidence = classify_evidence_confidence(evidence_type)
        evidence[canonical_skill] ={
            "sentence":sentence,
            "context": context,
            "evidence_type":evidence_type,
            "confidence": confidence
        }
    return evidence

