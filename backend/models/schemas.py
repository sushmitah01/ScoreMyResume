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
    job_desciption: Field(
        ...,
        min_length=50,
        description= "The job description to match resume against"
    )
