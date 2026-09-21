from fastapi import FastAPI
from backend.api.auth import router as auth_router
from backend.api.resume import router as resume_router


app=FastAPI(
    title="ScoreResumeProject",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(resume_router)
@app.get("/")

def home():
    return {
        "app": "ScoreMyResume API",
        "version": "1.0.0",
        "status":"running"
    } #this dict will get converted into a json