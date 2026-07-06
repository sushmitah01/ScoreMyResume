import os
from pathlib import Path
from dotenv import load_dotenv


_ENV_PATH = Path (__file__).resolve().parents[2] / '.env'
load_dotenv(_ENV_PATH)

APP_TITLE= "ScoreMyResume API"
APP_VERSION="1.0.0"
APP_DESCRIPTION ="AI- powered ATS resume scorer using NLP, LLM,ML"

ALLOWED_ORIGINS=[
    "http://localhost:8501",
    "http://scoremyresume.streamlit.app"
]

#upload file rules
MAX_FILE_SIZE_MB=5
MAX_FILE_SIZE_BYTES= MAX_FILE_SIZE_MB *1024 * 1024

SUPPORTED_MIME_TYPES= {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx" ,}
SUPPORTED_EXTENTONS = {".pdf",".docx"}

SPACY_MODEL = "en_core_web_md"
SENTENCE_TRNFORMER_MODEL = os.getenv(
    "SENTENCE_TRANSFORMER_MODEL",
    "all-MiniLM-L6-v2"
)

SCORE_WEIGHTS={
    "keywords": 25,
    "semantic": 25,
    "skills": 20,
    "formatting": 15,
    "experience": 15,
}

#DB
SUPABASE_URL=os.getenv("SUPABASE_URL","")
SUPABASE_KEY=os.getenv("SUPABASE_KEY", "")
SUPABASE_ANON_KEY=os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

#LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY","")