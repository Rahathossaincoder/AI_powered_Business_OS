import { ApiError } from "../services/api/client";

/** Turns Django's {field: ["message"]} error object into {field: "message"}. */
export function fieldMessages(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError) || error.status !== 400) return {};
  const result: Record<string, string> = {};
  for (const [field, messages] of Object.entries(error.fieldErrors)) {
    result[field] = Array.isArray(messages) ? messages.join(" ") : String(messages);
  }
  return result;
}