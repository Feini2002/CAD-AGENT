import type { JsonObject } from "./types";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: JsonObject,
  ) {
    super(message);
  }
}

export function jsonResponse(
  payload: unknown,
  init: ResponseInit = {},
  request?: Request,
  env?: Env,
): Response {
  const headers = responseHeaders(init.headers, request, env);
  headers.set("Content-Type", "application/json; charset=utf-8");
  return new Response(JSON.stringify(payload, null, 2), {
    ...init,
    headers,
  });
}

export function errorResponse(error: unknown, request?: Request, env?: Env): Response {
  if (error instanceof ApiError) {
    return rawJsonError(error.status, {
      error: error.code,
      message: error.message,
      ...(error.details ? { details: error.details } : {}),
    });
  }
  if (isApiLikeError(error)) {
    return rawJsonError(error.status, {
      error: error.code,
      message: error.message || error.code,
      ...(error.details ? { details: error.details } : {}),
    });
  }
  const message = error instanceof Error ? error.message : String(error);
  console.error(JSON.stringify({ level: "error", message: "worker_request_failed", error: message }));
  return rawJsonError(500, { error: "internal_error", message: "Internal server error" });
}

function isApiLikeError(error: unknown): error is { status: number; code: string; message?: string; details?: JsonObject } {
  if (!error || typeof error !== "object") {
    return false;
  }
  const candidate = error as Record<string, unknown>;
  return typeof candidate.status === "number" && typeof candidate.code === "string";
}

function rawJsonError(status: number, payload: JsonObject): Response {
  return new Response(JSON.stringify(payload, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
    },
  });
}

export function optionsResponse(request: Request, env: Env): Response {
  return new Response(null, { status: 204, headers: responseHeaders(undefined, request, env) });
}

function responseHeaders(initHeaders?: HeadersInit, request?: Request, env?: Env): Headers {
  const headers = new Headers(initHeaders);
  const origin = request?.headers.get("Origin") || "";
  const allowedOrigins = splitEnvList(env?.ALLOWED_ORIGINS || "");
  if (origin && allowedOrigins.includes(origin)) {
    headers.set("Access-Control-Allow-Origin", origin);
    headers.set("Vary", "Origin");
    headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization, Idempotency-Key, X-Request-Id");
  }
  return headers;
}

function splitEnvList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
