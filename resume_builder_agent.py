"""
Resume Builder Agent – v2.1 (full)
Adds Pydantic validation and fixes syntax truncation.
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from docx import Document as DocxDocument
from docx.shared import Pt, Inches
from docx2pdf import convert
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import List, Optional
import tempfile, os, shutil, zipfile, smtplib, json, logging
from email.message import EmailMessage
import docx2txt
import fitz

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ───────────────────────── Pydantic models ──────────────────────────
class ResumeHeader(BaseModel):
    name: str
    email: str
    phone: str

class ResumeExperience(BaseModel):
    title: str
    company: str
    dates: str
    bullets: List[str]

class ResumeEducation(BaseModel):
    degree: str
    institution: str
    dates: str

class ResumeJSON(BaseModel):
    header: ResumeHeader
    summary: str
    experience: List[ResumeExperience]
    education: List[ResumeEducation]
    skills: List[str]

# ───────────────────────── PROMPTS ──────────────────────────
resume_prompt = PromptTemplate(
    input_variables=["resume_data", "job_desc", "tone"],
    template="""
SYSTEM:
You are “ResumeRevamp-GPT”, a former Fortune‑500 recruiter.

RULES:
1. Do not fabricate education, employers, dates, or metrics.
2. Use only facts that appear in either the candidate résumé (below) or the job description.
3. Each bullet must begin with an action verb, include a metric, and finish with a skill or tool.
4. Tone = {tone}. Acceptable values: formal | modern | confident | impactful.
5. ≤6 bullets per job, ≤15 words per bullet.
6. Return **valid JSON only** matching the schema – no markdown, no commentary.

SCHEMA:
{
  "header": {"name":"", "email":"", "phone":""},
  "summary": "",
  "experience": [
    {"title":"", "company":"", "dates":"", "bullets":[""]}
  ],
  "education": [
    {"degree":"", "institution":"", "dates":""}
  ],
  "skills": [""]
}

[JOB DESCRIPTION]
{job_desc}

[CANDIDATE RÉSUMÉ]
{resume_data}
"""
)

cover_prompt = PromptTemplate(
    input_variables=["resume_data", "job_desc", "tone", "company_name", "recipient_name"],
    template="""
SYSTEM: You are “CoverCraft-GPT”, a career coach who crafts concise, story‑driven cover letters.

INSTRUCTIONS:
1. 250–300 words, four paragraphs (hook, alignment, value, close).
2. Mirror 5–7 keywords from the job description verbatim.
3. Mention ONE achievement from the résumé.
4. Close with a polite call‑to‑action.

Recipient = {recipient_name or "Hiring Manager"}
Company  = {company_name or "your organisation"}
Tone     = {tone}

[JOB DESCRIPTION]
{job_desc}

[RÉSUMÉ]
{resume_data}
"""
)

# ───────────────────────── UTILITIES ──────────────────────────

def style_doc(doc: DocxDocument) -> None:
    font = doc.styles["Normal"].font
    font.name = "Georgia"
    font.size = Pt(11)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

def extract_text(file: UploadFile) -> str:
    suffix = file.filename.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        path = tmp.name
    try:
        if suffix == "pdf":
            text = "\n".join(page.get_text() for page in fitz.open(path))
        elif suffix in {"docx", "doc"}:
            text = docx2txt.process(path)
        elif suffix == "txt":
            text = open(path, "r", encoding="utf-8").read()
        else:
            text = ""
    finally:
        os.unlink(path)
    return text

# ───────────────────────── LLM wrappers ──────────────────────────

def build_resume_struct(resume_data: str, job_desc: str, tone: str = "confident") -> dict:
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.4)
    raw_json = LLMChain(llm=llm, prompt=resume_prompt).run({
        "resume_data": resume_data,
        "job_desc": job_desc,
        "tone": tone
    })
    try:
        parsed = json.loads(raw_json)
        ResumeJSON(**parsed)  # validation
        return parsed
    except (json.JSONDecodeError, ValidationError) as err:
        logging.error(f"Schema validation failed: {err}")
        return {"raw": raw_json}

def build_cover_letter(resume_data: str, job_desc: str, tone: str, company: str, recipient: str) -> str:
    if not recipient.strip():
        recipient = "Hiring Manager"
    if not company.strip():
        company = ""
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)
    return LLMChain(llm=llm, prompt=cover_prompt).run({
        "resume_data": resume_data,
        "job_desc": job_desc,
        "tone": tone,
        "company_name": company,
        "recipient_name": recipient
    })

# ───────────────────────── DOCX builders ──────────────────────────

def docx_from_struct(data: dict) -> DocxDocument:
    doc = DocxDocument()
    style_doc(doc)

    header = data.get("header", {})
    doc.add_paragraph(header.get("name", "")).bold = True
    contact_bits = []
    if header.get("email"):
        contact_bits.append(f"Email: {header['email']}")
    if header.get("phone"):
        contact_bits.append(f"Phone: {header['phone']}")
    if contact_bits:
        doc.add_paragraph(" | ".join(contact_bits))

    if summary := data.get("summary"):
        doc.add_paragraph("")
        doc.add_heading("Professional Summary", level=2)
        doc.add_paragraph(summary.strip())

    if exp := data.get("experience"):
        doc.add_paragraph("")
        doc.add_heading("Experience", level=2)
        for role in exp:
            role_title = f"{role.get('title', '')} – {role.get('company', '')} ({role.get('dates', '')})"
            doc.add_paragraph(role_title).bold = True
            for b in role.get("bullets", []):
                if b.strip():
                    doc.add_paragraph(b.strip(), style="List Bullet")

    if edu := data.get("education"):
        doc.add_paragraph("")
        doc.add_heading("Education", level=2)
        for e in edu:
            edu_line = f"{e.get('degree', '')}, {e.get('institution', '')} ({e.get('dates', '')})"
            doc.add_paragraph(edu_line)

    if skills := data.get("skills"):
        doc.add_paragraph("")
        doc.add_heading("Skills", level=2)
        doc.add_paragraph(", ".join(skills))

    return doc

# ───────────────────────── Email helper ──────────────────────────

def email_resume_package(to_addr: str, from_addr: str, subject: str, body: str, attachments: List[str]):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)
    for path in attachments:
        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(), maintype="application", subtype="octet-stream", filename=os.path.basename(path)
            )
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)

# ───────────────────────── API endpoint ──────────────────────────

@app.post("/rewrite")
async def rewrite_resume(
    resume: UploadFile = File(...),
    tone: str = Form(...),
    job_desc: str = Form(...),
    company_name: str = Form(""),
    recipient_name: str = Form(""),
    sender_name: str = Form(...),
    sender_email: str = Form(...),
    sender_phone: str = Form(...),
    email_to: Optional[str] = Form(None),
    preview: str = Form("true")
):
    # 1) extract text
    resume_text = extract_text(resume)

    # 2) build LLM outputs
    resume_struct = build_resume_struct(resume_text, job_desc, tone)
    cover_text = build_cover_letter(resume_text, job_desc, tone, company_name, recipient_name)

    # 3) quick JSON preview route
    if preview.lower() == "true":
        return JSONResponse({
            "resume_json": resume_struct,
            "cover_letter": cover_text.strip()
        })

    # 4) build DOCX files
    if "raw" in resume_struct:
        resume_doc = DocxDocument()
        style_doc(resume_doc)
        resume_doc.add_paragraph(resume_struct["raw"])
    else:
        resume_doc = docx_from_struct(resume_struct)

    cover_doc = DocxDocument()
    style_doc(cover_doc)
    cover_doc.add_paragraph(sender_name).bold = True
    cover_doc.add_paragraph(f"Email: {sender_email} | Phone: {sender_phone}")
    cover_doc.add_paragraph("")
    for line in cover_text.split("\n"):
        if line.strip():
            cover_doc.add_paragraph(line.strip())

    # 5) write to temp dir and convert to PDF
    with tempfile.TemporaryDirectory() as tmpdir:
        res_path = os.path.join(tmpdir, "resume.docx")
        cov_path = os.path.join(tmpdir, "cover_letter.docx")
        zip_path = os.path.join(tmpdir, "resume_package.zip")

        resume_doc.save(res_path)
        cover_doc.save(cov_path)
        convert(res_path, res_path.replace(".docx", ".pdf"))
        convert(cov_path, cov_path.replace(".docx", ".pdf"))

        # 6) optional email
        if email_to:
            email_resume_package(
                to_addr=email_to,
                from_addr=sender_email,
                subject="Your Résumé + Cover Letter",
                body="Attached are your generated files.",
                attachments=[
                    res_path,
                    cov_path,
                    res_path.replace(".docx", ".pdf"),
                    cov_path.replace(".docx", ".pdf")
                ]
            )

        # 7) build ZIP for download
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(res_path, arcname="resume.docx")
            zf.write(cov_path, arcname="cover_letter.docx")
            zf.write(res_path.replace(".docx", ".pdf"), arcname="resume.pdf")
            zf.write(cov_path.replace(".docx", ".pdf"), arcname="cover_letter.pdf")

        return FileResponse(zip_path, media_type="application/zip", filename="resume_package.zip")

# ───────────────────────── Entrypoint ──────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("resume_builder_agent:app", host="0.0.0.0", port=10000, reload=False)
