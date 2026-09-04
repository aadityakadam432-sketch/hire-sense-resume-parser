# HireSense — Smart Resume Analysis & ATS Platform

A GitHub-ready HireSense that extracts structured information from PDF, DOCX and TXT resumes, stores results in SQLite, and calculates a resume quality / job-match score.

## Features

- PDF, DOCX and TXT parsing
- Email and phone extraction
- Name and links detection
- Skill extraction with categorized skills
- Education, experience, projects and certifications extraction
- Optional job-description skill matching
- Resume/ATS-style score
- Suggestions for improving a resume
- SQLite persistence and resume history
- JSON API endpoint: `POST /api/parse`
- Responsive Flask frontend

## Project Structure

```text
hiresense/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
├── parser/
│   ├── __init__.py
│   ├── resume_parser.py
│   └── scorer.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── resumes.html
├── static/
│   └── style.css
└── uploads/
    └── .gitkeep
```

## Setup

### 1. Create a virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## API

```bash
curl -X POST \
  -F "resume=@resume.pdf" \
  -F "job_description=Python SQL Power BI data analyst" \
  http://127.0.0.1:5000/api/parse
```

## Notes

This project intentionally uses transparent rule-based NLP/regex extraction so it can run locally without an AI API key. For production, consider adding OCR for scanned PDFs, a stronger NER model, authentication, virus scanning, background jobs, and encrypted storage.

## Resume/GitHub Project Description

**HireSense & ATS Analyzer** — Built a Flask-based web application that parses PDF/DOCX/TXT resumes, extracts candidate information and technical skills, stores structured data in SQLite, and calculates resume quality plus job-description skill-match scores.
