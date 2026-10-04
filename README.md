# AI Resume Analyzer

An AI-powered pipeline built with **FastAPI**, **Google Gemini GenAI SDK (`google-genai`)**, **Pydantic**, and document parsing utilities (`pypdf`, `python-docx`) that evaluates a candidate's resume and self-description against a target job description.

## 🚀 Features

Given:
1. **Cleaned Resume Content** (extracted and cleaned from uploaded PDF, DOCX, or TXT file or raw text)
2. **Job Description** (target role requirements and qualifications)
3. **User Self-Description** (candidate's self-articulated context, ongoing learning, goals, or notes)

The pipeline produces:
1. 🔍 **Missing Requirements**: Granular gap analysis categorizing missing skills, tools, experience, or certifications with severity levels (`Critical`, `High`, `Medium`, `Low`), detailed reasoning, and actionable fix recommendations.
2. 🎯 **5 Targeted Interview Questions**: Exactly 5 tailored interview questions with question type, hiring team rationale, and 3-5 key points the candidate should cover to prepare.
3. 🗺️ **Preparation Roadmap**: A chronological, phase-by-phase learning roadmap (timelines, objectives, actionable items, and recommended projects/resources) to bridge gaps and prepare for the role.

---

## 📁 Project Architecture

```
backend/
├── src/
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── pipeline.py       # Core ResumeAnalysisPipeline with Gemini integration
│   │   └── prompts.py        # System prompt and prompt templates
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # Pydantic Settings (.env configuration)
│   │   └── security.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py            # API router aggregator
│   │   └── analyzer.py       # /api/v1/analyzer endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── analyzer.py       # Pydantic schemas (MissingRequirement, InterviewQuestion, RoadmapStep, etc.)
│   ├── services/
│   │   ├── __init__.py
│   │   └── resume_parser.py  # PDF, DOCX, TXT loaders & unicode/bullet cleaning
│   └── main.py               # FastAPI application setup
└── tests/
    ├── test_gemini.py        # explicitly testing gemini model
    └── test_pipeline.py      # Unit & integration tests
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or standard `pip`

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and set your Google Gemini API Key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY="your-gemini-api-key"
GEMINI_MODEL="gemini-3.8-flash"
PROJECT_NAME="AI Resume Analyzer"
API_V1_STR="/api/v1"
```

### 3. Run the Server
```bash
uv run uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Alternative ReDoc UI: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🔌 API Endpoints

### 1. `POST /api/v1/analyzer/analyze-file` (Multipart Form)
Uploads a resume file (`.pdf`, `.docx`, `.txt`) along with job description and self-description.

```bash
curl -X POST "http://localhost:8000/api/v1/analyzer/analyze-file" \
  -F "resume_file=@/path/to/resume.pdf" \
  -F "job_description=Backend Engineer with strong foundation in Python, Go and Kafka exeprtise." \
  -F "self_description=I have strong Python web experience and recently started diving into Generative AI."
```

### 2. `POST /api/v1/analyzer/analyze-text` (JSON Payload)
Directly sends extracted/raw text for analysis.

```bash
curl -X POST "http://localhost:8000/api/v1/analyzer/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Backend Engineer with strong foundation in FastAPI, Flask, PostgreSQL, C++ and GenAI fundamentals.",
    "job_description": "Backend Engineer with Python, Go, Kafka, and Kubernetes expertise.",
    "self_description": "Currently practicing distributed system design and diving deep into GenAI stack."
  }'
```

### 3. `POST /api/v1/analyzer/parse-file` (Multipart Form)
Extracts and normalizes text from a resume document without triggering LLM analysis.

---

## 🧪 Running Tests
```bash
uv run pytest
```
