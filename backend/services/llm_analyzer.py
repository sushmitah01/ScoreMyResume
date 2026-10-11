import re
from backend.services.skill_taxonomy import SKILL_ALIAS_MAP
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
        if not result["summary"].strip():
            raise ValueError(
                "LLM response field 'summary' must not be empty"
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
        if (
            not isinstance(strength["skill"], str)
            or not strength["skill"].strip()
            or not isinstance(strength["explanation"], str)
            or not strength["explanation"].strip()
        ):
            raise ValueError(
                "LLM response field 'strengths' must contain "
                "non-empty string values for 'skill' and 'explanation'"
            )
              
    if analysis_data:
        supported_strengths = set(analysis_data.get("matched", []))
        supported_strengths.update(analysis_data.get("weak_match", []))
        for skill, evidence in analysis_data.get("semantic_evidence", {}).items():
            if evidence.get("is_match") is True:
                supported_strengths.add(skill)

        for strength in result["strengths"]:
            skill = strength["skill"]

            if skill not in supported_strengths:
                raise ValueError(
                    f"LLM response contains unsupported skill in strengths: {skill}"
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
        if (
            not isinstance(gap["skill"], str)
            or not gap["skill"].strip()
            or not isinstance(gap["explanation"], str)
            or not gap["explanation"].strip()
        ):
            raise ValueError(
                "LLM response field 'gaps' must contain "
                "non-empty string values for 'skill' and 'explanation'"
            )
        if analysis_data:
            supported_gaps = set(analysis_data.get("missing", []))

            if gap["skill"] not in supported_gaps:
                raise ValueError(
                    f"LLM response contains unsupported skill in gaps: "
                    f"{gap['skill']}"
                )
    for recommendation in result["recommendations"]:
        if not isinstance(recommendation, str):
            raise ValueError(
                "LLM response field 'recommendations' must contain strings"
            )
        if not recommendation.strip():
            raise ValueError(
                "LLM response field 'recommendations' must not contain empty strings"
            )
        if not analysis_data:
            continue 
        known_skills = (
            set(analysis_data.get("matched", []))
            | set(analysis_data.get("weak_match", []))
            | set(analysis_data.get("missing", []))
            | set(analysis_data.get("required_missing", []))
            | set(analysis_data.get("preferred_missing", []))
        ) 
        known_skill_names = {
            skill.casefold() for skill in known_skills
        } 
        unsupported_skills = set()          
        for skill in set(SKILL_ALIAS_MAP.values()):
            if (
                re.search(
                    rf"\b{re.escape(skill)}\b",
                    recommendation,
                    re.IGNORECASE,                
                )
                and skill.casefold() not in known_skill_names
                and not re.search(
                    rf"\b{re.escape(skill)}\b",
                    resume,
                    re.IGNORECASE,
                )
            ):
                unsupported_skills.add(skill)


        if unsupported_skills:
            raise ValueError(
                "LLM response contains unsupported skill in recommendation: "
                f"{sorted(unsupported_skills)[0]}"
            )
    return {
    "summary": result["summary"],
    "strengths": result["strengths"],
    "gaps": result["gaps"],
    "recommendations": result["recommendations"],
    }