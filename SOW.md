# Statement of Work
## AI-Powered Auto Claims Assessment Platform

**Prepared for:** [Insurance Carrier]
**Prepared by:** Solutions Engineering
**Version:** 1.0 — Prototype + Production Roadmap

---

## 1. Project Scope

### Vision

Reduce time-to-estimate, improve consistency, and lower handling cost on auto-physical-damage claims by automating the first-pass damage assessment with a vision-grounded AI pipeline. Replace the manual desk-review step on simple claims with an AI assessment that adjusters trust, and tier higher-stakes claims into human review automatically.

### In scope (Phase 1 — Production v1)

- **Image-based damage assessment.** Web and mobile-web upload of a single damaged-vehicle photo (or image URL); AI returns vehicle metadata (make, model, color, year), damage description with severity classification, and a repair-cost range with cited sources.
- **Confidence-driven routing.** Per-field numerical confidence indicators; automatic flagging of low-confidence and high-severity claims for human adjuster review.
- **Auditability.** Every analysis is persisted with the input image, output JSON, model version, and external sources cited. Reanalysis on demand.
- **PII handling.** Server-side EXIF stripping and image normalization before upload to AI provider; license-plate and face redaction pipeline.
- **Carrier integration.** REST/webhook integration with the carrier's claims management system (Guidewire ClaimCenter, Duck Creek Claims, or equivalent) to push assessments and pull claim status.

### Out of scope (Phase 1)

- Multi-angle / multi-image fusion (Phase 2)
- Pre-repair vs post-repair comparison flows (Phase 2)
- Fraud-signal pipeline (Phase 3)
- Native mobile apps (web-first; PWA-capable)
- Total-loss decisioning (advisory only — final call stays with adjuster)
- Subrogation, salvage value, or actual cash value calculations (out-of-band integrations)

### Boundaries and assumptions

- **Advisory, not authoritative.** AI output is a recommendation. A licensed adjuster owns every claim decision, especially payouts and denials.
- **Pilot cohort.** Phase 1 deploys to a defined cohort (e.g., one product line, one geography). National rollout is a separate engagement.
- **Carrier provides:** branded UI assets, sandbox claims system access, sample claim photos and ground-truth assessments for evaluation, and an SME contact for adjuster workflow questions.

---

## 2. Technical Approach

### Core architecture

A single, vision-capable LLM (Anthropic Claude Sonnet 4.6, with Opus 4.7 cross-validation on high-stakes claims) drives the AI pipeline. The prototype demonstrates that **one model API call** can produce all three required outputs — vehicle metadata, damage assessment, and repair cost — with structured-output guarantees. Production extends this with persistence, PII redaction, carrier integration, and a separate batch workload for non-latency-sensitive operations.

**Production architecture:**

```
Carrier upload (web/mobile)
        │
        ▼
API gateway ──► PII redaction service (license plates, faces)
        │
        ▼
Claims service ──► Anthropic Files API (image storage by file_id)
        │
        ▼
AI orchestration layer
   ├─ Claude Sonnet 4.6 vision (primary assessment)
   ├─ Opus 4.7 cross-validation on >$10k claims
   ├─ In-prompt reference cost table (Phase 1)
   ├─ Streaming Messages API (real-time per-claim)
   ├─ Batches API (Phase 1.5+, bulk reprocessing at 50% cost)
   └─ Mitchell / CCC ONE / Audatex parts pricing (Phase 1.5)
        │
        ▼
Result store (Postgres) + audit log
        │
        ▼
Carrier integration: Guidewire / Duck Creek webhook
```

### AI / ML model and integration choices

| Component                  | Choice                                                                  | Justification                                                                                                          |
| -------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Primary vision-LLM         | Claude Sonnet 4.6                                                       | Vision (2576px high-res) + structured outputs + adaptive thinking + streaming. Single-vendor reduces operational complexity. |
| Cost grounding (Phase 1)   | In-prompt reference table                                               | Industry-typical USD ranges by damage type × vehicle tier, inlined into the system prompt. No external dependency; no vendor agreement required. Limitation: not parts-level pricing. |
| Cost grounding (Phase 1.5) | Mitchell / CCC ONE / Audatex API integration                            | Industry-standard parts-level pricing used by every major US carrier. Replaces the in-prompt reference table with deterministic data. |
| Structured outputs         | `output_config.format` JSON Schema                                       | Server-enforced contract; downstream services consume typed JSON without parsing risk.                                |
| Image preprocessing        | `sharp` (Node)                                                          | Resize, JPEG normalize, EXIF strip. Runs at the edge before the image hits AI provider storage.                       |
| Confidence routing         | Per-field 0–100 + model-emitted `requires_human_review` flag             | Calibrated to adjuster workflow; thresholds tuned per carrier policy.                                                 |
| PII redaction              | Computer-vision detection (license plate / face) + `sharp` blur          | Required for compliance (state DMV regulations, GDPR-equivalent for international carriers).                          |
| Cross-validation (>$10k)   | Run on both Sonnet 4.6 and Opus 4.7; flag disagreement on severity/cost | Cheap insurance against single-model errors on high-stakes claims.                                                    |
| Self-consistency sampling  | Re-run Sonnet 4.6 on the same image when initial confidence is low; flag estimate variance | Cheap variance signal that surfaces uncertain assessments adjusters should double-check. Triggered only on low-confidence cases to bound cost. |
| VIN cross-reference        | NHTSA vPIC API decode of VIN sticker captured in dashboard photos (Phase 2) | Catches AI make/model misidentification on uncommon vehicles; fraud signal when claimed make/model ≠ VIN-decoded. |
| Bulk reprocessing (Phase 1.5+) | Anthropic Messages Batches API                                     | Asynchronous batch endpoint (`POST /v1/messages/batches`) for non-latency-sensitive workloads — model-upgrade reanalysis, historical fraud-detection backfill, end-of-day compliance audits, and acquired-book reprocessing. Up to 100,000 requests per batch with results within 24 hours, at 50% of synchronous-API cost. Distinct from real-time per-claim analysis, which continues to use the streaming Messages API. |
| Interactive workflows (Phase 2+) | Anthropic Managed Agents API                                       | Persistent stateful sessions for the adjuster co-pilot and long-running fraud investigations. Anthropic runs the agent loop and hosts a per-session sandbox where the agent can execute bash, file ops, and code (e.g., generating PDF claim reports). The Phase 1 single-call architecture handles stateless real-time assessment; Managed Agents handles stateful interactive workflows. |
| Persistence                | Postgres (claims, analyses, audit log) + S3 (images, with KMS at rest)   | Standard. 7-year retention with Glacier archival per insurance regulation.                                            |

### Integration points

- **Carrier claims system:** Bidirectional. Outbound: AI assessment posted as a claim attachment + structured fields. Inbound: claim status updates trigger reanalysis or archival.
- **Carrier identity provider (SAML / OIDC):** SSO for adjuster access to the review console.
- **Carrier audit/SIEM:** Stream every read/write of claim data with actor, timestamp, and purpose.
- **Anthropic Claude API:** Single outbound dependency for AI inference. Files API for image storage.
- **Mitchell / CCC ONE / Audatex (Phase 1.5):** Replace the in-prompt reference table for cost data once carrier procures access.

### Orchestration strategy: single-call spine + gated chaining

The Phase 0 prototype is a single `messages.create()` call. Production keeps the single-call architecture as the **default spine** for first-pass assessment — it handles the majority of claims correctly with one round-trip, one schema, one validation surface, and one transaction boundary. Chained model orchestration is layered on top **only as gated specializations** where a specific failure mode or cost dynamic justifies the extra inference. Six chained patterns ship across Phases 1–3:

| Phase | Chain pattern              | Trigger condition                       | What chains                                                                              | Why                                                                                |
| ----- | -------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1     | Cross-validation           | `repair_estimate.high_usd > $10k`       | Sonnet 4.6 + Opus 4.7 in parallel → deterministic comparison                             | Independent second opinion on high-stakes claims; flag disagreement for adjuster.  |
| 1     | Self-consistency sampling  | Any field confidence < threshold        | Re-run Sonnet 4.6 on same image → variance comparison on cost / severity / make-model    | Variance signal that surfaces uncertain assessments adjusters should double-check. |
| 1.5   | Haiku triage tier          | All claims (the only ungated chain)     | Haiku 4.5 image-quality + tier triage → escalate to Sonnet on pass, short-circuit on bad input | Cuts blended inference cost ~30% at scale; the only chain that *reduces* spend. |
| 1.5   | Parts-pricing fusion       | Damage assessment complete              | Sonnet damage description → Mitchell / CCC ONE / Audatex parts API → Sonnet cost grounding | Replace in-prompt reference table with deterministic parts pricing.                |
| 2     | Adjuster co-pilot          | Adjuster opens claim review console     | Anthropic Managed Agents API — chained tool/model loop in a persistent session           | Stateful multi-turn workflows: reanalyze, generate PDF/DOCX, iterative refinement. |
| 3     | Fraud pipeline             | Suspect-similarity above threshold      | Image-hash dedup → vector similarity → AI pairwise on top-K → structured fraud report     | Multi-stage candidate narrowing makes the AI-pairwise step affordable.             |

**Design rule.** Every chain ships with: (a) a named failure mode it addresses, (b) a measured baseline error rate on that failure mode, (c) a trigger condition gating the chain to a subset of traffic, and (d) an A/B-validated metric move versus the single-call baseline. Chains that fail to earn their keep are removed in quarterly review.

**Anti-patterns explicitly out of scope.** The single-call assessment is *not* split into vehicle-ID → damage → cost stages — adaptive thinking already runs that reasoning internally inside one call, and splitting it adds latency, breaks cross-stage information flow, and creates coherence risk. Generic "verifier" stages without a named failure mode are also out of scope: two calls of the same model on the same input mostly agree with themselves, producing 2× cost for no real signal.

### Deployment model

- Multi-tenant SaaS, with per-carrier data isolation at the database row level (PostgreSQL RLS) or schema level (depending on carrier requirements).
- Deployed in AWS us-east-1 with PrivateLink option for carriers requiring private connectivity.
- SOC 2 Type II in progress; HIPAA-equivalent controls for PII handling.

---

## 3. Milestones and Timeline

| Phase | Milestone                                                          | Deliverables                                                                                                       | Duration         |
| ----- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------------- |
| 0     | **Prototype** *(delivered)*                                        | Single-image upload + AI assessment. Local-run Next.js app + this SOW.                                             | ✅ Complete      |
| 1     | **Pilot launch (production v1)**                                   | Hosted multi-tenant app, carrier SSO, persistence, audit log, PII redaction, claims-system integration (1 carrier). | 8 weeks          |
| 1.5   | **Production cost integration + bulk reprocessing**                | Mitchell or CCC ONE replaces the in-prompt reference table for cost data. Calibration data collection begins. Operationalizes the Anthropic Messages Batches API for non-latency-sensitive workloads — model-upgrade reanalysis, historical fraud-detection backfill, and overnight compliance audits at 50% of synchronous-API cost. | 4 weeks          |
| 2     | **Multi-image flows + adjuster co-pilot**                          | Multi-angle upload, side-by-side and AI-powered before/after comparison for repair verification. Introduces an interactive **adjuster co-pilot** built on Anthropic's Managed Agents API — a persistent stateful session per claim where adjusters can request reanalysis, generate claim documents (PDF/DOCX), and iteratively refine the assessment. Single-call architecture from Phase 1 continues to handle batch first-pass assessment; Managed Agents handles the interactive layer. | 6 weeks          |
| 3     | **Fraud-signal pipeline**                                          | Image-hash dedup, visual-similarity scoring against historical claims, AI pairwise comparison on top suspects. Long-running fraud investigations run as Managed Agents sessions with custom tools that pull related claims from the carrier's database, compare photos pairwise, and produce a structured fraud report for SIU review. | 8 weeks          |
| 4     | **National rollout + multi-carrier**                               | Hardening, SLA tuning, observability, additional carrier onboarding, mobile-first UX refinements.                  | Ongoing          |

**Phase 1 weekly breakdown (8 weeks):**

| Week | Focus                                                                                              |
| ---- | -------------------------------------------------------------------------------------------------- |
| 1    | Discovery: adjuster workflow shadowing, claim-volume profiling, ground-truth dataset assembly      |
| 2    | Auth (SSO), persistence layer, deployment infrastructure                                           |
| 3    | PII redaction service, audit log                                                                   |
| 4    | Claims-system integration (carrier sandbox)                                                        |
| 5    | Adjuster review console (web UI), reanalysis flow                                                  |
| 6    | Calibration: tune confidence thresholds against ground-truth dataset                               |
| 7    | UAT with pilot adjuster cohort, bug fixes                                                          |
| 8    | Production cutover (limited cohort), runbook handoff to carrier IT                                 |

---

## 4. Risk Assessment

| Risk                                                                                | Likelihood | Impact | Mitigation                                                                                                                                                                                                                                                            |
| ----------------------------------------------------------------------------------- | ---------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cost estimate accuracy below adjuster expectations**                              | Medium     | High   | Phase 1.5 replaces the in-prompt reference table with Mitchell/CCC parts-level pricing. In Phase 1, cost is presented as a *range* with confidence and cited sources, with explicit "AI estimate, adjuster reviews" framing. Confidence-routed escalation to human for low confidence. |
| **AI misidentifies vehicle make/model on uncommon cars**                            | Medium     | Medium | Per-field confidence surfaced to adjuster. Adjuster can override. Calibration data collected from overrides feeds back into prompt tuning. VIN cross-reference via NHTSA vPIC (Phase 2) catches mismatches.                                                          |
| **PII leakage (license plate, GPS in EXIF, face)**                                  | Low        | High   | Server-side EXIF stripping before any AI provider sees the image. Phase 1 adds CV-based plate/face redaction. SOC 2 controls and per-carrier data isolation. No image leaves the platform without redaction.                                                          |
| **Low-quality input photos (blur, dark, partial view)**                             | High       | Medium | Image-quality scoring built into the AI pipeline; low quality caps confidence and triggers human review. UI surfaces specific quality issues so the user can retake.                                                                                                  |
| **Adjuster distrust of AI / change-management resistance**                          | High       | High   | Pilot launches as advisory tool only — no auto-decisions. Confidence indicators and source citations make every output auditable. Adjuster shadowing (Week 1) builds workflow alignment. Calibration phase gives adjusters control over thresholds.                  |
| **Anthropic API outage or rate-limit pressure during peak claim volume**            | Low        | High   | Multi-region failover, request queuing with SLA-bounded backoff, fallback to traditional desk-review queue. Business continuity runbook in place.                                                                                                                    |
| **Cost overrun on AI inference at scale**                                           | Medium     | Medium | Token-budget monitoring per claim. Image preprocessing caps input cost. Haiku 4.5 fallback for low-stakes claims (<$2k) reduces per-claim cost ~5×. Caching of repeated system-prompt + schema reduces input cost ~90%.                                                |
| **Regulatory: state-level disclosure requirements for AI in insurance decisions**   | Medium     | High   | All Phase 1 outputs are advisory only — final decisions stay with licensed adjuster. UI clearly labels AI-generated content. Compliance review per state of operation.                                                                                               |
| **Fraud actors exploit AI auto-handling on simple claims**                          | Medium     | High   | Phase 3 fraud-signal pipeline. Phase 1 mitigations: image-hash deduplication, sliding confidence thresholds for repeat claimants, sampling rate of human review on auto-handled claims.                                                                              |
| **Vendor lock-in (single-LLM dependency)**                                          | Low        | Medium | API contract for AI service is encapsulated in a single orchestration module. Phase 4 adds cross-vendor abstraction if needed. Open-source vision models evaluated as fallback for non-critical paths.                                                               |

---

## 5. Success Metrics

KPIs are tracked from Day 1 of pilot. Targets are for the end of Phase 1 (8 weeks post-launch on the pilot cohort).

### Primary KPIs

| KPI                                                | Baseline              | Phase 1 Target              | Why it matters                                                          |
| -------------------------------------------------- | --------------------- | --------------------------- | ----------------------------------------------------------------------- |
| **Time to first damage assessment**                | 4–24h (adjuster desk) | < 5 min (AI-first pass)     | Customer satisfaction; cycle-time reduction directly maps to NPS uplift |
| **Adjuster touch-time per claim** (simple claims)  | ~15 min               | < 5 min                     | Adjuster capacity unlocked for complex claims                           |
| **Cost-estimate accuracy** (within ±15% of final)  | N/A                   | ≥ 75% on pilot cohort       | Trust signal; if estimates are unreliable, adjusters won't lean on them |
| **Auto-handle rate** (simple claims, no escalation) | 0%                    | 30% of qualifying claims    | Volume unlocked; revenue model justification                            |
| **Adjuster override rate**                         | N/A                   | < 25% of AI assessments     | Calibration health; high override rate = retune prompt or thresholds   |

### Quality and trust KPIs

| KPI                                                  | Target                            |
| ---------------------------------------------------- | --------------------------------- |
| Confidence calibration (claimed vs. measured accuracy) | Within 10 percentage points       |
| Severity-classification accuracy                     | ≥ 85% agreement with adjuster     |
| PII-redaction false-negative rate                    | < 0.1% (1 in 1000 images)         |
| `requires_human_review` precision                    | ≥ 80% (when flagged, review was warranted) |
| `requires_human_review` recall                       | ≥ 95% (claims that needed review were flagged) |

### Operational KPIs

| KPI                                                       | Target              |
| --------------------------------------------------------- | ------------------- |
| API availability (rolling 30 days)                        | ≥ 99.9%             |
| p95 end-to-end analysis latency                           | < 60s               |
| p99 end-to-end analysis latency                           | < 90s               |
| Cost per analyzed claim (compute + AI)                    | < $0.50             |
| Audit-log completeness                                    | 100% (compliance)   |
| Bulk reprocessing SLA (Batches API runs, Phase 1.5+)      | ≥ 95% within 24h    |
| Bulk-vs-realtime cost delta (validation of 50% savings)   | ≥ 45% measured savings on Batches workloads |

### Business KPIs (Phase 1.5+ as data accumulates)

- **Loss-cost reduction** on pilot cohort vs. control cohort: target 3–5% via faster cycle-time and more consistent estimates.
- **Customer NPS** on claim handling: target +10 points on pilot vs. baseline.
- **Adjuster satisfaction** with the AI-assist workflow: target 4.0+ on a 5-point scale by end of Phase 1.

### Reporting cadence

- **Weekly:** Operational KPIs + adjuster override rate (during Phase 1)
- **Bi-weekly:** Quality KPIs (confidence calibration, severity accuracy)
- **Monthly:** Business KPIs + pilot vs. control comparison
- **Quarterly:** Executive review with carrier leadership

---

## Appendix A — Sign-off

| Role                                  | Name | Date |
| ------------------------------------- | ---- | ---- |
| Carrier Project Sponsor               |      |      |
| Carrier Claims Operations Lead        |      |      |
| Solutions Engineering Lead            |      |      |
| Implementation Manager                |      |      |
