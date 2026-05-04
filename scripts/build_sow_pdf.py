"""
Generate SOW.pdf — printable Statement of Work for the AI-powered Auto Claims
Assessment Platform. Mirrors the content of SOW.md with proper diagrams,
tables, and professional layout.

Run:
    .venv/bin/python scripts/build_sow_pdf.py
"""

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
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

# ─── Config ─────────────────────────────────────────────────────────────
OUT_PATH = Path(__file__).resolve().parent.parent / "SOW.pdf"

INK = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#475569")
ACCENT = colors.HexColor("#1D4ED8")
SOFT_BG = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")
AMBER_BG = colors.HexColor("#FEF3C7")
AMBER_BORDER = colors.HexColor("#F59E0B")
GREEN_BG = colors.HexColor("#DCFCE7")
GREEN_BORDER = colors.HexColor("#16A34A")
ROSE_BG = colors.HexColor("#FFE4E6")
ROSE_BORDER = colors.HexColor("#E11D48")
ROW_ALT = colors.HexColor("#F8FAFC")

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "TitleHero", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=26, leading=32, textColor=INK, alignment=TA_LEFT, spaceAfter=4,
)
SUBTITLE_STYLE = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontName="Helvetica",
    fontSize=14, leading=18, textColor=MUTED, spaceAfter=2,
)
META_STYLE = ParagraphStyle(
    "Meta", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10, leading=12, textColor=MUTED,
)
H1 = ParagraphStyle(
    "H1Section", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=15, leading=19, textColor=ACCENT, spaceBefore=12, spaceAfter=6,
)
H2 = ParagraphStyle(
    "H2Sub", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=11, leading=14, textColor=INK, spaceBefore=10, spaceAfter=4,
)
BODY = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica",
    fontSize=9.5, leading=13, textColor=INK, spaceAfter=4,
)
BULLET = ParagraphStyle(
    "Bullet", parent=BODY, leftIndent=14, bulletIndent=4, spaceAfter=2,
)
CAPTION = ParagraphStyle(
    "Caption", parent=styles["Normal"], fontName="Helvetica-Oblique",
    fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=10,
)
CELL_STYLE = ParagraphStyle(
    "Cell", parent=styles["Normal"], fontName="Helvetica",
    fontSize=8.5, leading=11.5, textColor=INK,
)


def _cell(value):
    if isinstance(value, str):
        safe = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return Paragraph(safe, CELL_STYLE)
    return value


def make_table(rows, col_widths, header=True):
    if header:
        wrapped = [rows[0]] + [[_cell(c) for c in row] for row in rows[1:]]
    else:
        wrapped = [[_cell(c) for c in row] for row in rows]

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT) if header else ("BACKGROUND", (0, 0), (-1, 0), SOFT_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white if header else INK),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, BORDER),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])
    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(style)
    return t


def bullet_list(items):
    """Render an indented bullet list."""
    flowables = []
    for item in items:
        safe = item.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        flowables.append(Paragraph(f"• {safe}", BULLET))
    return flowables


# ─── Diagram 1: Production architecture ─────────────────────────────────
def production_architecture_diagram() -> Drawing:
    W, H = 540, 380
    d = Drawing(W, H)

    def box(x, y, w, h, title, items=None, fill=SOFT_BG, border=BORDER, title_color=INK):
        d.add(Rect(x, y, w, h, strokeColor=border, strokeWidth=1, fillColor=fill, rx=4, ry=4))
        d.add(String(x + 8, y + h - 14, title, fontName="Helvetica-Bold", fontSize=9, fillColor=title_color))
        if items:
            for i, item in enumerate(items):
                d.add(String(x + 12, y + h - 28 - 11 * i, "• " + item,
                             fontName="Helvetica", fontSize=7.5, fillColor=INK))

    def arrow(x1, y1, x2, y2):
        d.add(Line(x1, y1, x2, y2, strokeColor=MUTED, strokeWidth=1.2))
        if y2 < y1:
            d.add(Polygon([x2 - 4, y2 + 6, x2 + 4, y2 + 6, x2, y2], strokeColor=MUTED, fillColor=MUTED))
        elif y2 > y1:
            d.add(Polygon([x2 - 4, y2 - 6, x2 + 4, y2 - 6, x2, y2], strokeColor=MUTED, fillColor=MUTED))
        elif x2 > x1:
            d.add(Polygon([x2 - 6, y2 - 4, x2 - 6, y2 + 4, x2, y2], strokeColor=MUTED, fillColor=MUTED))
        else:
            d.add(Polygon([x2 + 6, y2 - 4, x2 + 6, y2 + 4, x2, y2], strokeColor=MUTED, fillColor=MUTED))

    # Top: Carrier upload
    box(190, 330, 160, 40, "Carrier Upload (web/mobile)", fill=colors.white, border=BORDER)

    arrow(270, 330, 270, 295)

    # API gateway
    box(190, 250, 160, 40, "API Gateway", ["Auth (SSO), rate limit"], fill=SOFT_BG)

    arrow(270, 250, 270, 215)

    # PII redaction
    box(190, 170, 160, 40, "PII Redaction Service", ["License plate / face redact"], fill=GREEN_BG, border=GREEN_BORDER)

    arrow(270, 170, 270, 135)

    # Claims service (center)
    box(160, 90, 220, 40, "Claims Service", ["Orchestrates the analysis"], fill=SOFT_BG)

    # Branches from claims service
    arrow(160, 110, 100, 110)  # to Files API (left)
    arrow(380, 110, 440, 110)  # to AI orchestration (right)
    arrow(270, 90, 270, 55)    # down to result store

    # Files API (left of center)
    box(20, 90, 80, 40, "Anthropic Files API", fill=GREEN_BG, border=GREEN_BORDER)

    # AI orchestration (right of center)
    box(440, 35, 95, 150, "AI Orchestration", [
        "Claude (Sonnet 4.6 /",
        "  Opus 4.7 cross-val)",
        "Streaming Messages API",
        "  (real-time)",
        "Batches API",
        "  (bulk reprocess)",
        "Mitchell / CCC ONE",
        "  (parts pricing,",
        "   Phase 1.5)",
    ], fill=AMBER_BG, border=AMBER_BORDER)

    # Result store + audit log (bottom-center)
    box(160, 0, 220, 50, "Result Store + Audit Log", [
        "Postgres (claims, analyses)",
        "S3 + KMS (images, 7yr retention)",
    ], fill=SOFT_BG)

    # Carrier integration (bottom-right cap)
    arrow(380, 25, 440, 25)
    box(440, 5, 95, 25, "Carrier Integration", fill=colors.white, border=BORDER)

    return d


# ─── Diagram 2: Phase timeline ──────────────────────────────────────────
def timeline_diagram() -> Drawing:
    W, H = 540, 200
    d = Drawing(W, H)

    # Phase 0 is rendered as a fixed-width "delivered" pill (it has no
    # week-duration to proportion against). Phases 1–4 share the rest
    # of the bar proportionally to their weeks.
    phase0 = ("Phase 0", "Prototype", GREEN_BG, GREEN_BORDER, "delivered")

    phases = [
        ("Phase 1", "Pilot launch", 8.0, ACCENT, ACCENT, "8 weeks"),
        ("Phase 1.5", "Cost integration\n+ batch reprocess", 4.0, AMBER_BORDER, AMBER_BORDER, "4 weeks"),
        ("Phase 2", "Multi-image\n+ co-pilot", 6.0, colors.HexColor("#7C3AED"), colors.HexColor("#7C3AED"), "6 weeks"),
        ("Phase 3", "Fraud signals", 8.0, ROSE_BORDER, ROSE_BORDER, "8 weeks"),
        ("Phase 4", "National rollout", 4.0, MUTED, MUTED, "ongoing"),
    ]

    dark_fills = (ACCENT, MUTED, ROSE_BORDER, colors.HexColor("#7C3AED"), AMBER_BORDER)
    total_weeks = sum(p[2] for p in phases)
    margin_x = 30
    bar_y = 90
    bar_h = 36

    p0_w = 58
    p0_gap = 6
    p0_name, p0_label, p0_fill, p0_border, p0_dur = phase0
    d.add(Rect(margin_x, bar_y, p0_w, bar_h, strokeColor=p0_border, strokeWidth=1, fillColor=p0_fill, rx=3, ry=3))
    d.add(String(margin_x + 6, bar_y + bar_h - 12, p0_name,
                 fontName="Helvetica-Bold", fontSize=8, fillColor=INK))
    d.add(String(margin_x + 6, bar_y + 6, p0_dur,
                 fontName="Helvetica", fontSize=7, fillColor=INK))
    d.add(String(margin_x + 6, bar_y - 12, p0_label,
                 fontName="Helvetica", fontSize=7.5, fillColor=INK))

    bar_x_start = margin_x + p0_w + p0_gap
    avail_w = W - margin_x - bar_x_start

    x = bar_x_start
    for name, label, weeks, fill, border, duration in phases:
        w = (weeks / total_weeks) * avail_w
        d.add(Rect(x, bar_y, w, bar_h, strokeColor=border, strokeWidth=1, fillColor=fill, rx=3, ry=3))
        text_color = colors.white if fill in dark_fills else INK
        d.add(String(x + 6, bar_y + bar_h - 12, name,
                     fontName="Helvetica-Bold", fontSize=8, fillColor=text_color))
        d.add(String(x + 6, bar_y + 6, duration,
                     fontName="Helvetica", fontSize=7, fillColor=text_color))
        for li, line in enumerate(label.split("\n")):
            d.add(String(x + 6, bar_y - 12 - li * 10, line,
                         fontName="Helvetica", fontSize=7.5, fillColor=INK))
        x += w

    # Header
    d.add(String(margin_x, bar_y + bar_h + 24, "Engagement Timeline (Phase 0 → 4)",
                 fontName="Helvetica-Bold", fontSize=11, fillColor=INK))

    # Tick marks at the start of each Phase 1+ block (w1, w9, w13, w19, w27).
    cumulative = 0
    for _, _, weeks, _, _, _ in phases:
        tx = bar_x_start + (cumulative / total_weeks) * avail_w
        d.add(Line(tx, bar_y - 30, tx, bar_y - 26, strokeColor=BORDER, strokeWidth=0.5))
        d.add(String(tx, bar_y - 38, f"w{int(cumulative) + 1}",
                     fontName="Helvetica", fontSize=6.5, fillColor=MUTED, textAnchor="middle"))
        cumulative += weeks

    return d


# ─── Document content ───────────────────────────────────────────────────
def build_story():
    story = []

    # ── Title page
    story.append(Paragraph("Statement of Work", TITLE_STYLE))
    story.append(Paragraph("AI-Powered Auto Claims Assessment Platform", SUBTITLE_STYLE))
    story.append(Spacer(1, 14))
    story.append(Paragraph("Version: 1.0 — Prototype + Production Roadmap", META_STYLE))
    story.append(Paragraph("Date: 2026-04-28", META_STYLE))
    story.append(Spacer(1, 10))

    # ── Section 1: Project Scope
    story.append(Paragraph("1. Project Scope", H1))

    story.append(Paragraph("Vision", H2))
    story.append(Paragraph(
        "Reduce time-to-estimate, improve consistency, and lower handling cost on auto-physical-damage "
        "claims by automating the first-pass damage assessment with a vision-grounded AI pipeline. "
        "Replace the manual desk-review step on simple claims with an AI assessment that adjusters "
        "trust, and tier higher-stakes claims into human review automatically.",
        BODY,
    ))

    story.append(Paragraph("In scope (Phase 1 — Production v1)", H2))
    for item in [
        "Image-based damage assessment. Web and mobile-web upload of a single damaged-vehicle photo (or image URL); AI returns vehicle metadata (make, model, color, year), damage description with severity classification, and a repair-cost range with cited sources.",
        "Confidence-driven routing. Per-field numerical confidence indicators; automatic flagging of low-confidence and high-severity claims for human adjuster review.",
        "Auditability. Every analysis is persisted with the input image, output JSON, model version, and external sources cited. Reanalysis on demand.",
        "PII handling. Server-side EXIF stripping and image normalization before upload to AI provider; license-plate and face redaction pipeline.",
        "Carrier integration. REST/webhook integration with the carrier's claims management system (Guidewire ClaimCenter, Duck Creek Claims, or equivalent).",
    ]:
        story.append(Paragraph(f"• {item}", BULLET))

    story.append(Paragraph("Out of scope (Phase 1)", H2))
    for item in [
        "Multi-angle / multi-image fusion (Phase 2)",
        "Pre-repair vs post-repair comparison flows (Phase 2)",
        "Fraud-signal pipeline (Phase 3)",
        "Native mobile apps (web-first; PWA-capable)",
        "Total-loss decisioning (advisory only — final call stays with adjuster)",
        "Subrogation, salvage value, or actual cash value calculations (out-of-band integrations)",
    ]:
        story.append(Paragraph(f"• {item}", BULLET))

    story.append(Paragraph("Boundaries and assumptions", H2))
    for item in [
        "Advisory, not authoritative. AI output is a recommendation. A licensed adjuster owns every claim decision, especially payouts and denials.",
        "Pilot cohort. Phase 1 deploys to a defined cohort (e.g., one product line, one geography). National rollout is a separate engagement.",
        "Carrier provides: branded UI assets, sandbox claims system access, sample claim photos and ground-truth assessments for evaluation, and an SME contact for adjuster workflow questions.",
    ]:
        story.append(Paragraph(f"• {item}", BULLET))

    # ── Section 2: Technical Approach
    story.append(PageBreak())
    story.append(Paragraph("2. Technical Approach", H1))

    story.append(Paragraph("Core architecture", H2))
    story.append(Paragraph(
        "A single, vision-capable LLM (Anthropic Claude Sonnet 4.6, with Opus 4.7 cross-validation on "
        "high-stakes claims) drives the AI pipeline. The prototype demonstrates that one model API call "
        "can produce all three required outputs — vehicle metadata, damage assessment, and repair cost — "
        "with structured-output guarantees. Production extends this with persistence, PII redaction, "
        "carrier integration, and a separate batch workload for non-latency-sensitive operations.",
        BODY,
    ))

    story.append(Spacer(1, 6))
    story.append(production_architecture_diagram())
    story.append(Paragraph(
        "Figure 1. Production architecture. The streaming Messages API handles real-time per-claim analysis; "
        "the Batches API (Phase 1.5+) handles bulk reprocessing at 50% of synchronous-API cost.",
        CAPTION,
    ))

    story.append(Paragraph("AI / ML model and integration choices", H2))
    arch_rows = [
        ["Component", "Choice", "Justification"],
        ["Primary vision-LLM", "Claude Sonnet 4.6", "Vision + structured outputs + adaptive thinking + streaming. Single-vendor reduces operational complexity."],
        ["Cost grounding (Phase 1)", "In-prompt reference table", "Industry-typical ranges by damage type × vehicle tier. No external dependency."],
        ["Cost grounding (Phase 1.5)", "Mitchell / CCC ONE / Audatex API", "Industry-standard parts-level pricing used by every major US carrier."],
        ["Structured outputs", "output_config.format JSON Schema", "Server-enforced contract; downstream services consume typed JSON without parsing risk."],
        ["Image preprocessing", "sharp (Node)", "Resize, JPEG normalize, EXIF strip. Runs at the edge before image hits AI provider storage."],
        ["Confidence routing", "Per-field 0–100 + typed Trigger objects (server-side)", "Calibrated to adjuster workflow; thresholds tuned per carrier policy."],
        ["PII redaction", "CV detection (license plate / face) + sharp blur", "Required for compliance (state DMV regulations, GDPR-equivalent for international)."],
        ["Cross-validation (>$10k)", "Run on Sonnet 4.6 + Opus 4.7; flag disagreement", "Cheap insurance against single-model errors on high-stakes claims."],
        ["Self-consistency sampling", "Re-run Sonnet 4.6 on the same image; flag variance", "Triggered on low-confidence cases. Cheap variance signal that surfaces uncertain assessments adjusters should double-check."],
        ["VIN cross-reference (Phase 2)", "NHTSA vPIC decode of dashboard VIN sticker", "Catches AI make/model misidentification; fraud signal when claimed make/model ≠ VIN-decoded."],
        ["Bulk reprocessing (Phase 1.5+)", "Anthropic Messages Batches API", "Async batch endpoint for non-latency-sensitive workloads (model-upgrade reanalysis, fraud backfill, compliance audits, acquired-book reprocessing). Up to 100K requests / 24h at 50% of synchronous-API cost."],
        ["Interactive workflows (Phase 2+)", "Anthropic Managed Agents API", "Persistent stateful sessions for adjuster co-pilot and long-running fraud investigations. Anthropic runs agent loop and hosts per-session sandbox."],
        ["Persistence", "Postgres + S3 (KMS-encrypted)", "Standard. 7-year retention with Glacier archival per insurance regulation."],
    ]
    story.append(make_table(arch_rows, [1.4 * inch, 1.8 * inch, 3.4 * inch]))

    story.append(Paragraph("Integration points", H2))
    for item in [
        "Carrier claims system: bidirectional. Outbound: AI assessment posted as claim attachment + structured fields. Inbound: claim status updates trigger reanalysis or archival.",
        "Carrier identity provider (SAML / OIDC): SSO for adjuster access to the review console.",
        "Carrier audit / SIEM: stream every read/write of claim data with actor, timestamp, purpose.",
        "Anthropic Claude API: Messages API (streaming) for real-time + Batches API for bulk + Files API for image storage.",
        "Mitchell / CCC ONE / Audatex (Phase 1.5): replace in-prompt reference table for parts-level pricing once carrier procures access.",
    ]:
        story.append(Paragraph(f"• {item}", BULLET))

    story.append(Paragraph("Orchestration strategy: single-call spine + gated chaining", H2))
    story.append(Paragraph(
        "The Phase 0 prototype is a single messages.create() call. Production keeps the single-call architecture as the "
        "<b>default spine</b> for first-pass assessment — it handles the majority of claims correctly with one round-trip, "
        "one schema, and one transaction boundary. Chained model orchestration is layered on top <b>only as gated "
        "specializations</b> where a specific failure mode or cost dynamic justifies the extra inference. Six chained "
        "patterns ship across Phases 1–3:",
        BODY,
    ))

    chain_rows = [
        ["Phase", "Chain pattern", "Trigger", "What chains / Why"],
        ["1", "Cross-validation", "high_usd > $10k",
         "Sonnet 4.6 + Opus 4.7 in parallel → deterministic comparison. Independent second opinion on high-stakes claims; flag disagreement for adjuster."],
        ["1", "Self-consistency sampling", "Any field confidence < threshold",
         "Re-run Sonnet 4.6 on same image → variance comparison on cost / severity / make-model. Variance signal that surfaces uncertain assessments adjusters should double-check."],
        ["1.5", "Haiku triage tier", "All claims (only ungated chain)",
         "Haiku 4.5 image-quality + tier triage → escalate to Sonnet on pass, short-circuit on bad input. Cuts blended inference cost ~30% at scale; the only chain that reduces spend."],
        ["1.5", "Parts-pricing fusion", "Damage assessment complete",
         "Sonnet damage description → Mitchell / CCC ONE / Audatex parts API → Sonnet cost grounding. Replaces in-prompt reference table with deterministic parts pricing."],
        ["2", "Adjuster co-pilot", "Adjuster opens claim console",
         "Anthropic Managed Agents API — chained tool/model loop in a persistent session. Stateful multi-turn workflows: reanalyze, PDF/DOCX generation, iterative refinement."],
        ["3", "Fraud pipeline", "Similarity above threshold",
         "Image-hash dedup → vector similarity → AI pairwise on top-K → structured fraud report. Multi-stage candidate narrowing makes the AI-pairwise step affordable."],
    ]
    story.append(make_table(chain_rows, [0.4 * inch, 1.3 * inch, 1.5 * inch, 3.4 * inch]))

    story.append(Paragraph(
        "<b>Design rule.</b> Every chain ships with: (a) a named failure mode it addresses, (b) a measured baseline error "
        "rate on that failure mode, (c) a trigger condition gating the chain to a subset of traffic, and (d) an A/B-"
        "validated metric move versus the single-call baseline. Chains that fail to earn their keep are removed in quarterly review.",
        BODY,
    ))
    story.append(Paragraph(
        "<b>Anti-patterns explicitly out of scope.</b> The single-call assessment is <i>not</i> split into vehicle-ID → "
        "damage → cost stages — adaptive thinking already runs that reasoning internally inside one call, and splitting "
        "it adds latency, breaks cross-stage information flow, and creates coherence risk. Generic verifier stages "
        "without a named failure mode are also out of scope: two calls of the same model on the same input mostly agree "
        "with themselves, producing 2× cost for no real signal.",
        BODY,
    ))

    story.append(Paragraph("Deployment model", H2))
    for item in [
        "Multi-tenant SaaS, with per-carrier data isolation at the database row level (PostgreSQL RLS) or schema level.",
        "Deployed in AWS us-east-1 with PrivateLink option for carriers requiring private connectivity.",
        "SOC 2 Type II in progress; HIPAA-equivalent controls for PII handling.",
    ]:
        story.append(Paragraph(f"• {item}", BULLET))

    # ── Section 3: Milestones and Timeline
    story.append(PageBreak())
    story.append(Paragraph("3. Milestones and Timeline", H1))

    story.append(timeline_diagram())
    story.append(Paragraph(
        "Figure 2. Phase timeline. Bar widths are proportional to phase duration. Phase 4 is ongoing.",
        CAPTION,
    ))

    milestone_rows = [
        ["Phase", "Milestone", "Deliverables", "Duration"],
        ["0", "Prototype (delivered)", "Single-image upload + AI assessment. Local-run Next.js app + this SOW.", "Complete"],
        ["1", "Pilot launch (production v1)", "Hosted multi-tenant app, carrier SSO, persistence, audit log, PII redaction, claims-system integration (1 carrier).", "8 weeks"],
        ["1.5", "Production cost integration + bulk reprocessing", "Mitchell or CCC ONE replaces in-prompt reference for cost data. Operationalizes Anthropic Messages Batches API for non-latency-sensitive workloads (model-upgrade reanalysis, fraud backfill, compliance audits) at 50% of synchronous-API cost. Calibration data collection begins.", "4 weeks"],
        ["2", "Multi-image flows + adjuster co-pilot", "Multi-angle upload, side-by-side and AI-powered before/after comparison. Interactive adjuster co-pilot built on Anthropic's Managed Agents API — persistent stateful session per claim with PDF/DOCX generation.", "6 weeks"],
        ["3", "Fraud-signal pipeline", "Image-hash dedup, visual-similarity scoring against historical claims, AI pairwise comparison on top suspects. Long-running fraud investigations run as Managed Agents sessions.", "8 weeks"],
        ["4", "National rollout + multi-carrier", "Hardening, SLA tuning, observability, additional carrier onboarding, mobile-first UX refinements.", "Ongoing"],
    ]
    story.append(make_table(milestone_rows, [0.4 * inch, 1.4 * inch, 4.0 * inch, 0.7 * inch]))

    week_rows = [
        ["Week", "Focus"],
        ["1", "Discovery: adjuster workflow shadowing, claim-volume profiling, ground-truth dataset assembly"],
        ["2", "Auth (SSO), persistence layer, deployment infrastructure"],
        ["3", "PII redaction service, audit log"],
        ["4", "Claims-system integration (carrier sandbox)"],
        ["5", "Adjuster review console (web UI), reanalysis flow"],
        ["6", "Calibration: tune confidence thresholds against ground-truth dataset"],
        ["7", "UAT with pilot adjuster cohort, bug fixes"],
        ["8", "Production cutover (limited cohort), runbook handoff to carrier IT"],
    ]
    story.append(KeepTogether([
        Paragraph("Phase 1 weekly breakdown", H2),
        make_table(week_rows, [0.5 * inch, 6.0 * inch]),
    ]))

    # ── Section 4: Risk Assessment
    story.append(PageBreak())
    story.append(Paragraph("4. Risk Assessment", H1))

    risk_rows = [
        ["Risk", "Likelihood", "Impact", "Mitigation"],
        ["Cost estimate accuracy below adjuster expectations", "Med", "High",
         "Phase 1.5 replaces reference table with Mitchell/CCC parts-level pricing. In Phase 1, cost is presented as a range with confidence; AI estimate framed as advisory. Confidence-routed escalation to human for low confidence."],
        ["AI misidentifies vehicle make/model on uncommon cars", "Med", "Med",
         "Per-field confidence surfaced to adjuster. Adjuster can override. Calibration data from overrides feeds prompt tuning. VIN cross-reference via NHTSA vPIC (Phase 2) catches mismatches."],
        ["PII leakage (license plate, GPS in EXIF, face)", "Low", "High",
         "Server-side EXIF stripping before any AI provider sees the image. Phase 1 adds CV-based plate/face redaction. SOC 2 controls and per-carrier data isolation."],
        ["Low-quality input photos (blur, dark, partial view)", "High", "Med",
         "Image-quality scoring built into the AI pipeline; low quality caps confidence and triggers human review. UI surfaces specific quality issues so user can retake."],
        ["Adjuster distrust of AI / change-management resistance", "High", "High",
         "Pilot launches as advisory tool only — no auto-decisions. Confidence indicators and source citations make every output auditable. Adjuster shadowing (Week 1) builds workflow alignment."],
        ["Anthropic API outage or rate-limit pressure during peak claim volume", "Low", "High",
         "Multi-region failover, request queuing with SLA-bounded backoff, fallback to traditional desk-review queue. Business continuity runbook in place."],
        ["Cost overrun on AI inference at scale", "Med", "Med",
         "Token-budget monitoring per claim. Image preprocessing caps input cost. Haiku 4.5 fallback for low-stakes claims (<$2k) reduces per-claim cost ~5×. Caching + Batches API (50% off) for non-latency-sensitive workloads."],
        ["Regulatory: state-level disclosure requirements for AI in insurance decisions", "Med", "High",
         "All Phase 1 outputs are advisory only — final decisions stay with licensed adjuster. UI clearly labels AI-generated content. Compliance review per state of operation."],
        ["Fraud actors exploit AI auto-handling on simple claims", "Med", "High",
         "Phase 3 fraud-signal pipeline. Phase 1 mitigations: image-hash deduplication, sliding confidence thresholds for repeat claimants, sampling rate of human review on auto-handled claims."],
        ["Vendor lock-in (single-LLM dependency)", "Low", "Med",
         "API contract for AI service is encapsulated in a single orchestration module. Phase 4 adds cross-vendor abstraction if needed. Open-source vision models evaluated as fallback for non-critical paths."],
    ]
    story.append(make_table(risk_rows, [2.0 * inch, 0.5 * inch, 0.5 * inch, 3.5 * inch]))

    # ── Section 5: Success Metrics
    story.append(PageBreak())
    story.append(Paragraph("5. Success Metrics", H1))
    story.append(Paragraph(
        "KPIs are tracked from Day 1 of pilot. Targets are for the end of Phase 1 (8 weeks post-launch on the pilot cohort).",
        BODY,
    ))

    story.append(Paragraph("Primary KPIs", H2))
    primary_rows = [
        ["KPI", "Baseline", "Target", "Why it matters"],
        ["Time to first damage assessment", "4–24h (adjuster desk)", "< 5 min (AI-first pass)",
         "Customer satisfaction; cycle-time reduction maps to NPS uplift"],
        ["Adjuster touch-time per claim (simple claims)", "~15 min", "< 5 min",
         "Adjuster capacity unlocked for complex claims"],
        ["Cost-estimate accuracy (within ±15% of final)", "N/A", "≥ 75% on pilot cohort",
         "Trust signal; unreliable estimates → adjusters won't lean on them"],
        ["Auto-handle rate (simple claims, no escalation)", "0%", "30% of qualifying claims",
         "Volume unlocked; revenue model justification"],
        ["Adjuster override rate", "N/A", "< 25% of AI assessments",
         "Calibration health; high override rate → retune prompt or thresholds"],
    ]
    story.append(make_table(primary_rows, [1.7 * inch, 1.1 * inch, 1.3 * inch, 2.4 * inch]))

    story.append(Paragraph("Quality and trust KPIs", H2))
    quality_rows = [
        ["KPI", "Target"],
        ["Confidence calibration (claimed vs. measured accuracy)", "Within 10 percentage points"],
        ["Severity-classification accuracy", "≥ 85% agreement with adjuster"],
        ["PII-redaction false-negative rate", "< 0.1% (1 in 1000 images)"],
        ["requires_human_review precision (when flagged, review warranted)", "≥ 80%"],
        ["requires_human_review recall (claims that needed review were flagged)", "≥ 95%"],
    ]
    story.append(make_table(quality_rows, [4.0 * inch, 2.5 * inch]))

    story.append(Paragraph("Operational KPIs", H2))
    op_rows = [
        ["KPI", "Target"],
        ["API availability (rolling 30 days)", "≥ 99.9%"],
        ["p95 end-to-end analysis latency", "< 60s"],
        ["p99 end-to-end analysis latency", "< 90s"],
        ["Cost per analyzed claim (compute + AI)", "< $0.50"],
        ["Audit-log completeness", "100% (compliance)"],
        ["Bulk reprocessing SLA (Batches API runs, Phase 1.5+)", "≥ 95% within 24h"],
        ["Bulk-vs-realtime cost delta (validation of 50% savings)", "≥ 45% measured savings on Batches workloads"],
    ]
    story.append(make_table(op_rows, [4.0 * inch, 2.5 * inch]))

    story.append(Paragraph("Business KPIs (Phase 1.5+ as data accumulates)", H2))
    for item in [
        "Loss-cost reduction on pilot cohort vs. control cohort: target 3–5% via faster cycle-time and more consistent estimates.",
        "Customer NPS on claim handling: target +10 points on pilot vs. baseline.",
        "Adjuster satisfaction with the AI-assist workflow: target 4.0+ on a 5-point scale by end of Phase 1.",
    ]:
        story.append(Paragraph(f"• {item}", BULLET))

    story.append(Paragraph("Reporting cadence", H2))
    cadence_rows = [
        ["Cadence", "Reports"],
        ["Weekly", "Operational KPIs + adjuster override rate (during Phase 1)"],
        ["Bi-weekly", "Quality KPIs (confidence calibration, severity accuracy)"],
        ["Monthly", "Business KPIs + pilot vs. control comparison"],
        ["Quarterly", "Executive review with carrier leadership"],
    ]
    story.append(make_table(cadence_rows, [1.2 * inch, 5.3 * inch]))

    # ── Appendix: Sign-off
    story.append(Spacer(1, 16))
    story.append(Paragraph("Appendix A — Sign-off", H1))
    signoff_rows = [
        ["Role", "Name", "Date"],
        ["Carrier Project Sponsor", "", ""],
        ["Carrier Claims Operations Lead", "", ""],
        ["Solutions Engineering Lead", "", ""],
        ["Implementation Manager", "", ""],
    ]
    story.append(make_table(signoff_rows, [3.0 * inch, 2.5 * inch, 1.0 * inch]))

    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    page_num = canvas.getPageNumber()
    canvas.drawRightString(letter[0] - 0.5 * inch, 0.5 * inch, f"Page {page_num}")
    canvas.drawString(0.5 * inch, 0.5 * inch, "SOW · AI-Powered Auto Claims Assessment Platform")
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.7 * inch,
        title="SOW — AI-Powered Auto Claims Assessment Platform",
        author="Solutions Engineering",
    )
    doc.build(build_story(), onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
