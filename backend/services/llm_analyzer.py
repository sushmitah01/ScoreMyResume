from groq import Groq
from backend.core.config import GROQ_API_KEY, GROQ_MODEL
import json

groq_client = Groq(api_key=GROQ_API_KEY)
class GroqLLM:
    def generate(self, prompt):
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "resume_analysis",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string"
                            },
                            "strengths": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "skill": {
                                            "type": "string"
                                        },
                                        "explanation": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [
                                        "skill",
                                        "explanation"
                                    ],
                                    "additionalProperties": False
                                }
                            },
                            "gaps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "skill": {
                                            "type": "string"
                                        },
                                        "severity": {
                                            "type": "string",
                                            "enum": [
                                                "low",
                                                "medium",
                                                "high"
                                            ]
                                        },
                                        "explanation": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [
                                        "skill",
                                        "severity",
                                        "explanation"
                                    ],
                                    "additionalProperties": False
                                }
                            },
                            "recommendations": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "summary",
                            "strengths",
                            "gaps",
                            "recommendations"
                        ],
                        "additionalProperties": False
                    }
                }
            },
        )

        return json.loads(response.choices[0].message.content)

def analyze_resume(resume, job_description, analysis_data=None, llm=None):
    if analysis_data is None:
        analysis_data = {}
    if llm is None:
        llm= GroqLLM()

    prompt = f"""
Analyze the following resume against the job description.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

DETERMINISTIC ANALYSIS:

MATCHED SKILLS:
{analysis_data.get("matched", [])}

WEAK SKILLS:
{analysis_data.get("weak_match", [])}

MISSING SKILLS:
{analysis_data.get("missing", [])}

REQUIRED MISSING:
{analysis_data.get("required_missing", [])}


PREFERRED MISSING:
{analysis_data.get("preferred_missing", [])}

SEMANTIC EVIDENCE:
{analysis_data.get("semantic_evidence", {})}

WEIGHTED MATCH PERCENTAGE:
{analysis_data.get("weighted_match_percentage", 0.0)}
ANALYSIS RULES:
Do not invent skills that are not supported by the deterministic analysis.
Do not invent experience that is not supported by the resume or deterministic evidence.
Do not contradict deterministic evidence.
Do not change the numerical score.
Use the deterministic analysis as the authoritative source for skill matching.
Use the resume and job description only to explain the evidence.

"""
    result = llm.generate(prompt)
    required_fields = {
    "summary": str,
    "strengths": list,
    "gaps": list,
    "recommendations": list,
    }
    for field, expected_type in required_fields.items():
        if field not in result:
            raise ValueError(f"LLM response is missing required field: {field}")

        if not isinstance(result[field], expected_type):
            raise ValueError(
                f"LLM response field '{field}' must be "
                f"{expected_type.__name__}"
            )
    for strength in result["strengths"]:
        if not isinstance(strength, dict):
            raise ValueError(
                "LLM response field 'strengths' must contain objects"
            )

        if "skill" not in strength or "explanation" not in strength:
            raise ValueError(
                "LLM response field 'strengths' items must contain "
                "'skill' and 'explanation'"
            )
    allowed_severities = {"low", "medium", "high"}

    for gap in result["gaps"]:
        if not isinstance(gap, dict):
            raise ValueError(
                "LLM response field 'gaps' must contain objects"
            )

        if "skill" not in gap or "severity" not in gap or "explanation" not in gap:
            raise ValueError(
                "LLM response field 'gaps' items must contain "
                "'skill', 'severity', and 'explanation'"
            )

        if gap["severity"] not in allowed_severities:
            raise ValueError(
                "LLM response field 'gaps' severity must be "
                "'low', 'medium', or 'high'"
            )
    for recommendation in result["recommendations"]:
        if not isinstance(recommendation, str):
            raise ValueError(
                "LLM response field 'recommendations' must contain strings"
            )
    return {
    "summary": result["summary"],
    "strengths": result["strengths"],
    "gaps": result["gaps"],
    "recommendations": result["recommendations"],
    }