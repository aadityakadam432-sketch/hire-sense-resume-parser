from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from parser.resume_parser import parse_resume
from parser.scorer import score_resume
from database import init_db, save_resume, get_resume, get_all_resumes
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
UPLOAD_FOLDER = os.path.join("uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/resumes")
def resumes():
    return render_template("resumes.html", resumes=get_all_resumes())

@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files:
        flash("Please select a resume.")
        return redirect(url_for("index"))

    file = request.files["resume"]
    if not file.filename:
        flash("Please select a resume.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only PDF, DOCX and TXT files are supported.")
        return redirect(url_for("index"))

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(filename))
    file.save(path)

    try:
        parsed = parse_resume(path)
        job_description = request.form.get("job_description", "").strip()
        score = score_resume(parsed, job_description)
        resume_id = save_resume(file.filename, parsed, score)
        return redirect(url_for("result", resume_id=resume_id))
    except Exception as exc:
        if os.path.exists(path):
            os.remove(path)
        flash(f"Could not parse the resume: {exc}")
        return redirect(url_for("index"))

@app.route("/result/<int:resume_id>")
def result(resume_id):
    resume = get_resume(resume_id)
    if not resume:
        return "Resume not found", 404
    return render_template("result.html", resume=resume)

@app.route("/api/parse", methods=["POST"])
def api_parse():
    if "resume" not in request.files:
        return jsonify({"error": "resume file is required"}), 400
    file = request.files["resume"]
    if not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "PDF, DOCX and TXT files are supported"}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(filename))
    file.save(path)
    try:
        parsed = parse_resume(path)
        jd = request.form.get("job_description", "").strip()
        return jsonify({"data": parsed, "score": score_resume(parsed, jd)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    finally:
        if os.path.exists(path):
            os.remove(path)

@app.errorhandler(413)
def too_large(_):
    return "File too large. Maximum size is 5 MB.", 413

if __name__ == "__main__":
    app.run(debug=True)
