"""Text extraction, contact info and section detection."""
import io
import re

SECTION_ALIASES = {
    "education": ["education", "academic background", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "experience": ["experience", "work experience", "employment", "internships", "internship"],
    "projects": ["projects", "academic projects", "personal projects"],
    "summary": ["summary", "objective", "profile", "about me"],
    "certifications": ["certifications", "certificates", "achievements", "awards"],
}


def extract_text(data: bytes, filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages).strip()
    if name.endswith(".docx"):
        import docx
        d = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in d.paragraphs).strip()
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore").strip()
    raise ValueError("Unsupported file type. Use PDF, DOCX or TXT.")


def extract_contact(text: str) -> dict:
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = re.search(r"(\+?\d[\d\s().-]{8,}\d)", text)
    linkedin = re.search(r"linkedin\.com/in/[\w-]+", text, re.I)
    github = re.search(r"github\.com/[\w-]+", text, re.I)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return {
        "name": lines[0] if lines else "",
        "email": email.group(0) if email else "",
        "phone": phone.group(0).strip() if phone else "",
        "linkedin": linkedin.group(0) if linkedin else "",
        "github": github.group(0) if github else "",
    }


def detect_sections(text: str) -> dict:
    """Split resume into sections by heading lines. Returns {section: text}."""
    lookup = {a: k for k, v in SECTION_ALIASES.items() for a in v}
    sections, current = {}, None
    for line in text.splitlines():
        key = re.sub(r"[^a-z ]", "", line.strip().lower()).strip()
        if key in lookup and len(line.strip()) < 40:
            current = lookup[key]
            sections.setdefault(current, [])
        elif current:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}
