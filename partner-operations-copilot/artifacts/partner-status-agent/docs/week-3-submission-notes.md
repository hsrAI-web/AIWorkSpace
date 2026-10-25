# Week 3 Project: Partner Operations Copilot

## Project overview

Partner Operations Copilot helps partners answer routine deal-registration and quote-status questions without repeatedly contacting an account representative. Internal staff can review exceptions, assign ownership, and record a response in the demo support queue.

This is a bring-your-own-use-case submission using the Python LangChain + LangGraph code track. It adapts the status-agent idea to partner operations; it does not claim to implement all six suggested projects or the Jira sprint-reporting project.

## Agent one-liner

My agent helps partners check deal registrations, quote progress, and registration requirements in a web workspace, replacing repeated manual follow-ups to individual representatives; it chooses among three read-only tools, remembers the conversation in PostgreSQL-backed LangGraph checkpoints, hands sensitive or unsupported questions to a human before any support-request write, and targets completion of eight out of ten routine tasks in under two minutes each.

The success rate and completion-time target have not been measured with real users. Automated functional checks are not evidence of business impact.

## Agent framework

### Agent goal
Answer routine partner operations questions with source evidence and a practical next step; route exceptions to a human without making commercial decisions.

### Where people use it
The browser application offers switchable Partner and Staff demo views. The role switch is not authentication or an authorization boundary.

### Steps, in order
1. Validate the selected synthetic partner and its conversation-thread identifier.
2. Run a deterministic safety gate for special pricing, credit holds, and eligibility.
3. For routine requests, let the Nebius model choose a LangChain tool inside a LangGraph loop.
4. Execute the read-only lookup with the partner scope injected by the graph, then return the result to the model.
5. Check for current-turn source evidence, cite the record or guide, and display the graph's execution trace.
6. If needed, prepare a support form; the partner reviews and explicitly submits it, and staff manually update the demo request.

### Actions and tools
- READ: `lookup_deal_status` retrieves a matching selected-partner registration.
- READ: `lookup_quote_status` retrieves a matching selected-partner quote.
- READ: `search_registration_guide` searches the approved synthetic registration guide.
- HUMAN WRITE: Save a browser-local support request after reviewing the form.
- HUMAN WRITE: Assign ownership, update request status, and record a staff response.

The LLM has no write tool and cannot create a request, send a message, or modify Salesforce.

### Memory and state
LangGraph stores conversation messages and graph checkpoints in PostgreSQL, keyed by a partner-prefixed thread ID. The browser keeps that ID per selected partner, so subsequent questions can refer to earlier records even after an API restart; a New conversation button starts a fresh thread.

The model receives a bounded recent-message window. Old checkpoint history remains in the database until explicitly cleaned up; there is no automatic retention/deletion policy in this demo. Support requests, staff updates, and view preferences are stored only in this browser, not shared across devices.

### Hard limits
Use synthetic records only. Never represent the role selector as secure access control, infer another partner's record from a failed ID match, approve discounts or eligibility, clear credit holds, write CRM data, or send external messages.

### Human-in-the-loop
Sensitive questions bypass the model and present a human-review action. Preparing the form does not save it: the partner must click Save support request, and a person in Staff view controls ownership, status, and response.

This is an application-level approval boundary, not a LangGraph `interrupt()`/resume implementation or a real staffed helpdesk.

### Failure handling
The tools return explicit not-found results; ToolNode converts tool exceptions into recoverable results. Model retries and timeouts, bounded tool rounds, and a graph recursion limit prevent uncontrolled execution.

An unavailable provider, tool error, or missing source produces a labeled deterministic exact-match fallback when possible, otherwise an honest no-answer and human-support option. Browser fallback is also labeled non-AI, and the public API applies in-memory demo usage limits.

### How success will be measured
Run ten predefined end-to-end tasks and measure source-correct task completion plus time to finish, including the human handoff when required. Target: eight successful tasks within two minutes each; no claim of measured partner wait-time reduction is made.

## Architecture

Browser (React/Vite)
→ generated OpenAPI client
→ Express validation and usage limits
→ loopback FastAPI service
→ LangGraph safety gate
→ Nebius agent ↔ scoped LangChain read-only tools
→ evidence check or human handoff
→ answer, source citations, and run trace.

PostgreSQL holds graph checkpoints. Browser storage holds the synthetic support queue. The FastAPI service listens on loopback and is not separately exposed as a public service.

## Datasets used

One canonical synthetic JSON dataset supplies both the UI and Python tools: four partner organizations, six deal registrations, five quotes, and one registration guide. The file is `artifacts/partner-status-agent/src/demo-records.json`.

Record dates are generated relative to the current date for demonstration. They are not live CRM refresh timestamps. No real Salesforce records, customer files, or private partner data are used.

## AI provider and credits

The model is `Qwen/Qwen3-30B-A3B-Instruct-2507` through Nebius Token Factory's OpenAI-compatible endpoint, invoked with LangChain ChatOpenAI. The Nebius key is configured as a server-side secret and a live graph run has been verified; it is never sent to the browser.

Routine questions generally need a tool-selection call plus an answer call, with a bounded allowance for more tools or a retry. Sensitive questions use the deterministic safety gate and need no model call.

Illustrative budget: if the account rate is $0.10 per million input tokens and $0.30 per million output tokens, three calls at 3,000 input and 600 output tokens each cost about $0.00144 per question, or $0.144 per 100 questions. Budget approximately $0.20–$0.35 per 100 questions as a test allowance; actual costs depend on token counts, retries, model availability, and account pricing. Hosting costs are separate.

LangChain and LangGraph do not require token-credit accounts. Tavily, Mem0, and LangSmith are not required or used in this version; there is no additional credential to supply for this demo.

## Prompts used during AI-assisted development

1. Initial brief: build an agent that helps partners with status updates, code status, release status, and potentially broader capabilities.
2. Product clarification: partners need help with deal registration, quote status, product positioning, renewals, eligibility, enablement assets, and complex issue routing; information is spread across portals, CRM, and email.
3. Selected scope: deal registration and quote status first, synthetic public-demo data, and switchable Partner / Staff views.
4. Selected implementation: Python LangChain + LangGraph, Nebius tool calling, persistent graph state, citations, safe failures, and human-controlled writes.

The runtime system prompt is maintained in `src/partner_agent_graph/graph.py`. It instructs the model to call tools for current facts, use conversation history only to resolve references, cite sources, refuse unsupported claims, and never make pricing/credit/eligibility decisions or external writes.

AI coding assistance was used to build the UI, define the API contract, implement the Python graph and tools, write tests, and prepare documentation. Outputs were checked with TypeScript checks, deterministic Python tests, live API requests, and a visual preview.

## Iterations and learnings

1. A broad status dashboard was narrowed to the user's highest-value first workflow: partner deal and quote support.
2. A one-shot model endpoint was replaced with a real agent/tool loop and PostgreSQL checkpointer. This separates the model's tool selection from the deterministic safety and evidence boundaries.
3. A shared synthetic dataset replaced separate UI and backend examples to avoid contradictory statuses.
4. Partner scope is injected by the tool runner rather than supplied by the model; explicit unknown IDs cannot fall through to fuzzy matching.
5. A simulated tool failure showed why a fallback must be labeled and why unsupported model output must be replaced in conversation state, not only hidden on screen.
6. Human support was kept explicit and browser-local for the public demo. A live external pilot would need authentication, tenant authorization, a shared helpdesk queue, approved content sources, retention controls, and authenticated Salesforce access.
7. Live testing found that a model could repeat historical evidence without a new tool call and invent a plausible guide URL. The first model step now requires a read-only tool, and server-side answer formatting removes unapproved URLs.

## Verification performed

- Eight deterministic Python tests pass: scoped lookup, cross-partner rejection, sensitive human routing, thread memory, exact-ID handling, simulated tool failure, bounded tool-loop recovery, and unapproved-link removal.
- TypeScript checks and production JavaScript builds pass with the artifact environment configured.
- Live Nebius calls exercised deal lookup and combined quote-plus-guide lookup with source citations.
- A follow-up after restarting the API recovered the previously discussed deal from PostgreSQL checkpoints and retrieved its owner through a fresh tool call.
- A live sensitive-pricing request returned a human-review route with zero model/tool calls.
- The Help page was visually checked; business success-rate targets remain unmeasured.

## Reproducible demo scenarios

- Northstar: “What is the status of DR-2841?” → In review, owner, next step, citation, and tool trace.
- Same conversation: “Who owns that deal?” → Uses remembered reference and retrieves the deal again.
- Northstar: “What is the status of Q-73108?” → Pricing review, without approving pricing.
- “How do I submit a deal registration?” → Approved demo guide and source citation.
- “Can you approve a special pricing discount?” → No model call; prepare a human support request.
- Switch to Meridian and request DR-2841 → No matching selected-partner evidence, not Northstar's record.
- Simulated tool exception in the Python tests → Labeled local fallback rather than an unsupported answer.

## Submission checklist

- Working code-track application with state, tool selection, bounded recovery, citations, and a human-controlled support workflow: implemented.
- Project overview, dataset description, prompts, iterations, learnings, framework, and architecture: this document.
- Five-minute-or-shorter live video: record using the accompanying demo script.
- Google Doc: import the generated DOCX into Google Docs and review the formatting.
- GitHub codebase: upload this repository without secrets, dependency directories, generated downloads, or private customer data.
- Submit the Google Doc, video, and GitHub links at https://forms.gle/waBYFkkf5xxmcouV9.

The recording, Google Doc creation, GitHub upload, publishing, and submission form are user-controlled steps; this documentation does not claim those actions have been completed.
