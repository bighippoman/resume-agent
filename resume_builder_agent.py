"""
Resume Builder Agent – v2.1
Adds Pydantic schema validation for safer JSON handling.
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
from typing import List
import tempfile, os, shutil, zipfile, smtplib, json, logging
from email.message import EmailMessage
import docx2txt
import fitz

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
SYSTEM:\nYou are “ResumeRevamp-GPT”, a former Fortune‑500 recruiter.\n\nRULES:\n1. Do not fabricate education, employers, dates, or metrics.\n2. Use only facts that appear in either the candidate résumé (below) or the job description.\n3. Each bullet must begin with an action verb, include a metric, and finish with a skill or tool.\n4. Tone = {tone}. Acceptable values: formal | modern | confident | impactful.\n5. \u22646 bullets per job, \u226415 words per bullet.\n6. Return **valid JSON only** matching the schema – no markdown, no comments.\n\nSCHEMA:\n{\n  \"header\": {\"name\":\"\", \"email\":\"\", \"phone\":\"\"},\n  \"summary\": \"\",\n  \"experience\": [\n     {\"title\":\"\", \"company\":\"\", \"dates\":\"\", \"bullets\":[\"\"]}\n  ],\n  \"education\": [\n     {\"degree\":\"\", \"institution\":\"\", \"dates\":\"\"}\n  ],\n  \"skills\": [\"\"]\n}\n\n[JOB DESCRIPTION]\n{job_desc}\n\n[CANDIDATE RÉSUMÉ]\n{resume_data}\n"""
)

cover_prompt = PromptTemplate(
    input_variables=["resume_data", "job_desc", "tone", "company_name", "recipient_name"],
    template="""
SYSTEM: You are “CoverCraft-GPT”, a career coach who crafts concise, story‑driven cover letters.\n\nINSTRUCTIONS:\n1. 250–300 words, four paragraphs (hook, alignment, value, close).\n2. Mirror 5–7 keywords from the job description verbatim.\n3. Mention ONE achievement from the résumé.\n4. Close with a polite call‑to‑action.\n\nRecipient = {recipient_name or \"Hiring Manager\"}\nCompany  = {company_name or \"your organisation\"}\nTone     = {tone}\n\n[JOB DESCRIPTION]\n{job_desc}\n\n[RÉSUMÉ]\n{resume_data}\n"""
)

# ───────────────────────── UTILITIES ──────────────────────────

def style_doc(doc: DocxDocument):
    font = doc.styles['Normal'].font
    font.name = 'Georgia'
    font.size = Pt(11)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

def extract_text(file: UploadFile) -> str:
    suffix = file.filename.split('.')[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        path = tmp.name
    try:
        if suffix == 'pdf':
            text = "\n".join([page.get_text() for page in fitz.open(path)])
        elif suffix in ['docx', 'doc']:
            text = docx2txt.process(path)
        elif suffix == 'txt':
            text = open(path, 'r', encoding='utf-8').read()
        else:
            text = ""
    finally:
        os.unlink(path)
    return text

# ───────────────────────── LLM CALLS ──────────────────────────

def build_resume_struct(resume_data: str, job_desc: str, tone: str = 'confident') -> dict:
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.4)
    raw_json = LLMChain(llm=llm, prompt=resume_prompt).run({
        'resume_data': resume_data,
        'job_desc': job_desc,
        'tone': tone
    })
    try:
        struct = json.loads(raw_json)
        # Validate against schema
        ResumeJSON(**struct)
    except (json.JSONDecodeError, ValidationError) as e:
        logging.error(f"Schema validation failed: {e}")
        struct = {"raw": raw_json}
    return struct

def build_cover_letter(resume_data: str, job_desc: str, tone: str, company_name: str, recipient_name: str) -> str:
    if not recipient_name.strip():
        recipient_name = "Hiring Manager"
    if not company_name.strip():
        company_name = ""
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)
    return LLMChain(llm=llm, prompt=cover_prompt).run({
        'resume_data': resume_data,
        'job_desc': job_desc,
        'tone': tone,
        'company_name': company_name,
        'recipient_name': recipient_name
    })

# ───────────────────────── DOCX BUILDERS ──────────────────────────

def docx_from_struct(data: dict) -> DocxDocument:
    doc = DocxDocument()
    style_doc(doc)

    header = data.get('header', {})
    doc.add_paragraph(header.get('name', '')).bold = True
    contact_line = " | ".join(filter(None, [
        f"Email: {header.get('email', '')}" if header.get('email') else '',
        f"Phone: {header.get('phone', '')}" if header.get('phone') else ''
    ]))
    if contact_line:
        doc.add_paragraph(contact_line)

    if summary := data.get('summary'):
        doc.add_paragraph('')
        doc.add_heading('Professional Summary', level=2)
        doc.add_paragraph(summary.strip())

    if exps := data.get('experience'):
        doc.add_paragraph('')
        doc.add_heading('Experience', level=2)
        for role in exps:
            title_line = f"{role.get('title', '')} – {role.get('company', '')} ({role.get('dates', '')})"
            doc.add_paragraph(title_line).bold = True
            for b in role.get('bullets', []):
                if b.strip():
                    doc.add_paragraph(b.strip(), style='List Bullet')

    if edus := data.get('education'):
        doc.add_paragraph('')
        doc.add_heading('Education', level=2)
        for ed in edus:
            edu_line = f"{ed.get('degree', '')}, {ed.get('institution', '')} ({ed.get('dates', '')})"
            doc.add_paragraph(edu_line)

    if skills := data.get('skills'):
        doc.add_paragraph('')
        doc.add_heading('Skills', level=2)
        doc.add_paragraph(', '.join(skills))

    return doc

# ───────────────────────── EMAIL ──────────────────────────

def email_resume_package(to: str, from_email: str, subject: str, message: str, attachments: List[str]):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to
    msg.set_content(message)
    for path in attachments:
        with open(path, 'rb') as f:
            msg.add_attachment(
                f.read(), maintype='application', subtype='octet-stream', filename=os.path.basename(path)
            )
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(os.getenv('SMTP_EMAIL'), os.getenv('SMTP_PASSWORD'))
        smtp.send_message(msg)

# ───────────────────────── ENDPOINT ──────────────────────────

@app.post('/rewrite')
async def rewrite_resume(
    resume: UploadFile = File(...),
    tone: str = Form(...),
    job_desc: str = Form(...),
    company_name: str = Form(...),
    recipient_name: str = Form(...),
    sender_name: str = Form(...),
    sender_email: str = Form(...),
    sender_phone: str = Form(...),
    email_to: str | None =
