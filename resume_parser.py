import re
from pathlib import Path

SKILL_GROUPS = {
    "Programming": ["python", "java", "c", "c++", "javascript", "typescript", "go", "r", "php"],
    "Data & Analytics": ["sql", "excel", "power bi", "tableau", "pandas", "numpy", "matplotlib", "seaborn", "statistics", "data analysis"],
    "Web": ["html", "css", "react", "node.js", "nodejs", "flask", "django", "fastapi", "rest api"],
    "Databases": ["mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "linux"],
    "AI & ML": ["machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "scikit-learn", "opencv"],
}

CERT_KEYWORDS = ["certified", "certification", "certificate", "coursera", "udemy", "google", "microsoft", "aws"]

def extract_text(path):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        import fitz
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    if ext == ".docx":
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def clean_text(text):
    return re.sub(r"[ \t]+", " ", text.replace("\x00", " ")).strip()

def extract_email(text):
    m = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I)
    return m.group(0) if m else ""

def extract_phone(text):
    patterns = [
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        r"(?<!\d)\+?\d[\d\s().-]{8,}\d(?!\d)"
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return re.sub(r"\s+", " ", m.group(0)).strip()
    return ""

def extract_links(text):
    urls = re.findall(r"(?:https?://|www\.)\S+", text, re.I)
    return [u.rstrip(".,);]") for u in urls]

def extract_name(text, email):
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines() if x.strip()]
    bad = {"resume", "curriculum vitae", "cv", "profile", "summary", "objective"}
    for line in lines[:12]:
        if email and email in line:
            candidate = line.replace(email, "").strip(" -|,:")
        else:
            candidate = line
        words = candidate.split()
        if 2 <= len(words) <= 5 and all(re.fullmatch(r"[A-Za-z.'-]+", w) for w in words):
            if candidate.lower() not in bad:
                return candidate
    return ""

def extract_skills(text):
    lower = text.lower()
    found = {}
    for group, skills in SKILL_GROUPS.items():
        hits = []
        for skill in skills:
            pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
            if re.search(pattern, lower):
                hits.append(skill)
        if hits:
            found[group] = sorted(set(hits))
    flat = sorted({s for values in found.values() for s in values})
    return found, flat

def extract_section(text, headings):
    pattern = r"(?is)(?:^|\n)\s*(?:" + "|".join(map(re.escape, headings)) + r")\s*:?\s*\n?(.*?)(?=\n\s*(?:education|experience|work experience|employment|skills|technical skills|projects|certifications|achievements|summary|objective|profile|contact)\s*:?\s*(?:\n|$)|\Z)"
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""

def extract_education(text):
    section = extract_section(text, ["education", "academic background", "qualifications"])
    return [x.strip(" •-\t") for x in section.splitlines() if x.strip()][:10]

def extract_experience(text):
    section = extract_section(text, ["experience", "work experience", "employment", "professional experience"])
    return [x.strip(" •-\t") for x in section.splitlines() if x.strip()][:15]

def extract_projects(text):
    section = extract_section(text, ["projects", "academic projects", "personal projects"])
    return [x.strip(" •-\t") for x in section.splitlines() if x.strip()][:15]

def extract_certifications(text):
    section = extract_section(text, ["certifications", "certificates", "licenses"])
    lines = [x.strip(" •-\t") for x in section.splitlines() if x.strip()]
    if lines:
        return lines[:10]
    return [line.strip() for line in text.splitlines()
            if any(k in line.lower() for k in CERT_KEYWORDS)][:10]

def parse_resume(path):
    raw = extract_text(path)
    text = clean_text(raw)
    email = extract_email(text)
    skills_by_group, skills = extract_skills(text)
    return {
        "name": extract_name(text, email),
        "email": email,
        "phone": extract_phone(text),
        "links": extract_links(text),
        "skills": skills,
        "skills_by_group": skills_by_group,
        "education": extract_education(raw),
        "experience": extract_experience(raw),
        "projects": extract_projects(raw),
        "certifications": extract_certifications(raw),
        "text_preview": text[:1500],
    }
