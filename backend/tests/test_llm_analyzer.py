import pytest
from backend.services.llm_analyzer import analyze_resume
from backend.services import llm_analyzer
                                         
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
def test_analyze_resume_rejects_strength_with_invalid_field_types():
    class InvalidStrengthLLM:
        def generate(self, prompt):
            return {
                "summary": "Good candidate.",
                "strengths": [
                    {
                        "skill": None,
                        "explanation": "Demonstrates Python experience.",
                    }
                ],
                "gaps": [],
                "recommendations": [],
            }

    with pytest.raises(ValueError, match="strengths"):
        analyze_resume(
            "Python developer.",
            "Required: Python.",
            llm=InvalidStrengthLLM(),
        )

def test_analyze_resume_rejects_gap_with_invalid_field_types():
    class InvalidGapLLM:
        def generate(self, prompt):
            return {
                "summary": "Good candidate.",
                "strengths": [],
                "gaps": [
                    {
                        "skill": "Kubernetes",
                        "severity": "high",
                        "explanation": None,
                    }
                ],
                "recommendations": [],
            }

    with pytest.raises(ValueError, match="gaps"):
        analyze_resume(
            "Python developer.",
            "Required: Python and Kubernetes.",
            llm=InvalidGapLLM(),
        )


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

def test_analyze_resume_rejects_hallucinated_strength():
    class HallucinatingLLM:
        def generate(self, prompt):
            return {
                "summary": "Strong backend candidate.",
                "strengths": [
                    {
                        "skill": "Kubernetes",
                        "explanation": "The candidate has strong Kubernetes experience.",
                    }
                ],
                "gaps": [],
                "recommendations": [],
            }

    analysis_data = {
        "matched": ["Python", "FastAPI"],
        "weak_match": [],
        "missing": ["Kubernetes"],
        "required_missing": ["Kubernetes"],
        "preferred_missing": [],
        "semantic_evidence": {},
        "weighted_match_percentage": 66.7,
        "score": 66.7,
    }

    with pytest.raises(ValueError, match="unsupported skill"):
        analyze_resume(
            "Python developer with FastAPI experience.",
            "Required: Python, FastAPI, Kubernetes.",
            analysis_data=analysis_data,
            llm=HallucinatingLLM(),
        )

def test_analyze_resume_rejects_hallucinated_gap():
    class HallucinatedGapLLM:
        def generate(self, prompt):
            return {
                "summary": "Strong backend candidate.",
                "strengths": [],
                "gaps": [
                    {
                        "skill": "Docker",
                        "severity": "high",
                        "explanation": "Docker experience is missing.",
                    }
                ],
                "recommendations": [],
            }
    analysis_data = {
        "matched": ["Python", "FastAPI"],
        "weak_match": [],
        "missing": ["Kubernetes"],
        "required_missing": ["Kubernetes"],
        "preferred_missing": [],
        "semantic_evidence": {},
        "weighted_match_percentage": 66.7,
        "score": 66.7,
    }
    with pytest.raises(ValueError, match="unsupported skill in gaps"):
        analyze_resume(
            "Python developer with FastAPI experience.",
            "Required: Python, FastAPI, Kubernetes.",
            analysis_data=analysis_data,
            llm=HallucinatedGapLLM(),
        )
    

def test_analyze_resume_rejects_empty_recommendation():
    class EmptyRecommendationLLM:
        def generate(self, prompt):
            return {
                "summary": "Good candidate.",
                "strengths": [],
                "gaps": [],
                "recommendations": ["   "],
            }

    with pytest.raises(ValueError, match="recommendations"):
        analyze_resume(
            "Python developer.",
            "Required: Python.",
            llm=EmptyRecommendationLLM(),
        )

def test_analyze_resume_rejects_empty_summary():
    class EmptySummaryLLM:
        def generate(self, prompt):
            return {
                "summary": "   ",
                "strengths": [],
                "gaps": [],
                "recommendations": [],
            }

    with pytest.raises(ValueError, match="summary"):
        analyze_resume(
            "Python developer.",
            "Required: Python.",
            llm=EmptySummaryLLM(),
        )

def test_groq_llm_propagates_api_errors(monkeypatch):
    from backend.services import llm_analyzer

    class FakeCompletions:
        def create(self, **kwargs):
            raise RuntimeError("Simulated Groq API failure")

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setattr(llm_analyzer, "groq_client", FakeClient())

    with pytest.raises(RuntimeError, match="Simulated Groq API failure"):
        llm_analyzer.GroqLLM().generate("Test prompt")

def test_groq_llm_rejects_invalid_json_response(monkeypatch):
    class FakeMessage:
        content = "This is not valid JSON"
    class FakeChoice:
        message = FakeMessage()
    class FakeResponse:
        choices = [FakeChoice()]
    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()
    class FakeChat:
        completions = FakeCompletions()
    class FakeClient:
        chat = FakeChat()
    monkeypatch.setattr(llm_analyzer, "groq_client", FakeClient())

    with pytest.raises(ValueError):
        llm_analyzer.GroqLLM().generate("Test prompt")


def test_analyze_resume_allows_resume_skill_not_in_job_analysis():
    class ResumeSkillLLM:
        def generate(self, prompt):
            return {
                "summary": "The candidate has relevant backend experience.",
                "strengths": [],
                "gaps": [],
                "recommendations": [
                    "Highlight your existing AWS experience in the resume."
                ],
            }

    analysis_data = {
        "matched": ["Python", "Docker"],
        "weak_match": [],
        "missing": [],
        "required_missing": [],
        "preferred_missing": [],
        "semantic_evidence": {},
        "weighted_match_percentage": 80.0,
        "score": 80.0,
    }

    result = analyze_resume(
        "Python developer with experience using Docker and AWS.",
        "Looking for a Python developer with experience in Docker.",
        analysis_data=analysis_data,
        llm=ResumeSkillLLM(),
    )

    assert result["recommendations"] == [
        "Highlight your existing AWS experience in the resume."
    ]


def test_analyze_resume_rejects_unsupported_skill_in_recommendation():
    class UnsupportedSkillLLM:
        def generate(self, prompt):
            return {
                "summary": "Backend candidate.",
                "strengths": [],
                "gaps": [],
                "recommendations": [
                    "Learn Kubernetes to improve your profile."
                ],
            }

    analysis_data = {
        "matched": ["Python", "Docker"],
        "weak_match": [],
        "missing": [],
        "required_missing": [],
        "preferred_missing": [],
        "semantic_evidence": {},
        "weighted_match_percentage": 80.0,
        "score": 80.0,
    }

    with pytest.raises(ValueError, match="unsupported skill in recommendation"):
        analyze_resume(
            "Python developer with Docker experience.",
            "Looking for a Python developer with Docker experience.",
            analysis_data=analysis_data,
            llm=UnsupportedSkillLLM(),
        )


