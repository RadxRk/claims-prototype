"""
Generate TALK_TRACK.pdf from TALK_TRACK.md — printable speaker notes for the
20-minute customer presentation.

Run:
    .venv/bin/python scripts/build_talk_track_pdf.py
"""

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    HRFlowable,
)

# ─── Config ─────────────────────────────────────────────────────────────
SRC_PATH = Path(__file__).resolve().parent.parent / "TALK_TRACK.md"
OUT_PATH = Path(__file__).resolve().parent.parent / "TALK_TRACK.pdf"

INK = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#475569")
ACCENT = colors.HexColor("#1D4ED8")
SOFT_BG = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
NOTE_INK = colors.HexColor("#0F766E")
NOTE_BG = colors.HexColor("#F0FDFA")

styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "Title", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=24, leading=30, textColor=INK, alignment=TA_LEFT, spaceAfter=4,
)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=18, leading=22, textColor=INK, spaceBefore=14, spaceAfter=6,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=14, leading=18, textColor=ACCENT, spaceBefore=14, spaceAfter=6,
    keepWithNext=True,
)
H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"], fontName="Helvetica-Bold",
    fontSize=11.5, leading=15, textColor=INK, spaceBefore=10, spaceAfter=4,
    keepWithNext=True,
)
BODY = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10.5, leading=15, textColor=INK, spaceAfter=6,
)
BULLET = ParagraphStyle(
    "Bullet", parent=BODY, leftIndent=16, bulletIndent=4, spaceAfter=3,
)
NOTE = ParagraphStyle(
    "Note", parent=styles["Normal"], fontName="Helvetica-Oblique",
    fontSize=9.5, leading=13, textColor=NOTE_INK, spaceAfter=6,
    leftIndent=12, rightIndent=8,
    borderPadding=(4, 6, 4, 6),
    backColor=NOTE_BG,
    borderColor=NOTE_BG, borderWidth=0,
)


def md_inline_to_rml(text: str) -> str:
    """Convert markdown inline syntax to reportlab Paragraph markup."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" size="9.5">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", text)
    return text


def parse_markdown(md_text: str):
    """Convert the talk-track markdown into a list of reportlab flowables."""
    lines = md_text.splitlines()
    flowables: list = []
    in_quote_block: list[str] = []
    in_paragraph: list[str] = []

    def flush_paragraph():
        if in_paragraph:
            joined = " ".join(in_paragraph).strip()
            if joined:
                flowables.append(Paragraph(md_inline_to_rml(joined), BODY))
            in_paragraph.clear()

    def flush_quote():
        if in_quote_block:
            joined = " ".join(in_quote_block).strip()
            if joined:
                flowables.append(Paragraph(md_inline_to_rml(joined), NOTE))
            in_quote_block.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped == "---":
            flush_paragraph(); flush_quote()
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=0.4, color=BORDER, spaceBefore=2, spaceAfter=8))
            i += 1
            continue

        if stripped.startswith("# "):
            flush_paragraph(); flush_quote()
            flowables.append(Paragraph(md_inline_to_rml(stripped[2:].strip()), TITLE))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_paragraph(); flush_quote()
            flowables.append(Paragraph(md_inline_to_rml(stripped[3:].strip()), H2))
            i += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph(); flush_quote()
            flowables.append(Paragraph(md_inline_to_rml(stripped[4:].strip()), H3))
            i += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            content = stripped[1:].lstrip()
            in_quote_block.append(content)
            i += 1
            continue
        else:
            flush_quote()

        m_num = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m_num:
            flush_paragraph()
            num, text = m_num.group(1), m_num.group(2)
            flowables.append(Paragraph(f"{num}. {md_inline_to_rml(text)}", BULLET))
            i += 1
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            flowables.append(Paragraph(f"• {md_inline_to_rml(stripped[2:])}", BULLET))
            i += 1
            continue

        if stripped == "":
            flush_paragraph()
            i += 1
            continue

        in_paragraph.append(stripped)
        i += 1

    flush_paragraph(); flush_quote()
    return flowables


def add_page_chrome(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(letter[0] - 0.5 * inch, 0.5 * inch, f"Page {canvas.getPageNumber()}")
    canvas.drawString(0.5 * inch, 0.5 * inch, "Customer presentation talk track · 20 min")
    canvas.restoreState()


def main():
    md_text = SRC_PATH.read_text()
    flowables = parse_markdown(md_text)
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.7 * inch,
        title="Customer presentation talk track",
        author="Solutions Engineering",
    )
    doc.build(flowables, onFirstPage=add_page_chrome, onLaterPages=add_page_chrome)
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
