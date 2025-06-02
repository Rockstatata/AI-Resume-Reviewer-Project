import io
from pdfminer.high_level import extract_text
from docx import Document

def parse_resume_file(filename: str, content: bytes) -> str:
    if filename.endswith(".pdf"):
        return extract_text(io.BytesIO(content))
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""