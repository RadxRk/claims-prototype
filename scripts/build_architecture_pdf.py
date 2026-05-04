"""
Generate ARCHITECTURE.pdf — a printable architecture overview of the
Insurance Claims Analyzer prototype. Uses reportlab Platypus + Drawing.

Run:
    .venv/bin/python scripts/build_architecture_pdf.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    Image,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader

# ─── Config ─────────────────────────────────────────────────────────────
OUT_PATH = Path(__file__).resolve().parent.parent / "ARCHITECTURE.pdf"

INK = colors.HexColor("#0F172A")        # near-black text
MUTED = colors.HexColor("#475569")
ACCENT = colors.HexColor("#1D4ED8")     # blue
SOFT_BG = colors.HexColor("#F1F5F9")    # cool grey 100
BORDER = colors.HexColor("#CBD5E1")
AMBER_BG = colors.HexColor("#FEF3C7")
AMBER_BORDER = colors.HexColor("#F59E0B")
GREEN_BG = colors.HexColor("#DCFCE7")
ROW_ALT = colors.HexColor("#F8FAFC")

styles = getSampleStyleSheet()

# Custom paragraph styles
TITLE_STYLE = ParagraphStyle(
    "TitleHero",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=28,
    leading=34,
    textColor=INK,
    alignment=TA_LEFT,
    spaceAfter=4,
)
SUBTITLE_STYLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=14,
    leading=18,
    textColor=MUTED,
    spaceAfter=2,
)
META_STYLE = ParagraphStyle(
    "Meta",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=12,
    textColor=MUTED,
)
H1 = ParagraphStyle(
    "H1Section",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=20,
    textColor=ACCENT,
    spaceBefore=14,
    spaceAfter=8,
)
H2 = ParagraphStyle(
    "H2Sub",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=15,
    textColor=INK,
    spaceBefore=10,
    spaceAfter=4,
)
BODY = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=14,
    textColor=INK,
    spaceAfter=4,
)
CODE = ParagraphStyle(
    "InlineCode",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=9,
    leading=12,
    textColor=INK,
)
CAPTION = ParagraphStyle(
    "Caption",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=9,
    leading=11,
    textColor=MUTED,
    spaceAfter=10,
)


# ─── System diagram ─────────────────────────────────────────────────────
def system_diagram() -> Drawing:
    """Boxes-and-arrows architecture diagram rendered with reportlab.graphics."""
    W, H = 540, 470
    d = Drawing(W, H)

    def box(x, y, w, h, title, items, fill=SOFT_BG, border=BORDER, title_color=INK):
        d.add(Rect(x, y, w, h, strokeColor=border, strokeWidth=1, fillColor=fill, rx=4, ry=4))
        d.add(String(x + 8, y + h - 16, title, fontName="Helvetica-Bold", fontSize=10, fillColor=title_color))
        for i, item in enumerate(items):
            d.add(String(x + 12, y + h - 32 - 12 * i, "• " + item, fontName="Helvetica", fontSize=8.5, fillColor=INK))

    def arrow(x1, y1, x2, y2, label="", side="left"):
        d.add(Line(x1, y1, x2, y2, strokeColor=MUTED, strokeWidth=1.2))
        # arrowhead
        if y2 < y1:  # downward
            d.add(Polygon([x2 - 4, y2 + 6, x2 + 4, y2 + 6, x2, y2], strokeColor=MUTED, fillColor=MUTED))
        else:  # upward
            d.add(Polygon([x2 - 4, y2 - 6, x2 + 4, y2 - 6, x2, y2], strokeColor=MUTED, fillColor=MUTED))
        if label:
            lx = (x1 + x2) / 2 + (8 if side == "right" else -100)
            ly = (y1 + y2) / 2
            d.add(String(lx, ly, label, fontName="Helvetica-Oblique", fontSize=7.5, fillColor=MUTED))

    # ── Browser layer (top)
    d.add(Rect(10, 330, 520, 130, strokeColor=BORDER, strokeWidth=1, fillColor=colors.white, rx=6, ry=6))
    d.add(String(20, 444, "BROWSER", fontName="Helvetica-Bold", fontSize=9, fillColor=MUTED))

    box(25, 345, 160, 90, "Upload Card", ["File picker", "Sample gallery", "Image preview"])
    box(195, 345, 160, 90, "Live Status", ["Phase events", "Streaming checklist", "Pulse indicator"])
    box(365, 345, 160, 90, "Results Panel", ["Vehicle / Damage / Cost", "Review banner (typed)", "Image quality"])

    # ── HTTP boundary arrows
    arrow(110, 340, 110, 305, "POST FormData", side="left")
    arrow(285, 305, 285, 340, "SSE: status + complete", side="right")

    # ── Server layer (middle)
    d.add(Rect(10, 175, 520, 130, strokeColor=BORDER, strokeWidth=1, fillColor=ROW_ALT, rx=6, ry=6))
    d.add(String(20, 289, "SERVER (Next.js)", fontName="Helvetica-Bold", fontSize=9, fillColor=MUTED))

    box(
        25, 185, 500, 95,
        "/api/analyze (Server-Sent Events endpoint)",
        [
            "1. Parse multipart upload",
            "2. Image preprocess: resize ≤ 2576px, strip EXIF (PII)",
            "3. Upload to Anthropic Files API → file_id",
            "4. Stream Claude analysis (Sonnet 4.6)",
            "5. Validate output (Zod) + 6. Compute typed Triggers + 7. Send complete event",
        ],
    )

    # ── External arrows
    arrow(160, 180, 160, 145, "store image", side="left")
    arrow(390, 180, 390, 145, "vision + reasoning", side="right")

    # ── External services (bottom)
    box(
        25, 25, 240, 120,
        "Anthropic Files API",
        [
            "Image stored by file_id",
            "Persists across calls",
            "PII-free (we strip EXIF",
            "before upload)",
        ],
        fill=GREEN_BG,
        border=colors.HexColor("#16A34A"),
    )

    box(
        285, 25, 240, 120,
        "Claude Sonnet 4.6",
        [
            "Vision (the image)",
            "System prompt (adjuster persona +",
            "  reference cost table)",
            "Structured outputs (JSON schema)",
            "Adaptive thinking + effort: low",
            "Streaming",
        ],
        fill=AMBER_BG,
        border=AMBER_BORDER,
    )

    return d


# Body cell paragraph style — used to wrap long strings so they auto-wrap
# within their column width instead of overflowing the right margin.
CELL_STYLE = ParagraphStyle(
    "Cell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=INK,
)


def _cell(value):
    """Wrap plain strings in a Paragraph so the cell auto-wraps."""
    if isinstance(value, str):
        # escape XML-significant chars so things like "→" or "&" render correctly
        safe = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return Paragraph(safe, CELL_STYLE)
    return value


# ─── Tables ─────────────────────────────────────────────────────────────
def make_table(rows, col_widths, header=True):
    # Header row stays as plain strings (styled by TableStyle below).
    # Body rows get wrapped in Paragraphs so long text auto-wraps.
    if header:
        wrapped = [rows[0]] + [[_cell(c) for c in row] for row in rows[1:]]
    else:
        wrapped = [[_cell(c) for c in row] for row in rows]

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT) if header else ("BACKGROUND", (0, 0), (-1, 0), SOFT_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white if header else INK),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        # Body rows are Paragraphs now — they style their own font.
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(style)
    return t


def trigger_box():
    """Amber trust-and-escalation summary block."""
    rows = [
        ["Trigger code", "Rule", "Threshold"],
        ["low_confidence", "Any field confidence below threshold", "< 30 / 100"],
        ["severe_damage", "Damage classified as severe", "severity = severe"],
        ["poor_image_quality", "Image quality score below threshold", "< 50 / 100"],
        ["high_value", "Repair estimate high end above threshold", "> $9,000"],
    ]
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AMBER_BORDER),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (0, -1), "Courier"),
        ("FONTSIZE", (0, 1), (0, -1), 9),
        ("FONTNAME", (1, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (1, 1), (-1, -1), 9),
        ("BACKGROUND", (0, 1), (-1, -1), AMBER_BG),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, AMBER_BORDER),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, AMBER_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
    t = Table(rows, colWidths=[1.5 * inch, 3.2 * inch, 1.6 * inch], repeatRows=1)
    t.setStyle(style)
    return t


# ─── Document content ───────────────────────────────────────────────────
def build_story():
    story = []

    # ─── Title page
    story.append(Paragraph("Insurance Claims Analyzer", TITLE_STYLE))
    story.append(Paragraph("Architecture Overview", SUBTITLE_STYLE))
    story.append(Spacer(1, 12))
    story.append(Paragraph("AI-powered damage assessment prototype", BODY))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Date: 2026-04-28", META_STYLE))
    story.append(Paragraph("Stack: Next.js 16 · TypeScript · Tailwind 4 · Anthropic Claude Sonnet 4.6", META_STYLE))
    story.append(Spacer(1, 18))

    story.append(Paragraph(
        "This document describes the architecture of a single-image claims-assessment prototype. "
        "A single Anthropic Claude API call drives the entire AI pipeline — vision-based vehicle "
        "identification, damage classification with severity, and a confidence-bracketed repair-cost "
        "estimate — with structured outputs, adaptive thinking, and live streaming back to the user.",
        BODY,
    ))

    # ─── Section 1: Design Explanation (assignment deliverable)
    story.append(PageBreak())
    story.append(Paragraph("1. Design Explanation", H1))
    story.append(Paragraph(
        "Focused answer to the three required sub-bullets of the take-home brief: why these tools, "
        "how the AI logic works, and what would change with more time.",
        BODY,
    ))

    story.append(Paragraph("Why these tools", H2))
    story.append(Paragraph(
        "<b>Next.js (App Router) + TypeScript + Tailwind</b> in a single repo, because the spec demands "
        "a working full-stack demo in 3–4 hours. Next.js gives one codebase, one dev command, one test "
        "surface — no client/server split to maintain. Tailwind keeps styling decisions out of the "
        "critical path.",
        BODY,
    ))
    story.append(Paragraph(
        "<b>Anthropic Claude (Sonnet 4.6) as the only AI service</b>, because the entire pipeline — "
        "vehicle identification, damage classification, cost estimation — fits inside a single API call "
        "when you combine vision, structured outputs, and adaptive thinking. No model chaining, no glue "
        "code, one provider in the architecture diagram. This is the most impactful design decision in "
        "the prototype: every other choice flows from it.",
        BODY,
    ))
    story.append(Paragraph(
        "<b>Anthropic Files API</b> for image storage, to avoid introducing S3 / Vercel Blob and the "
        "associated CORS / presigned-URL plumbing for a 4-hour build. The file_id is a durable handle "
        "that sets up the multi-step workflows in Phase 2 (reanalysis, before/after comparison, fraud "
        "signals) without an architectural pivot. <b>sharp</b> handles image preprocessing — resize "
        "to ≤ 2576 px and EXIF strip — at the server edge before the image hits Anthropic's storage "
        "(real PII removal: GPS, timestamps, device info). <b>zod</b> validates Claude's structured "
        "output at runtime, so the frontend never has to defensively parse model responses.",
        BODY,
    ))

    story.append(Paragraph("How the AI logic works", H2))
    story.append(Paragraph(
        "A single client.beta.messages.stream() call drives everything. The image (referenced by file_id "
        "from the Files API upload) goes into a multimodal message alongside an instruction to analyze. "
        "The model is steered by a system prompt that frames Claude as an experienced auto damage adjuster "
        "with a five-step playbook (identify vehicle → describe damage → estimate cost → score image quality "
        "→ flag for review). The system prompt also inlines a typical-cost reference table by damage type "
        "and vehicle tier, so cost estimates are anchored in industry-typical ranges.",
        BODY,
    ))
    story.append(Paragraph(
        "output_config.format enforces a JSON schema on the response — the shape is guaranteed at the "
        "API level, no parsing flakiness possible. Adaptive thinking with effort: low lets Claude reason "
        "as deeply as it needs but stay tuned for fast first-pass assessment. The endpoint is a "
        "Server-Sent Events stream, so the user sees each phase appear live (preprocessing → upload → "
        "vehicle ID → output generation). Total wall-clock is ~5–10 seconds, but it feels instant.",
        BODY,
    ))
    story.append(Paragraph(
        "After Claude returns, the server validates the JSON with Zod, then runs four deterministic rules "
        "to compute typed Trigger objects (low confidence, severe damage, poor image quality, high-value "
        "claim). These are the human-review escalation signals — the AI's self-assessment is a fallback; "
        "the typed triggers are the source of truth. Each trigger carries a code for routing, the actual "
        "value, and the threshold that tripped — machine-readable and auditable.",
        BODY,
    ))

    story.append(Paragraph("Potential improvements", H2))
    story.append(Paragraph(
        "The full roadmap is in SOW.md as five phases. Highlights:",
        BODY,
    ))
    improvements = [
        ("Persistence + audit log (Phase 1)",
         "Postgres for claim records, S3 + KMS for images with 7-year retention, full read/write "
         "audit trail with the Claude model version captured for every analysis."),
        ("Production cost integration (Phase 1.5)",
         "Replace the in-prompt reference table with Mitchell / CCC ONE / Audatex APIs for parts-level "
         "pricing — the actual stack every major US carrier uses."),
        ("Multi-image and comparison flows (Phase 2)",
         "Multi-angle upload, side-by-side and AI-powered before/after comparison for repair verification. "
         "Introduces an interactive adjuster co-pilot built on Anthropic's Managed Agents API — persistent "
         "stateful sessions per claim where adjusters can reanalyze, generate PDF/DOCX claim documents, and "
         "iteratively refine the assessment."),
        ("Fraud signals (Phase 3)",
         "Image-hash deduplication, visual-similarity scoring against historical claims, AI pairwise "
         "comparison on top suspects."),
        ("PII redaction pipeline (Phase 1+)",
         "Automatic license-plate and face redaction before storage, configurable retention with archival, "
         "full SOC 2 / GDPR-equivalent audit logging."),
    ]
    improvements_rows = [["Phase / Theme", "Description"]] + [[t, d] for t, d in improvements]
    story.append(Spacer(1, 4))
    story.append(make_table(improvements_rows, [2.0 * inch, 4.6 * inch]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Smaller wins not in the prototype but easy adds: VIN sticker detection with NHTSA cross-reference "
        "(fraud signal), self-consistency sampling on low-confidence cases, cross-model verification on "
        ">$10k claims, and a real claims-system integration (Guidewire / Duck Creek webhook).",
        BODY,
    ))

    # ─── Section 2: System diagram
    story.append(PageBreak())
    story.append(Paragraph("2. System Diagram", H1))
    story.append(Paragraph(
        "Three layers — browser, server, external services — connected by a multipart upload "
        "(downward) and a Server-Sent Events stream (upward). The right-side panel shows a real "
        "sample of the SSE event stream the server emits to the browser as Claude works.",
        BODY,
    ))
    story.append(Spacer(1, 8))

    # Embed the Excalidraw-rendered architecture PNG (sized to fit page width).
    arch_png = OUT_PATH.parent / "architecture.png"
    if arch_png.exists():
        # Scale to fit available page width (page is 8.5", margins 0.6" each = 7.3" available)
        from reportlab.lib.utils import ImageReader as _IR
        ir = _IR(str(arch_png))
        iw, ih = ir.getSize()
        available_w = (letter[0] - 1.2 * inch)  # ≈ 525pt
        scale = available_w / iw
        story.append(Image(str(arch_png), width=iw * scale, height=ih * scale))
    else:
        # Fallback: keep the hand-coded reportlab diagram if PNG hasn't been generated.
        story.append(system_diagram())

    story.append(Paragraph(
        "Figure 1. Logical layout. The browser holds the SPA, the server runs the SSE "
        "endpoint, and Anthropic's Files API + Claude API are the only external dependencies. "
        "Source: architecture.excalidraw (editable at excalidraw.com).",
        CAPTION,
    ))

    # ─── Section 2: End-to-end data flow
    story.append(PageBreak())
    story.append(Paragraph("3. End-to-End Data Flow", H1))
    story.append(Paragraph(
        "Step-by-step trace of what happens when a user clicks Analyze. Total wall-clock "
        "time: approximately 5–10 seconds. Streaming makes the wait feel active rather than blocked.",
        BODY,
    ))

    flow_rows = [
        ["#", "Where", "What happens"],
        ["1", "Browser", "User selects file (or sample fetched as blob, wrapped as File)"],
        ["2", "Browser", "POSTs multipart/form-data to /api/analyze"],
        ["3", "Server", "Parses file from FormData"],
        ["4", "Server", "Image preprocess (sharp): rotate per EXIF → resize to ≤ 2576 px → JPEG re-encode → strip EXIF metadata (PII removal)"],
        ["5", "Server", "Opens SSE stream back to browser"],
        ["6", "Server", 'Sends status: "Preprocessing image"'],
        ["7", "Server", "Uploads to Anthropic Files API → receives file_id"],
        ["8", "Server", 'Sends status: "Uploading to Anthropic Files API"'],
        ["9", "Server", "Calls Claude Sonnet 4.6 (streaming): image by file_id, system prompt, JSON schema, adaptive thinking, effort: low"],
        ["10", "Server", 'Sends status: "Identifying vehicle and assessing damage"'],
        ["11", "Server", 'When Claude emits final text block: status "Generating structured output"'],
        ["12", "Server", "Validates JSON output with Zod"],
        ["13", "Server", "Computes typed Triggers (4 mechanical rules)"],
        ["14", "Server", 'Sends "complete" event with analysis + triggers + meta'],
        ["15", "Browser", "Renders three result cards + structured trigger banner if any"],
    ]
    story.append(Spacer(1, 6))
    story.append(make_table(flow_rows, [0.45 * inch, 0.8 * inch, 5.25 * inch]))

    # ─── Section 3: AI pipeline detail
    story.append(PageBreak())
    story.append(Paragraph("4. AI Pipeline (the single Claude call)", H1))
    story.append(Paragraph(
        "The entire AI logic is one client.beta.messages.stream() call. No model chaining, no "
        "multi-step orchestration. Vision, reasoning, and structured output happen in a single request.",
        BODY,
    ))

    pipeline_rows = [
        ["Field", "Value", "Purpose"],
        ["model", "claude-sonnet-4-6", "Vision-capable, balanced for speed/quality"],
        ["thinking", "{ type: 'adaptive' }", "Model decides reasoning depth dynamically"],
        ["output_config.format", "JSON Schema (ANALYSIS_JSON_SCHEMA)", "Enforces output shape — no JSON parsing flakiness"],
        ["output_config.effort", '"low"', "Speed-tuned reasoning for first-pass assessment"],
        ["system", "Adjuster persona + cost reference table", "Steers behavior, anchors cost estimates"],
        ["user content", "Image (by file_id) + analysis instruction", "Multimodal input"],
        ["betas", '["files-api-2025-04-14"]', "Required for file_id image references"],
    ]
    story.append(Spacer(1, 4))
    story.append(make_table(pipeline_rows, [1.6 * inch, 2.0 * inch, 3.0 * inch]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Output schema (every field guaranteed by the API)", H2))
    schema_rows = [
        ["Field path", "Description"],
        ["car.{make, model, color, year_estimate}", "Vehicle identification"],
        ["car.field_confidences.{make, model, color, year}", "0–100 per-field confidence"],
        ["car.confidence_reasoning", "Why the model is more or less confident"],
        ["damage.{summary, affected_areas[], severity}", "Damage description and classification"],
        ["damage.severity_confidence", "0–100 confidence in severity classification"],
        ["repair_estimate.{low_usd, high_usd, confidence, reasoning}", "Cost range with reasoning"],
        ["image_quality.{score, issues[]}", "0–100 image quality assessment"],
        ["requires_human_review, review_triggers[]", "Model self-assessment (overridden server-side)"],
        ["analysis_notes", "Free-form summary for adjuster context"],
    ]
    story.append(make_table(schema_rows, [3.6 * inch, 3.0 * inch]))

    # ─── Section 5: Image Processing Pipeline
    story.append(PageBreak())
    story.append(Paragraph("5. How Images Are Processed", H1))
    story.append(Paragraph(
        "The image traverses five stages from the user's hard drive to Claude's vision system. The "
        "middle stage (server-side preprocessing) is where the meaningful work happens — PII removal "
        "and dimension capping before any external service sees the bytes.",
        BODY,
    ))

    pipeline_steps = [
        ["Stage", "Where", "What happens"],
        ["1", "Browser", "User picks file via the file input or clicks a sample. Samples are fetched client-side and wrapped as a File object so they share the exact same upload path."],
        ["2", "Browser → Server", "FormData + native fetch sends the file as multipart/form-data — binary bytes over the wire, no base64 encoding."],
        ["3", "Server", "Request.formData() parses the multipart body, file.arrayBuffer() converts to a Node Buffer. Validation errors return as JSON 4xx, not in-stream errors."],
        ["4", "Server (sharp pipeline)", "rotate() — apply EXIF orientation. resize() — cap to ≤ 2576 px long-edge, preserve aspect, no upscaling. jpeg(quality:90, mozjpeg) — re-encode, dropping ALL EXIF metadata."],
        ["5", "Server → Anthropic", "Cleaned bytes uploaded once to Files API → file_id returned. Claude messages reference the image by file_id, not by re-sending bytes."],
    ]
    story.append(Spacer(1, 6))
    story.append(make_table(pipeline_steps, [0.6 * inch, 1.5 * inch, 4.4 * inch]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Order of operations matters", H2))
    story.append(Paragraph(
        "The sharp pipeline runs three transformations and the order is deliberate. .rotate() must "
        "come BEFORE the JPEG re-encode — otherwise the EXIF orientation tag is gone by the time "
        "we'd want to apply it, and Claude would see phone photos sideways. .resize() in the middle "
        "caps token cost (larger images cost more vision tokens). The .jpeg() re-encode is what "
        "actually strips EXIF — sharp's encoders don't carry metadata through.",
        BODY,
    ))

    story.append(Paragraph("Why EXIF stripping matters", H2))
    story.append(Paragraph(
        "EXIF metadata in phone photos can include GPS lat/long (where the photo was taken), "
        "timestamps (when), and device fingerprints (model and serial). For a claims pipeline, "
        "any of these can leak PII or contradict the claimed incident details. Stripping at the "
        "edge — before the cleaned bytes reach Anthropic's Files API — means Anthropic never "
        "stores the metadata in the first place. This is real compliance handling, not theatre.",
        BODY,
    ))

    bytes_table = [
        ["Stage", "Image state", "Size (typical)", "Stored where"],
        ["1. Browser pick", "Original phone JPEG with full EXIF", "4–8 MB", "Browser memory"],
        ["2. POST", "Original bytes over the wire", "4–8 MB transferred", "In flight"],
        ["3. Buffer", "Same bytes in Node", "4–8 MB", "Server memory"],
        ["4. After sharp", "Resized JPEG, no EXIF", "~400–800 KB", "Server memory"],
        ["5a. Files API", "Cleaned bytes uploaded", "~400–800 KB", "Anthropic Files storage"],
        ["5b. Claude call", "Reference by file_id only", "~30 bytes (just the ID)", "Request payload"],
    ]
    story.append(KeepTogether([
        Paragraph("What ends up where", H2),
        Spacer(1, 4),
        make_table(bytes_table, [1.0 * inch, 2.2 * inch, 1.4 * inch, 1.9 * inch]),
    ]))

    # ─── Section 6: Trust & escalation
    story.append(PageBreak())
    story.append(Paragraph("6. Trust &amp; Escalation Layer (server-side)", H1))
    story.append(Paragraph(
        "After Claude returns the analysis, the server runs deterministic rules and produces typed "
        "Trigger objects. Each trigger carries a code (for routing), the actual value, and the "
        "threshold that tripped the rule. Banners fire when triggers.length &gt; 0.",
        BODY,
    ))
    story.append(Spacer(1, 6))
    story.append(trigger_box())
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Why server-side instead of model-driven? Two reasons. First, deterministic enforcement — "
        "the four mechanical rules execute every time, regardless of how Claude phrases its self-assessment. "
        "Second, typed downstream consumption — fraud routing, queue assignment, audit logs, and "
        "analytics can act on the trigger code and value without parsing prose.",
        BODY,
    ))
    story.append(Paragraph(
        "Thresholds are exported constants in lib/schema.ts (REVIEW_THRESHOLDS). Different carriers "
        "calibrate differently — a conservative carrier might raise the confidence threshold to 70; "
        "an aggressive automation strategy might raise the high-value threshold to $20,000. This is "
        "the per-carrier tuning surface in production.",
        BODY,
    ))

    # ─── Section 5: Tech stack
    story.append(Paragraph("7. Tech Stack", H1))
    stack_rows = [
        ["Layer", "Choice"],
        ["Framework", "Next.js 16 (App Router) + TypeScript"],
        ["Styling", "Tailwind CSS 4"],
        ["AI", "@anthropic-ai/sdk + Claude Sonnet 4.6 (vision + structured outputs + adaptive thinking + streaming)"],
        ["Image storage", "Anthropic Files API (beta)"],
        ["Image processing", "sharp"],
        ["Schema validation", "zod (runtime) + hand-written JSON Schema (Claude contract)"],
        ["Streaming", "Server-Sent Events (native fetch + custom SSE parser)"],
        ["Hosting", "Local-only (npm run dev)"],
    ]
    story.append(make_table(stack_rows, [1.6 * inch, 5.0 * inch]))

    # ─── Section 6: Design decisions
    story.append(PageBreak())
    story.append(Paragraph("8. Key Design Decisions", H1))

    decisions = [
        ("One AI service, one API call",
         "Vision, reasoning, and structured output all happen in a single Claude request. No model "
         "chaining, no glue code, one provider to talk about with the customer."),
        ("Structured outputs over JSON parsing",
         "The contract is enforced by the API. The frontend never crashes on malformed model output; "
         "every field is guaranteed."),
        ("Server-side triggers, client-side rendering",
         "The four mechanical review rules execute deterministically server-side after Claude returns. "
         "Bulletproof, typed, auditable. The UI just renders them."),
        ("Streaming for UX, not throughput",
         "Wall-clock time is approximately 5–10 seconds either way. Streaming makes the wait feel "
         "instant by showing live phase progress (preprocessing → upload → vehicle ID → output)."),
        ("EXIF stripping before upload",
         "Real PII concern — GPS coordinates, timestamps, device info. Done at the edge with sharp "
         "before the image hits Anthropic storage."),
        ("Anthropic Files API for image storage",
         "Avoids introducing S3 / Vercel Blob and the associated CORS / presigned-URL plumbing for a "
         "4-hour build. The file_id becomes the durable handle to the image."),
        ("No persistence in v1",
         "The original spec does not require it. Adding a database costs hours and is invisible in the "
         "demo. Phase 1 in the SOW adds Postgres + audit log."),
    ]
    for i, (title, body) in enumerate(decisions, start=1):
        story.append(KeepTogether([
            Paragraph(f"{i}. {title}", H2),
            Paragraph(body, BODY),
        ]))

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "End of document. See README.md for setup instructions and SOW.md for the production roadmap.",
        CAPTION,
    ))

    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    page_num = canvas.getPageNumber()
    canvas.drawRightString(letter[0] - 0.5 * inch, 0.5 * inch, f"Page {page_num}")
    canvas.drawString(0.5 * inch, 0.5 * inch, "Insurance Claims Analyzer · Architecture Overview")
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.7 * inch,
        title="Insurance Claims Analyzer — Architecture Overview",
        author="Solutions Engineering",
    )
    doc.build(build_story(), onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
