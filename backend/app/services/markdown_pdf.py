import io
import re
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

# Private-use sentinel that shields inline code spans from emphasis parsing.
_CODE_SENTINEL = chr(0xE000)
_HRULE = re.compile(r"([-*_])\1{2,}$")
_HEADING = re.compile(r"(#{1,4})\s+(.*)")
_BULLET = re.compile(r"[-*+]\s+(.*)")
# The digit run is bounded: an unbounded \d+ backtracks once per digit when the
# trailing "." is absent, so a long run of digits in user-supplied Markdown costs
# time proportional to its length (CodeQL py/polynomial-redos).
_ORDERED = re.compile(r"\d{1,9}\.\s+(.*)")


def _inline(text: str) -> str:
    """Convert inline Markdown (bold, italic, inline code, links) into the small
    HTML-like markup ReportLab's Paragraph understands. Special characters are
    escaped first so raw ``<``, ``>`` and ``&`` render literally rather than
    breaking the paragraph parser."""
    text = escape(text)

    codes: list[str] = []

    def _stash(match: re.Match) -> str:
        codes.append(match.group(1))
        return f"{_CODE_SENTINEL}{len(codes) - 1}{_CODE_SENTINEL}"

    # Pull code spans out first so their contents are not treated as emphasis.
    text = re.sub(r"`([^`]+)`", _stash, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2" color="#2563eb">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<i>\1</i>", text)

    def _restore(match: re.Match) -> str:
        return f'<font face="Courier">{codes[int(match.group(1))]}</font>'

    return re.sub(rf"{_CODE_SENTINEL}(\d+){_CODE_SENTINEL}", _restore, text)


def markdown_to_pdf(markdown_text: str) -> bytes:
    """Render Markdown (headings, bullet/numbered lists, fenced code blocks,
    paragraphs, and inline bold/italic/code/links) to a PDF and return the
    bytes. Inline markers are converted to styled runs rather than emitted
    literally."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()

    code_style = ParagraphStyle(
        "MdCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=10,
        leftIndent=20,
        backgroundColor=colors.lightgrey,
    )
    heading_styles = {
        1: styles["Title"],
        2: styles["Heading2"],
        3: styles["Heading3"],
        4: styles["Heading4"],
    }

    story: list = []
    items: list[ListItem] = []
    item_type: str | None = None  # "bullet" or "ordered"
    in_code = False
    code_buffer: list[str] = []

    def flush_list() -> None:
        nonlocal items, item_type
        if items:
            kwargs = (
                {"bulletType": "1", "bulletFormat": "%s."}
                if item_type == "ordered"
                else {"bulletType": "bullet"}
            )
            story.append(ListFlowable(items, leftIndent=35, spaceBefore=8, spaceAfter=8, **kwargs))
        items = []
        item_type = None

    def flush_code() -> None:
        nonlocal code_buffer
        if code_buffer:
            story.append(Preformatted(escape("\n".join(code_buffer)), code_style))
        code_buffer = []

    for raw in markdown_text.split("\n"):
        line = raw.strip()

        if line.startswith("```"):
            if in_code:
                flush_code()
            in_code = not in_code
            continue
        if in_code:
            code_buffer.append(raw)
            continue

        if not line:
            flush_list()
            story.append(Spacer(1, 6))
            continue
        if _HRULE.match(line):
            flush_list()
            continue

        heading = _HEADING.match(line)
        bullet = _BULLET.match(line)
        ordered = _ORDERED.match(line)
        if heading:
            flush_list()
            story.append(
                Paragraph(_inline(heading.group(2)), heading_styles[len(heading.group(1))])
            )
        elif bullet:
            if item_type == "ordered":
                flush_list()
            item_type = "bullet"
            items.append(ListItem(Paragraph(_inline(bullet.group(1)), styles["BodyText"])))
        elif ordered:
            if item_type == "bullet":
                flush_list()
            item_type = "ordered"
            items.append(ListItem(Paragraph(_inline(ordered.group(1)), styles["BodyText"])))
        else:
            flush_list()
            story.append(Paragraph(_inline(line), styles["Normal"]))

    flush_list()
    flush_code()  # tolerate an unterminated code fence
    doc.build(story)
    return buf.getvalue()


def pdf_to_markdown(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text_parts: list[str] = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "".join(text_parts)
