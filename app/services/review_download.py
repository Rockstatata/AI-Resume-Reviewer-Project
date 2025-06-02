from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def ensure_list(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, str):
        import re
        points = re.split(r"\n\d+\.\s*", "\n" + obj.strip())
        points = [p.strip() for p in points if p.strip()]
        if len(points) > 1:
            return points
        return [s.strip() for s in re.split(r"[\n;]", obj) if s.strip()]
    return []

def wrap_text(text, font, font_size, max_width, canvas_obj):
    """Wrap text for PDF based on actual string width in points."""
    lines = []
    for paragraph in text.splitlines():
        line = ''
        for word in paragraph.split():
            test_line = f"{line} {word}".strip()
            if canvas_obj.stringWidth(test_line, font, font_size) <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines

def generate_review_pdf(resume, score, suggestions, summary, pdf_path):
    suggestions = ensure_list(suggestions)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    margin = 40
    max_width = width - 2 * margin

    y = height - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, f"AI Resume Review for: {resume.filename}")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(margin, y, f"Score: {score if score is not None else 'N/A'}")
    y -= 25
    c.drawString(margin, y, "Suggestions:")
    y -= 20
    for idx, suggestion in enumerate(suggestions, 1):
        wrapped_lines = wrap_text(f"{idx}. {suggestion}", "Helvetica", 12, max_width-20, c)
        for line in wrapped_lines:
            c.drawString(margin + 20, y, line)
            y -= 18
            if y < margin:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - margin
    y -= 10
    c.drawString(margin, y, "Summary:")
    y -= 20
    for line in wrap_text(summary or "", "Helvetica", 12, max_width-20, c):
        c.drawString(margin + 20, y, line)
        y -= 15
        if y < margin:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - margin
    c.save()