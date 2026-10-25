# Week 3 Project: Partner Operations Copilot

## Project overview

Partner Operations Copilot helps partners answer routine deal-registration and quote-status questions without repeatedly contacting an account representative. Internal staff can review exceptions, assign ownership, and record a response in the demo support queue.

This is a bring-your-own-use-case submission using the Python LangChain + LangGraph code track. It adapts the status-agent idea to partner operations; it does not claim to implement all six suggested projects or the Jira sprint-reporting project.

## Agent one-liner

My agent helps channel partners check Salesforce-backed demo registrations, synthetic quote examples, and partner guidance in Partner Desk, replacing searches across CRM, portals, and email plus repeated rep follow-ups; it routes questions through four read-only tools, grounds answers in record or public-reference evidence, hands sensitive or unsupported company-specific questions to a human, and targets eight of ten routine tasks completed in under two minutes.

The success rate and completion-time target have not been measured with real users. Automated functional checks are not evidence of business impact.

## Agent framework

### Agent goal
Answer routine partner operations questions with source evidence and a practical next step; route exceptions to a human without making commercial decisions.

### Where people use it
The browser application offers switchable Partner and Staff demo views. The role switch is not authentication or an authorization boundary.

### Steps, in order
1. The API validates the request and, for Red Valley or Bluewater, reads only the fixed demo registrations from the allowlisted Salesforce Developer Edition org.
2. The Python service validates the selected partner/thread pair; LangGraph runs safety and source-scope gates.
3. Exact record IDs go to their scoped lookup. For other routine questions, the Nebius model selects a LangChain tool in the LangGraph loop.
4. Tools return a Salesforce registration, local synthetic quote, registration guide, or relevant public-reference excerpt.
5. The graph checks for expected record/source evidence, then returns a cited answer and visible execution trace.
6. Sensitive or unsupported questions use the human path. A partner reviews and explicitly saves a browser-local request; staff manually update that demo request.

### Actions and tools
- READ: `lookup_deal_status` retrieves a partner-scoped Salesforce demo registration for Red Valley/Bluewater, or a local synthetic registration for another demo partner.
- READ: `lookup_quote_status` searches local synthetic quote examples. Native Salesforce Quotes are not enabled in the connected org.
- READ: `search_registration_guide` searches the local deal-registration guide.
- READ: `search_partner_knowledge` uses Nebius Qwen3 embeddings to find relevant excerpts in five curated public references and returns source links.
- HUMAN WRITE: Save a browser-local support request after reviewing the form.
- HUMAN WRITE: Assign ownership, update request status, and record a staff response.

The LLM has no write tool and cannot create a request, send a message, or modify Salesforce.

### Memory and state
LangGraph stores conversation messages and graph checkpoints in PostgreSQL, keyed by a partner-prefixed thread ID. The browser keeps that ID per selected partner, so subsequent questions can refer to earlier records even after an API restart; a New conversation button starts a fresh thread.

The model receives a bounded recent-message window. Old checkpoint history remains in the database until explicitly cleaned up; there is no automatic retention/deletion policy in this demo. Support requests, staff updates, and view preferences are stored only in this browser, not shared across devices.

### Hard limits
Use only the fixed demo-only Salesforce records and local synthetic examples; never use production partner/customer data. Never represent the role selector as secure access control, infer another partner's record from a failed ID match, approve discounts or eligibility, clear credit holds, write CRM data, or send external messages.

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
→ Express validation / demo limits / Salesforce connector
→ allowlisted read-only Salesforce Developer Edition query for the selected demo partner
→ loopback FastAPI service
→ LangGraph safety gate
→ deterministic ID routing or Nebius agent ↔ four scoped read-only tools
→ Salesforce registrations / local synthetic quotes and guide / cited public knowledge
→ evidence check or human handoff
→ answer, source citations, and run trace.

PostgreSQL holds graph checkpoints. Browser storage holds the local support queue. The FastAPI service listens on loopback and is not separately exposed as a public service. The AI never creates the Salesforce connection: the Connected App/API integration is conventional read-only data access; AI interprets questions, selects tools, and summarizes retrieved evidence.

## Datasets used

The local JSON dataset supplies synthetic records for the UI and Python tools: four partner organizations, six deal registrations, five quote examples, and one registration guide. The file is `artifacts/partner-status-agent/src/demo-records.json`. Red Valley and Bluewater registration lookups instead use three fixed demo records in the connected Salesforce Developer Edition org; only the selected partner's rows are passed to the agent.

Dates on local examples are generated for demonstration. Salesforce registration timestamps come from the connected demo org. These are development-org sample records, not production customer/partner data; native Salesforce Quotes are not enabled.

Public knowledge comes from five curated snapshots in `src/partner_agent_graph/knowledge-base.json`: CISA, NIST, Channeltivity, Training Industry, and PartnerStack. Nebius embeddings rank relevant excerpts; publisher links and review timestamps accompany the answer. These are public industry references, not company policy, internal assets, product claims, or live web search.

## AI provider and credits

The answer/tool-selection model is `Qwen/Qwen3-30B-A3B-Instruct-2507` through Nebius Token Factory's OpenAI-compatible endpoint, invoked with LangChain ChatOpenAI. Public knowledge retrieval also uses `Qwen/Qwen3-Embedding-8B`: five curated documents are embedded and cached in process, and each knowledge query is embedded for semantic ranking. The Nebius key is configured server-side and never sent to the browser. Salesforce uses the separate managed Connected App/API integration; it is not an AI connection.

Routine questions generally need a tool-selection call plus an answer call, with a bounded allowance for more tools or a retry. Sensitive questions use the deterministic safety gate and need no model call.

Illustrative chat-only budget: at example rates of $0.10 per million input tokens and $0.30 per million output tokens, three calls at 3,000 input and 600 output tokens each cost about $0.00144 per question, or $0.144 per 100 questions. This excludes embedding calls and hosting; each knowledge query uses an embedding request, and the five document vectors are generated once per API process when the cache initializes. Actual costs depend on provider pricing, token counts, retries, and model availability.

LangChain and LangGraph do not require token-credit accounts. Tavily, Mem0, and LangSmith are not required or used in this version; there is no additional credential to supply for this demo.

## Prompts used during AI-assisted development

1. Initial brief: build an agent that helps partners with status updates, code status, release status, and potentially broader capabilities.
2. Product clarification: partners need help with deal registration, quote status, product positioning, renewals, eligibility, enablement assets, and complex issue routing; information is spread across portals, CRM, and email.
3. Selected scope: deal registration and quote status first, switchable Partner / Staff demo views, and public demo content; later, an isolated Salesforce Developer Edition was added for allowlisted sample registrations.
4. Selected implementation: Python LangChain + LangGraph, Nebius tool calling and embeddings, Salesforce read-only tool data, persistent graph state, citations, safe failures, and human-controlled writes.

The runtime system prompt is maintained in `src/partner_agent_graph/graph.py`. It instructs the model to call tools for current facts, use conversation history only to resolve references, cite sources, refuse unsupported claims, and never make pricing/credit/eligibility decisions or external writes.

AI coding assistance was used to build the UI, define the API contract, implement the Python graph and tools, write tests, and prepare documentation. Outputs were checked with TypeScript checks, deterministic Python tests, live API requests, and a visual preview.

## Iterations and learnings

1. A broad status dashboard was narrowed to the user's highest-value first workflow: partner deal and quote support.
2. A one-shot model endpoint was replaced with a real agent/tool loop and PostgreSQL checkpointer. This separates the model's tool selection from the deterministic safety and evidence boundaries.
3. A shared synthetic dataset replaced separate UI and backend examples to avoid contradictory statuses.
4. Partner scope is injected by the tool runner rather than supplied by the model; explicit unknown IDs cannot fall through to fuzzy matching.
5. A simulated tool failure showed why a fallback must be labeled and why unsupported model output must be replaced in conversation state, not only hidden on screen.
6. Human support was kept explicit and browser-local for the public demo. A live pilot would need partner authentication, tenant authorization, a shared helpdesk queue, approved content sources, retention controls, and a separately approved production Salesforce scope.
7. Live testing found that a model could repeat historical evidence without a new tool call and invent a plausible guide URL. The first model step now requires a read-only tool, and server-side answer formatting removes unapproved URLs.
8. Public release-note content was replaced with practical co-sell guidance. Semantic retrieval now answers general partner questions from cited public snapshots while company-specific policy and internal assets remain human-routed.

## Verification performed

- 27 deterministic Python tests pass, covering graph behavior, partner scoping, safety routing, evidence checks, and public-knowledge retrieval.
- TypeScript checks and production JavaScript builds pass with the artifact environment configured.
- A live Nebius knowledge request answered the co-sell prompt and returned a PartnerStack source citation.
- The current preview displayed Salesforce-sourced Red Valley registrations and clearly labeled the workspace demo-only.
- A live sensitive-pricing request returned a human-review route with zero model/tool calls.
- The updated Help, home, and quote screens were visually captured; business success-rate and time targets remain unmeasured.

## Reproducible demo scenarios

- Red Valley: ask for the status of a registration ID visible on the home page → Salesforce demo source, status, next step, and tool trace.
- Same conversation: ask for the next step on that registration → Uses thread context and retrieves current source evidence again.
- “What should a co-sell partner know before starting an opportunity?” → Semantic public-reference search and source citation.
- “What information should I include when registering a deal?” → Local registration guide and source citation.
- Switch to Northstar and ask “What is the status of Q-73108?” → Local synthetic quote status; no pricing decision.
- “Can you approve a special pricing discount?” → No model call; prepare a human support request.
- Switch partners and request another partner's registration ID → No cross-partner record is returned.
- Simulated tool exception in the Python tests → Labeled local fallback rather than an unsupported answer.

## Submission checklist

- Working code-track application with state, tool selection, bounded recovery, citations, and a human-controlled support workflow: implemented.
- Project overview, dataset description, prompts, iterations, learnings, framework, and architecture: this document.
- Five-minute-or-shorter live video: record using the accompanying demo script.
- Google Doc: import the generated DOCX into Google Docs and review the formatting.
- GitHub codebase: upload this repository without secrets, dependency directories, generated downloads, or private customer data.
- Submit the Google Doc, video, and GitHub links at https://forms.gle/waBYFkkf5xxmcouV9.

The recording, Google Doc creation, GitHub upload, publishing, and submission form are user-controlled steps; this documentation does not claim those actions have been completed.
