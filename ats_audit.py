import re
from typing import List, Dict

def normalize_text(text: str) -> List[str]:
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if len(w) > 2]

def keyword_match_score(resume_text: str, job_text: str) -> Dict:
    resume_tokens = set(normalize_text(resume_text))
    job_tokens = set(normalize_text(job_text))

    matched = resume_tokens.intersection(job_tokens)
    missing = job_tokens - resume_tokens

    total = len(job_tokens)
    score = round((len(matched) / total) * 100, 2) if total else 0

    return {
        "score": score,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing)
    }

def audit_resume(resume_data: Dict, job_description: str) -> Dict:
    combined_text = []

    if "summary" in resume_data:
        combined_text.append(resume_data["summary"])

    for exp in resume_data.get("experience", []):
        combined_text.append(exp.get("title", ""))
        combined_text.append(exp.get("company", ""))
        combined_text.append(" ".join(exp.get("bullets", [])))

    for edu in resume_data.get("education", []):
        combined_text.append(edu.get("degree", ""))
        combined_text.append(edu.get("institution", ""))

    combined_text.extend(resume_data.get("skills", []))

    resume_flat = " ".join(combined_text)
    return keyword_match_score(resume_flat, job_description)
