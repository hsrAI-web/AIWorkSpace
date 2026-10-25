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
- Secret: `NEBIUS_API_KEY` — enables Nebius chat and public-knowledge embeddings. Without it, only supported exact-record questions can use a labeled deterministic fallback; knowledge retrieval must not answer from model memory.
- Salesforce: the managed connector must target the approved Developer Edition org; its fixed partner/registration allowlist is not a general CRM integration.

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5 proxy + internal Python FastAPI service
- Agent: Python 3.13, LangChain, LangGraph, Nebius tool calling, and Qwen3 semantic embeddings
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

- Red Valley and Bluewater registrations are read from a fixed Salesforce Developer Edition sample set. Other registration examples, all quote examples, and the local guide use demo JSON; support requests and staff responses persist in browser local storage.
- The public portfolio demo uses only sample data, including the allowlisted Developer Edition records. Public knowledge comes from curated source snapshots, not company policy or internal assets.
- LangGraph selects read-only tools and keeps conversation state in PostgreSQL checkpoints. Without a working provider, exact-match questions use a labeled deterministic fallback.
- Four read-only tools cover registrations, synthetic quotes, the local registration guide, and public-knowledge search. Embeddings are cached in process; there is no persistent vector database or live web search.
- Demo roles are a convenience, not authentication. Salesforce access is read-only; no action writes to CRM or sends messages. Native Salesforce Quotes are not enabled.
- Pricing, credit-hold, eligibility, and exception decisions remain with a human.

## Product

- Partner view: check demo registrations and synthetic quote status, read the registration guide, ask source-grounded public knowledge questions, and save local support requests.
- Staff view: review partner requests, assign an owner, update local status, and record a human response.
- Source labels and timestamps distinguish sample data from live CRM information.

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Distinguish Salesforce-sourced sample registrations from local synthetic records. Never present the role switch as secure access control or public references as approved company guidance.
- The older `partner-copilot-walkthrough` film is a historical, pre-Salesforce/pre-public-knowledge snapshot. Use the current explainer and live demo script for final submissions, not that film.
- Before any external partner pilot, add real authentication and server-side partner/tenant authorization.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
