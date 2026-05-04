/**
 * Minimal Server-Sent Events client for `fetch`-based POST endpoints.
 * The native EventSource API only supports GET requests, so for our
 * streaming POST /api/analyze endpoint we parse the SSE wire format manually.
 */
export type SSEHandler = (event: string, data: unknown) => void;

export async function streamSSE(response: Response, onEvent: SSEHandler): Promise<void> {
  if (!response.body) throw new Error("Response has no body");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by a blank line ("\n\n").
    let separatorIdx;
    while ((separatorIdx = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, separatorIdx);
      buffer = buffer.slice(separatorIdx + 2);

      let eventType = "message";
      const dataLines: string[] = [];
      for (const line of rawEvent.split("\n")) {
        if (line.startsWith("event:")) {
          eventType = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          dataLines.push(line.slice(5).trim());
        }
      }
      if (dataLines.length === 0) continue;
      try {
        onEvent(eventType, JSON.parse(dataLines.join("\n")));
      } catch (err) {
        console.warn("Failed to parse SSE data:", err, dataLines);
      }
    }
  }
}
