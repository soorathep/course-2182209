import handler from "vinext/server/fetch-handler";
import { authorizeInstructor, privateHeaders } from "../lib/instructor-policy.mjs";
import { runWithConnectorBinding } from "../lib/connector-context";
import type { ConnectorBinding } from "../lib/connector-contract.mjs";

const worker = {
  async fetch(request: Request, env: Cloudflare.Env, ctx: ExecutionContext<{ CONNECTORS?: ConnectorBinding }>) {
    const pathname = new URL(request.url).pathname;
    const protectedApi = pathname === "/api/instructor" || pathname.startsWith("/api/instructor/");
    const studentApi = pathname === "/api/exit-tickets" || pathname.startsWith("/api/exit-tickets/") || pathname.startsWith("/api/teaching-feedback/");
    const protectedPage = pathname === "/instructor" || pathname.startsWith("/instructor/");
    if (protectedApi) {
      const identity = { userId: request.headers.get("oai-authenticated-user-id"), email: request.headers.get("oai-authenticated-user-email") };
      const access = authorizeInstructor(identity, (env as unknown as Record<string, string | undefined>).COURSE_INSTRUCTOR_EMAILS);
      if (!access.allowed) return Response.json({ error: access.status === 401 ? "sign_in_required" : "instructor_access_required" }, { status: access.status, headers: privateHeaders });
    }
    let binding = ctx.props?.CONNECTORS;
    // Local preview emulates the same request-scoped capability. This branch and
    // the auxiliary service binding are absent from production builds.
    if (import.meta.env.DEV && !binding && env.CONNECTORS) {
      const preview = env.CONNECTORS;
      const expiresAt = Date.now() + 60_000;
      binding = {
        async getContext() {
          if (Date.now() >= expiresAt) return { status: "request_context_expired" };
          return preview.getContext?.() ?? { status: "binding_unavailable" };
        },
        async invoke(connectorId, actionName, args) {
          if (Date.now() >= expiresAt) {
            return { status: "request_context_expired", message: "This request has expired. Please try again." };
          }
          return preview.invoke(connectorId, actionName, args);
        },
      };
    }
    const response = await runWithConnectorBinding(binding, () => handler.fetch(request, env, ctx));
    const secured = new Response(response.body, response);
    secured.headers.set("X-Content-Type-Options", "nosniff");
    secured.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
    if (protectedApi || protectedPage || studentApi) {
      for (const [name, value] of Object.entries(privateHeaders)) {
        if (name.toLowerCase() === "vary") {
          const combined = [...new Set([...(secured.headers.get("Vary") ?? "").split(","), ...value.split(",")].map(item => item.trim()).filter(Boolean))];
          secured.headers.set("Vary", combined.join(", "));
        } else secured.headers.set(name, value);
      }
    }
    return secured;
  },
};

export default worker;
