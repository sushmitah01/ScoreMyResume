from backend.services.llm_analyzer import analyze_resume

def test_analyze_resume():

    result= analyze_resume(
        "Python developer with FastAPI experience.",
        "Required: Python and FastAPI.",
    )

    assert isinstance(result, dict)
    assert "summary" in result
    assert "strengths" in result
    assert "gaps" in result
    assert "recommendations" in result


class FakeLLM:
    def generate(self, prompt):
        return {
            "summary": "Strong Python and FastAPI alignment.",
            "strengths":[ {"skill": "Python",
                    "explanation": "The resume demonstrates Python experience.",
                },
                {
            "skill": "FastAPI",
            "explanation": "The resume demonstrates FastAPI experience.",
                },
            ],
            "gaps": [],
            "recommendations": ["Add more measurable project outcomes."],
        }


def test_analyze_resume_uses_llm_response():
    fake_llm = FakeLLM()

    result = analyze_resume(
        "Python developer with FastAPI experience.",
        "Required: Python and FastAPI.",
        llm=fake_llm,
    )

    assert result["summary"] == "Strong Python and FastAPI alignment."
    assert result["strengths"] == [
    {
        "skill": "Python",
        "explanation": "The resume demonstrates Python experience.",
    },
    {
        "skill": "FastAPI",
        "explanation": "The resume demonstrates FastAPI experience.",
    },
]
    assert result["gaps"] == []
    assert result["recommendations"] == [
        "Add more measurable project outcomes."
    ]


class RecordingLLM:
    def __init__(self):
        self.prompt = None

    def generate(self, prompt):
        self.prompt = prompt

        return {
            "summary": "Test summary",
            "strengths": [],
            "gaps": [],
            "recommendations": [],
        }


def test_analyze_resume_builds_prompt_from_resume_and_job_description():
    llm = RecordingLLM()

    analyze_resume(
        "I built APIs using FastAPI.",
        "Required: FastAPI experience.",
        llm=llm,
    )

    assert "I built APIs using FastAPI." in llm.prompt
    assert "Required: FastAPI experience." in llm.prompt


class StructuredFakeLLM:
    def generate(self, prompt):
        return {
            "summary": "Strong backend alignment.",
            "strengths": [
                {
                    "skill": "FastAPI",
                    "explanation": "The resume demonstrates FastAPI project experience.",
                }
            ],
            "gaps": [
                {
                    "skill": "Kubernetes",
                    "severity": "high",
                    "explanation": "Kubernetes is required but no supporting resume evidence was found.",
                }
            ],
            "recommendations": [
                "Add measurable outcomes to the FastAPI project description."
            ],
        }


def test_analyze_resume_supports_structured_strengths_and_gaps():
    llm = StructuredFakeLLM()

    result = analyze_resume(
        "Built APIs using FastAPI.",
        "Required: FastAPI and Kubernetes.",
        llm=llm,
    )

    assert result["strengths"][0]["skill"] == "FastAPI"
    assert result["strengths"][0]["explanation"] != ""

    assert result["gaps"][0]["skill"] == "Kubernetes"
    assert result["gaps"][0]["severity"] == "high"
    assert result["gaps"][0]["explanation"] != ""

class AnalysisDataRecordingLLM:
    def __init__(self):
        self.prompt = None

    def generate(self, prompt):
        self.prompt = prompt

        return {
            "summary": "Strong backend alignment.",
            "strengths": [],
            "gaps": [],
            "recommendations": [],
        }

def test_analyze_resume_includes_deterministic_analysis_in_prompt():
    llm = AnalysisDataRecordingLLM()

    analysis_data = {
        "matched": ["Python", "FastAPI"],
        "weak_match": ["Docker"],
        "missing": ["Kubernetes"],
        "required_missing": ["Kubernetes"],
        "preferred_missing": [],
        "weighted_match_percentage": 72.4,
    }

    analyze_resume(
        "Built APIs using FastAPI.",
        "Required: FastAPI and Kubernetes.",
        analysis_data,
        llm=llm,
    )

    assert "Python" in llm.prompt
    assert "FastAPI" in llm.prompt
    assert "Docker" in llm.prompt
    assert "Kubernetes" in llm.prompt
    assert "72.4" in llm.prompt

def test_analyze_resume_builds_evidence_aware_prompt():
    llm = AnalysisDataRecordingLLM()

    analysis_data = {
        "matched": ["Python", "FastAPI"],
        "weak_match": ["Docker"],
        "missing": ["Kubernetes"],
        "required_missing": ["Kubernetes"],
        "preferred_missing": [],
        "semantic_evidence": {
            "Distributed Systems": {
                "sentence": "Architected high-throughput microservices.",
                "score": 49.0,
                "is_match": True,
            }
        },
        "weighted_match_percentage": 72.4,
    }

    analyze_resume(
        "Built APIs using FastAPI.",
        "Required: FastAPI and Kubernetes.",
        analysis_data,
        llm=llm,
    )

    assert "MATCHED SKILLS" in llm.prompt
    assert "WEAK SKILLS" in llm.prompt
    assert "MISSING SKILLS" in llm.prompt
    assert "REQUIRED MISSING" in llm.prompt
    assert "PREFERRED MISSING" in llm.prompt
    assert "SEMANTIC EVIDENCE" in llm.prompt
    assert "Python" in llm.prompt
    assert "Docker" in llm.prompt
    assert "Kubernetes" in llm.prompt
    assert "Distributed Systems" in llm.prompt

def test_llm_to_deterministic_evidence():
    llm = AnalysisDataRecordingLLM()
    analysis_data = {
        "matched": ["Python", "FastAPI"],
        "weak_match": ["Docker"],
        "missing": ["Kubernetes"],
        "required_missing": ["Kubernetes"],
        "preferred_missing": [],
        "semantic_evidence": {},
        "weighted_match_percentage": 72.4,
    }

    analyze_resume(
        "Built APIs using FastAPI.",
        "Required: FastAPI and Kubernetes.",
        analysis_data,
        llm=llm,
    )
    assert "Do not invent skills" in llm.prompt
    assert "Do not invent experience" in llm.prompt
    assert "Do not contradict deterministic evidence" in llm.prompt
    assert "Do not change the numerical score" in llm.prompt

class MalformedLLM:
    def generate(self, prompt):
        return {
            "summary": "Good candidate.",
            "strengths": "Python, FastAPI",
            "gaps": [],
            "recommendations": [],
        }

def test_analyze_resume_rejects_malformed_llm_response():
    llm = MalformedLLM()
    try:
        analyze_resume(
            "Built APIs using FastAPI.",
            "Required: FastAPI.",
            llm=llm,
        )
    except ValueError:
        return
    assert False, "Expected ValueError for malformed LLM response"

class MissingFieldLLM:
    def generate(self, prompt):
        return {
            "summary": "Good candidate.",
            "strengths": [],
            "gaps": [],
        }

def test_analyze_resume_rejects_missing_llm_field():
    llm = MissingFieldLLM()
    try:
        analyze_resume(
            "Built APIs using FastAPI.",
            "Required: FastAPI.",
            llm=llm,
        )
    except ValueError as error:
        assert "recommendations" in str(error)
        return
    assert False, "Expected ValueError for missing LLM response field"


class MalformedStrengthLLM:
    def generate(self, prompt):
        return {
            "summary": "Good candidate.",
            "strengths": [
                {
                    "skill": "FastAPI",
                }
            ],
            "gaps": [],
            "recommendations": [],
        }

def test_analyze_resume_rejects_malformed_strength():
    llm = MalformedStrengthLLM()

    try:
        analyze_resume(
            "Built APIs using FastAPI.",
            "Required: FastAPI.",
            llm=llm,
        )
    except ValueError as error:
        assert "strengths" in str(error)
        return

    assert False, "Expected ValueError for malformed strength"

class MalformedGapLLM:
    def generate(self, prompt):
        return {
            "summary": "Good candidate.",
            "strengths": [],
            "gaps": [
                {
                    "skill": "Kubernetes",
                    "severity": "critical",  # Invalid severity
                    "explanation": "Kubernetes is missing.",
                }
            ],
            "recommendations": [],
        }

def test_analyze_resume_rejects_invalid_gap_severity():
    llm = MalformedGapLLM()
    try:
        analyze_resume(
            "Built APIs using FastAPI.",
            "Required: FastAPI and Kubernetes.",
            llm=llm,
        )
    except ValueError as error:
        assert "severity" in str(error)
        return

    assert False, "Expected ValueError for invalid gap severity"
