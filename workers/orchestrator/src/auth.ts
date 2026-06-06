import { DEFAULT_WORKSPACE_ID } from "./constants";
import { ApiError } from "./responses";
import type { AuthContext, AuthRole } from "./types";

export async function authenticate(
  request: Request,
  env: Env,
  allowedRoles: AuthRole[],
  claims: { workspaceId?: string; bridgeId?: string } = {},
): Promise<AuthContext> {
  if (allowedRoles.includes("anonymous")) {
    return anonymousContext(env);
  }

  const token = bearerToken(request);
  if (!token) {
    throw new ApiError(401, "auth_missing", "Authorization bearer token is required.");
  }

  const candidates = [
    {
      role: "admin" as const,
      secret: env.ADMIN_API_TOKEN,
      subjectId: "admin:orchestrator",
      tokenId: "admin_api_token",
      workspaces: ["*"],
      bridges: ["*"],
    },
    {
      role: "user" as const,
      secret: env.WORKER_API_TOKEN,
      subjectId: "user:worker_api",
      tokenId: "worker_api_token",
      workspaces: splitEnvList(env.ALLOWED_WORKSPACE_IDS || env.DEFAULT_WORKSPACE_ID || DEFAULT_WORKSPACE_ID),
      bridges: [],
    },
    {
      role: "bridge" as const,
      secret: env.BRIDGE_API_TOKEN,
      subjectId: bridgeSubject(env),
      tokenId: "bridge_api_token",
      workspaces: splitEnvList(env.ALLOWED_WORKSPACE_IDS || env.DEFAULT_WORKSPACE_ID || DEFAULT_WORKSPACE_ID),
      bridges: splitEnvList(env.ALLOWED_BRIDGE_IDS || env.DEFAULT_BRIDGE_ID || "bridge_local_smoke"),
    },
  ];

  for (const candidate of candidates) {
    if (!candidate.secret) {
      continue;
    }
    if (!(await constantTimeSecretEqual(token, candidate.secret))) {
      continue;
    }
    if (!allowedRoles.includes(candidate.role)) {
      throw new ApiError(403, "auth_role_forbidden", `Role ${candidate.role} cannot access this route.`);
    }
    const context: AuthContext = {
      role: candidate.role,
      subjectId: candidate.role === "bridge" && claims.bridgeId ? `bridge:${claims.bridgeId}` : candidate.subjectId,
      tokenId: candidate.tokenId,
      allowedTenantIds: ["default"],
      allowedWorkspaceIds: candidate.workspaces,
      allowedBridgeIds: candidate.bridges,
    };
    assertClaimsAllowed(context, claims);
    return context;
  }

  throw new ApiError(401, "auth_invalid", "Bearer token is invalid.");
}

export function assertClaimsAllowed(context: AuthContext, claims: { workspaceId?: string; bridgeId?: string }): void {
  if (claims.workspaceId && !isAllowed(context.allowedWorkspaceIds, claims.workspaceId)) {
    throw new ApiError(403, "auth_role_forbidden", "Auth subject is not allowed for this workspace.");
  }
  if (context.role === "bridge" && claims.bridgeId && !isAllowed(context.allowedBridgeIds, claims.bridgeId)) {
    throw new ApiError(403, "bridge_identity_mismatch", "Bridge token cannot claim this bridgeId.");
  }
}

export function requireAdmin(context: AuthContext): void {
  if (context.role !== "admin") {
    throw new ApiError(403, "auth_role_forbidden", "Admin role is required.");
  }
}

export function splitEnvList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function bearerToken(request: Request): string {
  const header = request.headers.get("Authorization") || "";
  const match = /^Bearer\s+(.+)$/i.exec(header.trim());
  return match?.[1]?.trim() || "";
}

function anonymousContext(env: Env): AuthContext {
  return {
    role: "anonymous",
    subjectId: "anonymous",
    tokenId: "anonymous",
    allowedTenantIds: ["default"],
    allowedWorkspaceIds: splitEnvList(env.ALLOWED_WORKSPACE_IDS || env.DEFAULT_WORKSPACE_ID || DEFAULT_WORKSPACE_ID),
    allowedBridgeIds: [],
  };
}

function bridgeSubject(env: Env): string {
  const bridges = splitEnvList(env.ALLOWED_BRIDGE_IDS || env.DEFAULT_BRIDGE_ID || "bridge_local_smoke");
  return `bridge:${bridges[0] || "bridge_local_smoke"}`;
}

function isAllowed(allowed: string[], value: string): boolean {
  return allowed.includes("*") || allowed.includes(value);
}

async function constantTimeSecretEqual(left: string, right: string): Promise<boolean> {
  if (!left || !right) {
    return false;
  }
  const [leftDigest, rightDigest] = await Promise.all([digest(left), digest(right)]);
  if (leftDigest.byteLength !== rightDigest.byteLength) {
    return false;
  }
  let diff = 0;
  const leftBytes = new Uint8Array(leftDigest);
  const rightBytes = new Uint8Array(rightDigest);
  for (let index = 0; index < leftBytes.length; index += 1) {
    diff |= leftBytes[index] ^ rightBytes[index];
  }
  return diff === 0;
}

function digest(value: string): Promise<ArrayBuffer> {
  return crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
}
