import { z } from "zod";

export const ConfidenceLevel = z.enum(["high", "medium", "low"]);

export const AffectedArea = z.object({
  location: z.string().describe("e.g., 'rear bumper, driver side'"),
  damage_type: z.string().describe("dent, scratch, crack, paint damage, broken glass, etc."),
  area_confidence: z.number().int().min(0).max(100),
});

export const AnalysisSchema = z.object({
  car: z.object({
    make: z.string(),
    model: z.string(),
    color: z.string(),
    year_estimate: z.string().describe("approximate year or range, e.g., '2018-2020'"),
    field_confidences: z.object({
      make: z.number().int().min(0).max(100),
      model: z.number().int().min(0).max(100),
      color: z.number().int().min(0).max(100),
      year: z.number().int().min(0).max(100),
    }),
    confidence_reasoning: z.string(),
  }),
  damage: z.object({
    summary: z.string().describe("single-sentence overview, e.g., 'Left rear bumper dent with paint scratch'"),
    affected_areas: z.array(AffectedArea),
    severity: z.enum(["minor", "moderate", "severe"]),
    severity_confidence: z.number().int().min(0).max(100),
    confidence_reasoning: z.string(),
  }),
  repair_estimate: z.object({
    low_usd: z.number().int().nonnegative(),
    high_usd: z.number().int().nonnegative(),
    confidence: z.number().int().min(0).max(100),
    reasoning: z.string(),
    sources: z.array(z.string()).describe("citations supporting the cost estimate (e.g., reference-table tier, industry knowledge)"),
  }),
  image_quality: z.object({
    score: z.number().int().min(0).max(100),
    issues: z.array(z.string()).describe("e.g., ['blurry', 'poor lighting', 'partial view']"),
  }),
  requires_human_review: z.boolean(),
  review_triggers: z.array(z.string()).describe("specific reasons review is recommended"),
  analysis_notes: z.string().describe("human-readable explanation of the analysis"),
});

export type Analysis = z.infer<typeof AnalysisSchema>;

// ─── Structured human-review triggers ─────────────────────────────────────
// Computed server-side after Claude returns. Each trigger is a typed object
// rather than a free-form string, so downstream code can route, filter, or
// render them deterministically.

export type Trigger =
  | { code: "low_confidence"; field: string; value: number; threshold: number; label: string }
  | { code: "severe_damage"; label: string }
  | { code: "poor_image_quality"; value: number; threshold: number; label: string }
  | { code: "high_value"; value: number; threshold: number; label: string };

export const REVIEW_THRESHOLDS = {
  CONFIDENCE: 30,
  IMAGE_QUALITY: 50,
  HIGH_VALUE_USD: 9000,
} as const;

export function computeTriggers(a: Analysis): Trigger[] {
  const out: Trigger[] = [];

  // 1. Low confidence — check every confidence field
  const checks: Array<[string, number]> = [
    ["car.make", a.car.field_confidences.make],
    ["car.model", a.car.field_confidences.model],
    ["car.color", a.car.field_confidences.color],
    ["car.year", a.car.field_confidences.year],
    ["damage.severity", a.damage.severity_confidence],
    ["repair_estimate", a.repair_estimate.confidence],
  ];
  for (const [field, value] of checks) {
    if (value < REVIEW_THRESHOLDS.CONFIDENCE) {
      out.push({
        code: "low_confidence",
        field,
        value,
        threshold: REVIEW_THRESHOLDS.CONFIDENCE,
        label: `Low confidence on ${field.replace(".", " ")}: ${value}/100`,
      });
    }
  }

  // 2. Severe damage
  if (a.damage.severity === "severe") {
    out.push({
      code: "severe_damage",
      label: "Severity classified as severe — possible structural or safety-system involvement",
    });
  }

  // 3. Poor image quality
  if (a.image_quality.score < REVIEW_THRESHOLDS.IMAGE_QUALITY) {
    out.push({
      code: "poor_image_quality",
      value: a.image_quality.score,
      threshold: REVIEW_THRESHOLDS.IMAGE_QUALITY,
      label: `Image quality is ${a.image_quality.score}/100 — assessment may miss damage detail`,
    });
  }

  // 4. High value
  if (a.repair_estimate.high_usd > REVIEW_THRESHOLDS.HIGH_VALUE_USD) {
    out.push({
      code: "high_value",
      value: a.repair_estimate.high_usd,
      threshold: REVIEW_THRESHOLDS.HIGH_VALUE_USD,
      label: `Repair estimate high end is $${a.repair_estimate.high_usd.toLocaleString()} (above $${REVIEW_THRESHOLDS.HIGH_VALUE_USD.toLocaleString()} threshold)`,
    });
  }

  return out;
}

// JSON Schema for Claude's output_config.format.
// Note: structured outputs do NOT support `minimum`/`maximum`/`multipleOf` on
// integer types — those constraints must be enforced client-side via Zod.
// Range guidance is communicated to the model via the system prompt + field
// descriptions instead.
export const ANALYSIS_JSON_SCHEMA = {
  type: "object",
  properties: {
    car: {
      type: "object",
      properties: {
        make: { type: "string" },
        model: { type: "string" },
        color: { type: "string" },
        year_estimate: { type: "string", description: "approximate year or range, e.g., '2018-2020'" },
        field_confidences: {
          type: "object",
          properties: {
            make: { type: "integer", description: "0-100 confidence" },
            model: { type: "integer", description: "0-100 confidence" },
            color: { type: "integer", description: "0-100 confidence" },
            year: { type: "integer", description: "0-100 confidence" },
          },
          required: ["make", "model", "color", "year"],
          additionalProperties: false,
        },
        confidence_reasoning: { type: "string" },
      },
      required: ["make", "model", "color", "year_estimate", "field_confidences", "confidence_reasoning"],
      additionalProperties: false,
    },
    damage: {
      type: "object",
      properties: {
        summary: { type: "string" },
        affected_areas: {
          type: "array",
          items: {
            type: "object",
            properties: {
              location: { type: "string" },
              damage_type: { type: "string" },
              area_confidence: { type: "integer", description: "0-100 confidence" },
            },
            required: ["location", "damage_type", "area_confidence"],
            additionalProperties: false,
          },
        },
        severity: { type: "string", enum: ["minor", "moderate", "severe"] },
        severity_confidence: { type: "integer", description: "0-100 confidence" },
        confidence_reasoning: { type: "string" },
      },
      required: ["summary", "affected_areas", "severity", "severity_confidence", "confidence_reasoning"],
      additionalProperties: false,
    },
    repair_estimate: {
      type: "object",
      properties: {
        low_usd: { type: "integer", description: "low end of repair cost range, USD" },
        high_usd: { type: "integer", description: "high end of repair cost range, USD" },
        confidence: { type: "integer", description: "0-100 confidence in the cost estimate" },
        reasoning: { type: "string" },
        sources: { type: "array", items: { type: "string" }, description: "citations supporting the cost estimate (e.g., reference-table tier, industry knowledge)" },
      },
      required: ["low_usd", "high_usd", "confidence", "reasoning", "sources"],
      additionalProperties: false,
    },
    image_quality: {
      type: "object",
      properties: {
        score: { type: "integer", description: "0-100 image quality score" },
        issues: { type: "array", items: { type: "string" } },
      },
      required: ["score", "issues"],
      additionalProperties: false,
    },
    requires_human_review: { type: "boolean" },
    review_triggers: { type: "array", items: { type: "string" } },
    analysis_notes: { type: "string" },
  },
  required: [
    "car",
    "damage",
    "repair_estimate",
    "image_quality",
    "requires_human_review",
    "review_triggers",
    "analysis_notes",
  ],
  additionalProperties: false,
} as const;
