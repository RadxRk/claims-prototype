import Anthropic from "@anthropic-ai/sdk";

let _client: Anthropic | null = null;

/**
 * Lazily construct the Anthropic client. We don't evaluate API key presence
 * at module-load time so that `next build` (which evaluates route modules)
 * doesn't fail in environments without the key set.
 */
export function getAnthropicClient(): Anthropic {
  if (!_client) {
    if (!process.env.ANTHROPIC_API_KEY) {
      throw new Error(
        "ANTHROPIC_API_KEY environment variable is not set. Copy .env.local.example to .env.local and add your key."
      );
    }
    _client = new Anthropic();
  }
  return _client;
}

export const MODEL = "claude-sonnet-4-6";
