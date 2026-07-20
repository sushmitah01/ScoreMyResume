from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email:str
    password: str
    full_name: str

class Userlogin(BaseModel):
    email: str
    password: str

class TokenResponses(BaseModel):
    acess_token:str
    token_type: str = "bearer"
    user_id: str
    email: str

class ScoreRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=50,
        description= "The job description to match resume against"
    )

class ScoreBreakdown(BaseModel):
    keywords: float
    semantic: float
    skills: float
    formatting: float
    experience: float

class ScoreResponse(BaseModel):
    overall_score: float
    breakdown: ScoreBreakdown
    matched_keywords: list[str]
    missing_keywords: list[str]
    matched_skills: list[str]
    matched_skills: list[str]
    ai_feedback: str
    suggestions: list[str]
    processing_time_ms: int

class HistoryRecord(BaseModel):
    id: str
    user_id: str
    resume_name: str
    job_tittle: Optional[str]
    overall_score: float
    breakdown: ScoreBreakdown
    ai_feedback: str
    created_at: datetime

class FeedbackRequest(BaseModel):
    score_id: str
    rating: int=Field(..., ge=1, le=5)
    comment: Optional[str]

class FeedbackResponse(BaseModel):
    message: str
    feedback_id: str


