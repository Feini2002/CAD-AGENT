import type { JsonObject, JsonValue } from "./types";

const SENSITIVE_KEY_PATTERN = /authorization|bearer|token|secret|password|heartbeatToken|fullPrompt|prompt|cadData|repositoryPath|localPath/i;
const WINDOWS_PATH_PATTERN = /[A-Za-z]:\\(?:[^\\\s]+\\)+[^\\\s]*/g;

export function redactForLog<T>(value: T): T {
  return redactValue(value) as T;
}

function redactValue(value: unknown): JsonValue | undefined {
  if (Array.isArray(value)) {
    return value.map((item) => redactValue(item) ?? null);
  }
  if (value && typeof value === "object") {
    const result: JsonObject = {};
    for (const [key, item] of Object.entries(value as Record<string, unknown>)) {
      if (SENSITIVE_KEY_PATTERN.test(key)) {
        result[key] = "[redacted]";
      } else {
        result[key] = redactValue(item) ?? null;
      }
    }
    return result;
  }
  if (typeof value === "string") {
    return value.replace(WINDOWS_PATH_PATTERN, "[local-path]");
  }
  if (typeof value === "number" || typeof value === "boolean" || value === null) {
    return value;
  }
  return undefined;
}
