# Partner Operations Copilot

A partner and internal-team demo for deal-registration and quote-status questions, with a human-reviewed support queue for complex cases.

## Run & Operate

- `bash scripts/run-api-stack.sh development` — run Express plus the Python graph service from the repository root
- `uv run pytest -q` — deterministic graph, scope, and recovery tests
- `uv run python -m partner_agent_graph.setup_checkpoint` — one-time development checkpoint schema setup; not a production startup task
- `pnpm run typecheck` — full typecheck across all packages
- `PORT=5000 BASE_PATH=/ pnpm run build` — typecheck + build all packages outside the managed artifact environment
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string
- Optional secret: `NEBIUS_API_KEY` — enables Nebius Token Factory answers; the UI uses a grounded local fallback if it is absent

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5 proxy + internal Python FastAPI service
- Agent: Python 3.13, LangChain, LangGraph, and Nebius tool calling
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `artifacts/partner-status-agent/` — partner dashboard and status agent.
- `artifacts/partner-status-agent/docs/week-3-submission-notes.md` — project overview and Week 3 agent framework.
- `artifacts/api-server/src/routes/partner-agent.ts` — guarded, rate-limited proxy to the Python agent.
- `src/partner_agent_graph/` — graph, scoped tools, API, and checkpoint setup.
- `lib/api-spec/openapi.yaml` — source contract for generated API hooks and validators.
- `artifacts/partner-status-agent/src/App.tsx` — Partner/Staff demo workflows and local persistence.

## Architecture decisions

- Deal, quote, guide, and partner examples are local demo data; submitted support requests and staff responses persist in browser local storage.
- The user chose the Python LangChain + LangGraph track and synthetic data for the public LinkedIn portfolio demo.
- LangGraph selects read-only tools and keeps conversation state in PostgreSQL checkpoints. Without a working provider, exact-match questions use a labeled deterministic fallback.
- Demo roles are a convenience, not authentication. Salesforce is not connected, and no action writes to a CRM or sends messages.
- Pricing, credit-hold, eligibility, and exception decisions remain with a human.

## Product

- Partner view: check deal registrations and quote status, read the registration guide, ask grounded questions, and submit support requests.
- Staff view: review partner requests, assign an owner, update local status, and record a human response.
- Source labels and timestamps distinguish sample data from live CRM information.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Do not present demo records or the role switch as live Salesforce data or secure access control.
- Before any external partner pilot, add real authentication and server-side partner/tenant authorization.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
