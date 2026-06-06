import { errorResponse } from "./responses";
import { routeRequest } from "./routes";

export { RunStateDurableObject } from "./run-state-do";

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    try {
      void ctx;
      const url = new URL(request.url);
      if (request.method === "GET" && url.pathname === "/health") {
        return new Response(
          JSON.stringify(
            {
              status: "ok",
              schemaVersion: "worker_run_state/v2",
              now: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
              service: "cad-agent-orchestrator",
              version: env.ORCHESTRATOR_VERSION || "mvp-0.2.0",
              workspaceId: env.DEFAULT_WORKSPACE_ID || "cad-agent-core-lab",
              boundaries: {
                workerExecutesShell: false,
                workerSavesCurrentDwg: false,
                cadReadbackRequiredForCadClaims: true,
              },
            },
            null,
            2,
          ),
          { headers: { "Content-Type": "application/json; charset=utf-8" } },
        );
      }
      return await routeRequest(request, env);
    } catch (error) {
      return errorResponse(error, request, env);
    }
  },
} satisfies ExportedHandler<Env>;
