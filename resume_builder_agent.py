from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from docx import Document as DocxDocument
from docx.shared import Pt, Inches
from docx2pdf import convert
from dotenv import load_dotenv
import tempfile, os, shutil, zipfile, smtplib
from email.message import EmailMessage
import docx2txt
import fitz
import tiktoken

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

embedding_model = OpenAIEmbeddings()
vectorstore = FAISS.load_local("resume_lines_faiss_index", embedding_model, allow_dangerous_deserialization=True)

resume_prompt = PromptTemplate(
    input_variables=["resume_text", "job_desc", "retrieved_lines", "retrieved_count", "tone"],
    template="""
You are an expert resume coach.
The user is applying for the following role:
[JOB DESCRIPTION]
{job_desc}

Here is the user's current resume:
[RESUME TEXT]
{resume_text}

You may use inspiration from these top {retrieved_count} strong resume bullet points:
[EXAMPLE BULLETS]
{retrieved_lines}

Please revise only the most important bullet points in the resume.
Focus on aligning with the job description using relevant skills, action verbs, and achievements.
Use a tone that is {tone}. Output only the revised bullet points in bullet format.
"""
)

cover_prompt = PromptTemplate(
    input_variables=["resume_text", "job_desc", "tone", "company_name", "recipient_name"],
    template="""
You are a professional career assistant.
Based on the following resume:
{resume_text}
And this job description:
{job_desc}
Write a tailored cover letter in a {tone} tone.
Address it to {recipient_name} at {company_name}.
If recipient_name is empty, address it to "Dear Hiring Manager".
If company_name is empty, simply reference the role and industry.
"""
)

def build_resume_prompt_safe(resume_text, job_desc, retrieved_docs, tone="confident", model_name="gpt-4o-mini", max_input_tokens=6000):
    encoding = tiktoken.encoding_for_model(model_name)
    base_tokens = len(encoding.encode(resume_text + job_desc))
    safe_lines, token_total = [], base_tokens
    for doc in retrieved_docs:
        line = doc.page_content.strip()
        line_tokens = len(encoding.encode(line))
        if token_total + line_tokens > max_input_tokens:
            break
        safe_lines.append(line)
        token_total += line_tokens
    input_data = {
        "resume_text": resume_text,
        "job_desc": job_desc,
        "retrieved_lines": "\n".join(safe_lines),
        "retrieved_count": len(safe_lines),
        "tone": tone
    }
    llm = ChatOpenAI(model_name=model_name, temperature=0.5)
    return LLMChain(llm=llm, prompt=resume_prompt).run(input_data)

def build_cover_letter(resume_text, job_desc, tone, company_name, recipient_name):
    if not recipient_name.strip(): recipient_name = "Dear Hiring Manager"
    if not company_name.strip(): company_name = ""
    return LLMChain(
        llm=ChatOpenAI(model_name="gpt-4", temperature=0.5),
        prompt=cover_prompt
    ).run({
        "resume_text": resume_text,
        "job_desc": job_desc,
        "tone": tone,
        "company_name": company_name,
        "recipient_name": recipient_name
    })

def style_doc(doc):
    font = doc.styles['Normal'].font
    font.name = 'Georgia'; font.size = Pt(11)
    for section in doc.sections:
        section.top_margin = Inches(0.75); section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(1.0); section.right_margin = Inches(1.0)

def extract_text(file: UploadFile):
    suffix = file.filename.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        path = tmp.name
    if suffix == "pdf":
        text = "\n".join([page.get_text() for page in fitz.open(path)])
    elif suffix in ["docx", "doc"]:
        text = docx2txt.process(path)
    elif suffix == "txt":
        text = open(path, "r", encoding="utf-8").read()
    else:
        text = ""
    os.unlink(path)
    return text

def email_resume_package(to, from_email, subject, message, attachments):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to
    msg.set_content(message)
    for path in attachments:
        with open(path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=os.path.basename(path))
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        smtp.send_message(msg)

@app.post("/rewrite")
async def rewrite_resume(
    resume: UploadFile = File(...),
    tone: str = Form(...),
    job_desc: str = Form(...),
    company_name: str = Form(...),
    recipient_name: str = Form(...),
    sender_name: str = Form(...),
    sender_email: str = Form(...),
    sender_phone: str = Form(...),
    email_to: str = Form(None),
    preview: str = Form("true")
):
    resume_text = extract_text(resume)
    retrieved_docs = vectorstore.similarity_search(job_desc, k=20)
    resume_result = build_resume_prompt_safe(resume_text, job_desc, retrieved_docs, tone=tone)
    cover_result = build_cover_letter(resume_text, job_desc, tone, company_name, recipient_name)

    if preview.lower() == "true":
        return JSONResponse({
            "resume_text": resume_result.strip(),
            "cover_letter": cover_result.strip()
        })

    resume_doc = DocxDocument(); style_doc(resume_doc)
    resume_doc.add_paragraph(sender_name).bold = True
    resume_doc.add_paragraph(f"Email: {sender_email} | Phone: {sender_phone}")
    resume_doc.add_paragraph(""); resume_doc.add_heading("Rewritten Resume Bullets", level=1)
    for line in resume_result.splitlines():
        clean = line.lstrip("-•\u2022* ").strip()
        if clean: resume_doc.add_paragraph(clean, style='List Bullet')

    cover_doc = DocxDocument(); style_doc(cover_doc)
    cover_doc.add_paragraph(sender_name).bold = True
    cover_doc.add_paragraph(f"Email: {sender_email} | Phone: {sender_phone}")
    cover_doc.add_paragraph(""); cover_doc.add_heading("Cover Letter", level=1)
    for paragraph in cover_result.split("\n"):
        if paragraph.strip(): cover_doc.add_paragraph(paragraph.strip())

    with tempfile.TemporaryDirectory() as temp_dir:
        resume_path = os.path.join(temp_dir, "resume.docx")
        cover_path = os.path.join(temp_dir, "cover_letter.docx")
        zip_path = os.path.join(temp_dir, "resume_package.zip")

        resume_doc.save(resume_path); cover_doc.save(cover_path)
        convert(resume_path, resume_path.replace(".docx", ".pdf"))
        convert(cover_path, cover_path.replace(".docx", ".pdf"))

        if email_to:
            email_resume_package(
                to=email_to, from_email=sender_email,
                subject="Your Resume + Cover Letter Package",
                message="Attached are your generated files.",
                attachments=[
                    resume_path,
                    cover_path,
                    resume_path.replace(".docx", ".pdf"),
                    cover_path.replace(".docx", ".pdf")
                ]
            )

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(resume_path)
            zipf.write(cover_path)
            zipf.write(resume_path.replace(".docx", ".pdf"))
            zipf.write(cover_path.replace(".docx", ".pdf"))

        return FileResponse(zip_path, media_type="application/zip", filename="resume_package.zip")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("resume_builder_agent:app", host="0.0.0.0", port=10000)# Placeholder for resume_builder_agent.py content

