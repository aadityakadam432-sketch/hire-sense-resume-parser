import re

COMMON_SKILLS = sorted({
    "python","java","c","c++","javascript","typescript","sql","excel","power bi",
    "tableau","pandas","numpy","matplotlib","seaborn","machine learning","deep learning",
    "nlp","tensorflow","pytorch","scikit-learn","html","css","react","node.js","flask",
    "django","fastapi","mysql","postgresql","mongodb","sqlite","aws","azure","gcp",
    "docker","kubernetes","git","github","linux","rest api","data analysis","statistics"
})

def normalize(s):
    return re.sub(r"\s+", " ", s.lower().strip())

def score_resume(parsed, job_description=""):
    # General quality score: presence of contact, sections, skills, links.
    checks = [
        bool(parsed.get("name")),
        bool(parsed.get("email")),
        bool(parsed.get("phone")),
        bool(parsed.get("education")),
        bool(parsed.get("experience")),
        bool(parsed.get("projects")),
        bool(parsed.get("skills")),
        bool(parsed.get("certifications")),
    ]
    base = round(sum(checks) / len(checks) * 70)

    jd_score = None
    matched = []
    missing = []
    if job_description:
        jd = normalize(job_description)
        resume_skills = {normalize(s) for s in parsed.get("skills", [])}
        required = [s for s in COMMON_SKILLS if re.search(r"(?<![a-z0-9])" + re.escape(s) + r"(?![a-z0-9])", jd)]
        required = list(dict.fromkeys(required))
        matched = [s for s in required if s in resume_skills]
        missing = [s for s in required if s not in resume_skills]
        jd_score = round((len(matched) / len(required)) * 100) if required else 0

    final = round((base * 0.55) + ((jd_score or base) * 0.45))
    suggestions = []
    if not parsed.get("email"): suggestions.append("Add a professional email address.")
    if not parsed.get("phone"): suggestions.append("Add a phone number.")
    if not parsed.get("skills"): suggestions.append("Add a dedicated technical skills section.")
    if not parsed.get("projects"): suggestions.append("Add 1–3 relevant projects with measurable outcomes.")
    if not parsed.get("experience"): suggestions.append("Add internships, work experience, or relevant practical experience.")
    if not parsed.get("certifications"): suggestions.append("Add relevant certifications if you have them.")
    if missing:
        suggestions.append("Consider adding relevant skills: " + ", ".join(missing[:8]) + ".")

    return {
        "overall": max(0, min(100, final)),
        "base_score": base,
        "job_match_score": jd_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "suggestions": suggestions,
    }
