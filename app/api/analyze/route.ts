import { toFile } from "@anthropic-ai/sdk";
import { getAnthropicClient, MODEL } from "@/lib/anthropic";
import { preprocessImage } from "@/lib/preprocess";
import { ANALYSIS_JSON_SCHEMA, AnalysisSchema, computeTriggers } from "@/lib/schema";
import { SYSTEM_PROMPT } from "@/lib/system-prompt";

export const runtime = "nodejs";
export const maxDuration = 90;

const FILES_BETA = "files-api-2025-04-14";
const encoder = new TextEncoder();

function sse(event: string, data: unknown): Uint8Array {
  return encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}

export async function POST(request: Request) {
  // Parse input outside the stream so request validation errors return as
  // normal JSON 4xx responses (not as in-stream events).
  let imageBuffer: Buffer;
  let filename: string;
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    if (!(file instanceof File)) {
      return Response.json({ error: "No file uploaded under the 'file' field" }, { status: 400 });
    }
    imageBuffer = Buffer.from(await file.arrayBuffer());
    filename = file.name || "upload.jpg";
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to read request";
    return Response.json({ error: message }, { status: 400 });
  }

  const stream = new ReadableStream({
    async start(controller) {
      const send = (event: string, data: unknown) => {
        try {
          controller.enqueue(sse(event, data));
        } catch {
          /* controller already closed */
        }
      };

      try {
        send("status", { message: "Preprocessing image (resize, EXIF strip)" });
        const processed = await preprocessImage(imageBuffer, filename);

        send("status", { message: "Uploading to Anthropic Files API" });
        const anthropic = getAnthropicClient();
        const uploaded = await anthropic.beta.files.upload({
          file: await toFile(processed.buffer, processed.filename, { type: processed.mimeType }),
          betas: [FILES_BETA],
        });

        send("status", { message: "Identifying vehicle and assessing damage" });

        const claudeStream = anthropic.beta.messages.stream({
          model: MODEL,
          max_tokens: 4096,
          thinking: { type: "adaptive" },
          system: SYSTEM_PROMPT,
          output_config: {
            format: {
              type: "json_schema",
              schema: ANALYSIS_JSON_SCHEMA as Record<string, unknown>,
            },
            effort: "low",
          },
          messages: [
            {
              role: "user",
              content: [
                { type: "image", source: { type: "file", file_id: uploaded.id } },
                {
                  type: "text",
                  text: "Analyze this damaged vehicle photo for an insurance claim. Return your analysis using the provided JSON schema.",
                },
              ],
            },
          ],
          betas: [FILES_BETA],
        });

        let announcedCompile = false;
        for await (const event of claudeStream) {
          if (event.type === "content_block_start") {
            const block = event.content_block;
            if (block.type === "text" && !announcedCompile) {
              announcedCompile = true;
              send("status", { message: "Generating structured output" });
            }
          }
        }

        const finalMessage = await claudeStream.finalMessage();
        const textBlock = finalMessage.content.find((b) => b.type === "text");
        if (!textBlock || textBlock.type !== "text") {
          send("error", { error: "Model did not return a text block with the analysis" });
          return;
        }

        let parsed;
        try {
          parsed = AnalysisSchema.parse(JSON.parse(textBlock.text));
        } catch (err) {
          console.error("Failed to parse analysis", err);
          send("error", { error: "Model returned malformed analysis", raw: textBlock.text });
          return;
        }

        // Compute structured triggers from the analysis output. This is the
        // server-side safety net — guaranteed to fire on the mechanical rules
        // (confidence, severity, image quality, cost) regardless of whether
        // Claude remembered to populate review_triggers.
        const triggers = computeTriggers(parsed);
        // Override requires_human_review from our deterministic computation.
        parsed.requires_human_review = triggers.length > 0;

        send("complete", {
          analysis: parsed,
          triggers,
          meta: {
            file_id: uploaded.id,
            model: MODEL,
            original_bytes: processed.originalBytes,
            processed_bytes: processed.processedBytes,
            dimensions: { width: processed.width, height: processed.height },
            usage: finalMessage.usage,
          },
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error";
        console.error("Analyze stream error:", err);
        send("error", { error: message });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
