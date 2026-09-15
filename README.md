# ScoreMyResume 

> AI-powered ATS Resume Scorer — built for job seekers who want to get hired faster.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![Supabase](https://img.shields.io/badge/Supabase-Database-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## What is ScoreMyResume?

ScoreMyResume analyzes your resume against any job description using AI — the same way an Applicant Tracking System (ATS) would. Get an instant match score, see exactly what keywords you're missing, and know what to fix before a recruiter ever sees your application.


##  Features

-  **Resume Upload** — supports PDF and DOCX formats
-  **AI-Powered Scoring** — multi-dimensional ATS score using NLP + ML + LLM
-  **Keyword Gap Analysis** — see exactly what's missing from your resume
-  **Score Breakdown** — keywords, semantic match, skills, formatting, experience
-  **AI Feedback** — detailed suggestions powered by Groq LLM
-  **PDF Report** — download a professional score report
-  **User Auth** — secure signup/login with JWT tokens
-  **History** — save and review past scoring sessions

##  How It Works

```
User uploads resume + job description
           ↓
spaCy NLP extracts skills and entities
           ↓
Sentence Transformers compute semantic similarity
           ↓
Groq LLM generates detailed feedback
           ↓
Score breakdown returned to user
           ↓
Results saved to Supabase database
```

##  Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Database & Auth | Supabase (PostgreSQL) |
| NLP | spaCy (en_core_web_md) |
| Semantic Search | Sentence Transformers |
| LLM | Groq API |
| PDF Generation | WeasyPrint + Jinja2 |
| Testing | Pytest + TDD |

##  Project Structure

```
ScoreMyResume/
├── backend/
│   ├── api/
│   │   └── auth.py          # signup, login endpoints
│   ├── core/
│   │   ├── config.py        # environment variables
│   │   └── security.py      # JWT + password hashing
│   ├── database/
│   │   └── supabase_client.py
│   ├── models/
│   │   └── schemas.py       # Pydantic data models
│   ├── services/            # scoring engine (coming soon)
│   └── tests/
│       ├── test_security.py
│       └── test_auth.py
├── frontend/                # Streamlit UI (coming soon)
├── .env                     # secrets (not committed)
├── requirements.txt
└── README.md
```

##  Current Progress

-  Project structure and architecture
-  Environment configuration
-  Pydantic schemas for all data models
-  Password hashing with bcrypt
-  JWT authentication
-  Supabase database connection
-  Signup and login API endpoints
-  TDD — all tests passing
-  ATS scoring engine (spaCy + Sentence Transformers)
-  Groq LLM feedback integration
-  Resume file parsing (PDF/DOCX)
-  PDF report generation
-  Streamlit frontend
-  Deployment (Render + Streamlit Cloud)

## Setup & Installation

```bash
# Clone the repo
git clone https://github.com/sushmitah01/ScoreMyResume.git
cd ScoreMyResume

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_md

# Create .env file — fill in your keys
```

##  Environment Variables

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
GROQ_API_KEY=your_groq_key
```

##  Running Tests

```bash
pytest backend/tests/ -v
```

##  Running the App

```bash
# Backend
uvicorn backend.main:app --reload

# Frontend (not completed)
streamlit run frontend/streamlit_app.py
```

##  API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API docs.

##  Built With TDD

This project follows Test-Driven Development — every feature has tests written before implementation. This ensures reliability and teaches real-world engineering practices.

##  Author

**Sushmita** — [@sushmitah01](https://github.com/sushmitah01)

---

