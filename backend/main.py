from fastapi import FastAPI

app=FastAPI()

@app.get("/")

def home():
    return {
        "app": "ScoreMyResume API",
        "version": "1.0.0",
        "status":"running"} #this dict will get converted into a json