import io

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def _flush_list(items: list[ListItem], story: list) -> list[ListItem]:
    if items:
        story.append(
            ListFlowable(
                items, bulletType="bullet", leftIndent=35, spaceBefore=10, spaceAfter=10
            )
        )
    return []


def markdown_to_pdf(markdown_text: str) -> bytes:
    """Render the supported subset of Markdown (#/##/### headings, - / * bullet lists,
    fenced ``` code blocks, paragraphs) to a PDF and return the bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()

    code_style = ParagraphStyle(
        "Code",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=10,
        leftIndent=20,
        backgroundColor=colors.lightgrey,
    )

    story: list = []
    list_items: list[ListItem] = []
    in_code = False
    code_buffer: list[str] = []

    for line in markdown_text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            if not in_code and code_buffer:
                story.append(Paragraph("\n".join(code_buffer), code_style))
                code_buffer = []
            continue

        if in_code:
            code_buffer.append(line)
            continue

        if line.strip():
            if line.startswith("# "):
                list_items = _flush_list(list_items, story)
                story.append(Paragraph(line[2:], styles["Title"]))
            elif line.startswith("## "):
                list_items = _flush_list(list_items, story)
                story.append(Paragraph(line[3:], styles["Heading2"]))
            elif line.startswith("### "):
                list_items = _flush_list(list_items, story)
                story.append(Paragraph(line[4:], styles["Heading3"]))
            elif line.startswith("- ") or line.startswith("* "):
                list_items.append(ListItem(Paragraph(line[2:], styles["BodyText"])))
            else:
                list_items = _flush_list(list_items, story)
                story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 6))

    _flush_list(list_items, story)
    doc.build(story)
    return buf.getvalue()


def pdf_to_markdown(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text_parts: list[str] = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "".join(text_parts)
