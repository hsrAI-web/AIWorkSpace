# Partner Operations Copilot — explained

> **Historical script — not the final demo.** This film predates the read-only Salesforce demo connection and the fourth public-knowledge tool. Its old source labels and narration describe that earlier build. For the current implementation, use `../../docs/partner-copilot-explainer/README.md` and `../partner-status-agent/docs/demo-script.md`. The retained film and audio have not been regenerated.

## Director's treatment

- **Promise:** I can show both audiences where a partner question travels, what the agent is allowed to use, and where the implementation stops.
- **Identity:** Partner Desk's existing deep teal, parchment, and restrained brass demo palette; Space Grotesk display, DM Sans support, JetBrains Mono system labels.
- **Hero:** A synthetic deal question moves through the actual application boundary, LangGraph, scoped evidence, and the human-owned support route.
- **Motion:** Diagram planes unfold into a single connected architecture; request lines trace through gates and tools; the map compresses into an implementation review card.
- **Arc:** Open with the architecture overview, expand its layers, follow a routine question, then close with implementation details and explicit limits.
- **Payoff:** The final frame is a crisp implementation map and limitation statement, not a product promise.
- **Format:** 16:9 landscape, 118 seconds.
- **Narrator:** First-person presenter script read by a neutral, locally synthesized English narrator. It is not a voice clone or imitation. Captions repeat the narration verbatim for silent viewing.

## Timeline

| Shot | Time | Focus | Mechanic / handoff |
|---|---:|---|---|
| 01 | 0–10s | Architecture at a glance; real Partner Desk screenshot | Opening diagram planes unfold around the actual UI; request token becomes browser-to-API packet |
| 02 | 10–28s | Browser, generated client, public API, internal service | One request crosses the public boundary; credential stays on the server side |
| 03 | 28–53s | LangGraph, model adapter, tools, synthetic data, checkpoints | Service layer folds into the graph; tool spokes return to the evidence node |
| 04 | 53–76s | Routine and sensitive request flow | Question branches at deterministic gate; direct-ID plan and bounded tool loop |
| 05 | 76–96s | Evidence, citations, fallback, human handoff | Source markers either close an answer loop or peel to support |
| 06 | 96–118s | Human write boundary, implementation recap, limits | Browser-local request card resolves into repository review map; question badge returns |

## Shot-by-shot script

Captions below are the exact spoken words, shown in a persistent, high-contrast caption rail. All other on-screen copy is also transcribed here. Speaker phrasing is first person, as the project presenter. Captions are not an abbreviated substitute for the narration.

### Shot 01 / 0.00–10.00s / 10.00s — “ARCHITECTURE FIRST.”

- **Purpose:** State the requested order and make clear this is an explanation of the present synthetic-data demo.
- **Exact content:** At 0.00s, `PARTNER OPERATIONS COPILOT`; `ARCHITECTURE → FLOW → TECHNICAL DETAILS`. At 0.40s, caption: “I’ll explain Partner Operations Copilot: architecture first, then the agent flow, then technical choices and limits. This demo uses synthetic data.” The left label reads `01 / SYSTEM MAP`; the screenshot is labeled `PARTNER DESK · SYNTHETIC EXAMPLE`. Hold the caption through 9.60s.
- **Composition:** Parchment full-bleed field. On the right, the existing `partner-home.jpg` screenshot sits inside a deep-teal cutout, large enough to recognize as the product. Three thin architecture planes cross the screenshot edge and meet at a brass `QUESTION` node. The left third owns the large title; lower fifth is reserved for the caption. Keep every label inside a 5% safe inset.
- **Artistic idea:** The screenshot is not a decorative mockup: its deal row becomes the data packet that enters the architecture diagram.
- **Timed choreography:** 0.00–0.25s: fully composed opening frame is already visible; no blank background or loading-like entrance. 0.25–1.2s: title masks open in two beats. 1.2–3.0s: screenshot aperture expands, then its `DR-2841` deal row receives a precise outline. 3.0–5.8s: three architecture planes unfold in depth, each attached to the visible question token. 5.8–8.7s: labels `BROWSER`, `PUBLIC API`, `INTERNAL RUNTIME` settle in reading order as a line joins them. 8.7–10.0s: token scales toward the first membrane, carrying the line into shot 02.
- **Transition contract:** The outlined request packet leaves the screenshot on the right edge; its size and position match the browser packet entering shot 02. The teal diagram plane rotates into a perspective system boundary.
- **Assets and technique:** Existing `public/images/partner-home.jpg`; SVG line and node geometry; local Google font imports already in `index.html`. No fabricated brand mark.
- **Sound intent:** Existing instrumental bed continues under the neutral synthesized narration. No SFX. Beat alignment is not claimed.

### Shot 02 / 10.00–28.00s / 18.00s — “THE PUBLIC EDGE.”

- **Purpose:** Explain the browser-to-public-API-to-internal-service architecture before discussing agent behavior.
- **Exact content:** Caption: “The browser is a React and TypeScript workspace built with Vite and Wouter. An Orval-generated React Query client follows OpenAPI. Public Express validates requests with Zod and in-memory demo caps, then proxies to internal FastAPI on loopback. The browser never calls Nebius; credentials stay server-side.” Layer labels: `01 BROWSER`, `02 PUBLIC API`, `03 INTERNAL SERVICE`. Stack labels: `React · TypeScript · Vite · Wouter`; `Orval · React Query · OpenAPI · Zod`; `Express · FastAPI · 127.0.0.1:8000`. Boundary stamp: `NEBIUS CREDENTIAL · SERVER-SIDE ONLY`. Hold caption through 27.60s.
- **Composition:** A dark teal oblique plane fills the frame. Three parchment surfaces sit at different depths, not in equal cards: browser lower-left, Express in the near center, FastAPI upper-right. The API boundary is a strong vertical brass membrane. Caption rail runs along the bottom on a solid parchment strip.
- **Artistic idea:** One physical packet changes outline at Express: a browser question becomes a validated API envelope, then crosses privately to FastAPI; the provider secret is drawn only inside the server plane.
- **Timed choreography:** 0.00–0.30s: the matching packet is visible immediately as the plane unfolds. 0.30–2.5s: browser surface resolves with React, TypeScript, Vite, and Wouter. 2.5–5.0s: OpenAPI contract and generated Orval/React Query path draw between browser and Express. 5.0–8.0s: Zod gate scans the envelope; in-memory demo cap is stamped beside the public edge. 8.0–11.5s: Express forwards to loopback FastAPI; the address appears as mono notation. 11.5–14.0s: a key icon appears inside the server plane only; browser route stops before the provider credential. 14.0–16.5s: packet advances through the private boundary and the camera turns toward the LangGraph plate. 16.5–18.0s: the graph plate expands to fill the frame, not a blank wipe.
- **Transition contract:** FastAPI plate enlarges into the outer LangGraph frame of shot 03. The request packet and brass route line remain visible across the cut.
- **Assets and technique:** CSS/HTML service planes, SVG packet path and validation membrane; no new external service implied.
- **Sound intent:** Instrumental continues; narration is primary. No unverified beat synchronization.

### Shot 03 / 28.00–53.00s / 25.00s — “THE RUNTIME AND ITS STATE.”

- **Purpose:** Complete the architecture diagram with orchestration, model adapter, tools, data, and persistence.
- **Exact content:** Caption: “FastAPI validates the demo partner and thread ID, then invokes LangGraph. The graph coordinates safety, planning, tools, evidence checks, and conversation checkpoints. LangChain adapts Nebius Token Factory’s Qwen3; PostgreSQL stores graph checkpoints. Three partner-scoped, read-only tools share synthetic JSON with the UI. Support requests stay separately in browser localStorage.” Diagram labels: `FASTAPI`; `LANGGRAPH`; `LANGCHAIN ADAPTER`; `NEBIUS TOKEN FACTORY · QWEN3`; `READ-ONLY TOOLS`; `SYNTHETIC JSON`; `POSTGRESQL CHECKPOINTS`; `BROWSER LOCALSTORAGE · SUPPORT ONLY`. Hold caption through 52.60s.
- **Composition:** Deep teal field, open at a large LangGraph node in the center. Three staggered read-only tool apertures sit on the right; synthetic JSON data sits below them. PostgreSQL is shown as a separate checkpoint line under the graph, not as the source of demo records. A small localStorage box sits outside the server region to make the support-request boundary distinct.
- **Artistic idea:** Separate two kinds of state: graph checkpoints travel to PostgreSQL, while support cards remain on the browser side. The model node is a connected inference service, never a data store.
- **Timed choreography:** 0.00–1.5s: FastAPI plate becomes the LangGraph frame. 1.5–4.0s: safety gate and planner occupy graph nodes; connecting edges draw in order. 4.0–7.5s: LangChain adapter plate turns toward the Nebius Qwen3 node. 7.5–12.0s: three read-only tools open sequentially—deal status, quote status, registration guide. 12.0–15.5s: their source lines converge on the shared synthetic JSON data plane; the same-data relationship to the UI is drawn. 15.5–19.0s: PostgreSQL checkpoint route appears beneath the graph, linked to conversation state. 19.0–21.0s: browser-local support request box appears outside the server region. 21.0–23.2s: camera pulls back to show all architecture layers and their separations. 23.2–25.0s: a question token moves toward the safety gate, motivating the flow explanation.
- **Transition contract:** The question token enters the safety gate at the same center point where shot 04 opens. Architecture nodes fold down to the gate, not to a generic title card.
- **Assets and technique:** SVG graph nodes and routes; CSS data and database plates. Labels distinguish checkpoint persistence from synthetic data and local support.
- **Sound intent:** Music bed continues at reduced level under narration. No generated SFX.

### Shot 04 / 53.00–76.00s / 23.00s — “THE QUESTION TAKES A PATH.”

- **Purpose:** Explain deterministic gates, exact-ID planning, agent-selected tools, and the bounded tool loop.
- **Exact content:** Caption: “Now follow a question. A deterministic gate sends pricing, credit, eligibility, and approval questions to human review without a model call; unsupported data, like renewals, also routes to support. Exact deal or quote IDs go directly to their scoped lookup through a planner. Otherwise, the agent selects a read-only tool. Results return to the agent for at most three tool rounds.” Visible gate labels: `SENSITIVE?`, `UNSUPPORTED SOURCE?`, `ROUTINE`. Human branch: `NO MODEL CALL`. Routine branch: `EXACT ID → DIRECT PLANNER` or `AGENT SELECTS TOOL`. Tool names: `lookup_deal_status`, `lookup_quote_status`, `search_registration_guide`. Round marker: `MAX 3 TOOL ROUNDS`. Hold caption through 75.60s.
- **Composition:** A close, centered diamond gate dominates the opening. Amber exits down-left to human support; the routine route arcs right through three staggered read-only apertures and returns to the agent. Caption owns a separate parchment strip below the diagram.
- **Artistic idea:** The same question is physically sorted before any model node appears. Exact IDs skip model tool selection and are planned straight to their scoped lookup.
- **Timed choreography:** 0.00–1.4s: token meets the gate; `SENSITIVE?` engraves. 1.4–4.5s: amber branch opens, labeled for pricing, credit, eligibility, approval, and no model call. 4.5–6.5s: unsupported-source gate opens beside it, with renewal as the concrete example. 6.5–9.5s: routine path lights; exact-ID planner catches a `DR-2841` packet. 9.5–13.0s: ID is routed directly to the deal lookup aperture; the quote lookup aperture answers the same path for `Q-73108`. 13.0–17.5s: a question without an exact ID crosses the LangChain agent node and selects a tool. 17.5–20.5s: tool results return to the agent; three round pips fill and stop. 20.5–23.0s: partner scope is pinned to every tool route; returned source dots lead into shot 05.
- **Transition contract:** The returned source dots retain their positions and become citation markers in shot 05. Amber human route remains at frame left.
- **Assets and technique:** SVG branch paths, deterministic tool windows, typed labels and bounded round pips. No dynamic or fabricated model response.
- **Sound intent:** Instrumental continues; no SFX and no beat-sync claim.

### Shot 05 / 76.00–96.00s / 20.00s — “EVIDENCE BEFORE ANSWER.”

- **Purpose:** Explain current-turn source coverage, visible citations and trace, fallback, and withheld partial answers.
- **Exact content:** Caption: “Before display, the graph checks citations for requested IDs, expected tools for obvious question types, and uncited IDs in the draft. The interface shows sources, timestamps, and a trace. This is source coverage, not a full semantic fact-check. Missing evidence withholds partial answers; fallback is used only when it covers the whole request.” Visible labels: `REQUESTED ID`, `EXPECTED SOURCE`, `UNCITED ID BLOCKED`, `SOURCES + TIMESTAMPS + TRACE`, `COVERAGE CHECK ≠ SEMANTIC FACT-CHECK`, `MISSING EVIDENCE → WITHHOLD / SUPPORT`. The existing help screenshot is labeled `INITIAL SCREEN CAPTURE · NOT A LIVE ANSWER`. Hold caption through 95.60s.
- **Composition:** Parchment field, actual `partner-help.jpg` capture occupies left 58%, with a source-check rail on the right. Three markers stamp over diagram callouts beside—but not as claims inside—the empty initial-state screenshot. A lower source rail changes into two distinct exits: grounded answer or withheld/fallback.
- **Artistic idea:** Citation markers press onto the source rail, not into a fabricated chat answer. Removing one makes the answer lane visibly close.
- **Timed choreography:** 0.00–1.5s: three source dots match into outlined citation rings. 1.5–4.0s: real initial help screenshot reveals through a split aperture; its empty answer field stays empty. 4.0–7.0s: requested ID, expected source, and uncited-ID checks stamp sequentially. 7.0–10.5s: source labels and timestamps join the visible execution trace. 10.5–13.0s: a missing marker removes the answer lane; partial answer text is explicitly withheld. 13.0–16.0s: exact-match fallback appears only with complete source coverage; a second path offers human support. 16.0–18.0s: qualification appears: this is not a complete semantic fact-check. 18.0–20.0s: amber path travels to the human-owned request card in shot 06.
- **Transition contract:** Amber evidence-gap branch folds into the browser-local support card. A vertical split opens the two distinct state boundaries in shot 06.
- **Assets and technique:** Existing `partner-help.jpg`; existing `quotes.jpg` may appear only as a brief initial-state strip; SVG source stamps. No simulated answer is added to either capture.
- **Sound intent:** Music bed remains secondary. Narration carries the explanation; beat alignment is unverified.

### Shot 06 / 96.00–118.00s / 22.00s — “HUMAN WRITE. TECHNICAL LIMITS.”

- **Purpose:** Explain the explicit human submission, local queue, technical safeguards, and current project limitations without promising future capabilities.
- **Exact content:** Caption: “For sensitive topics, partners review and explicitly save support requests. Staff can assign and respond in the same browser; requests do not sync across devices. Tools are read-only and scoped, but Salesforce is not connected, there are no CRM writes, and demo-role switching is not secure authentication. This is a demo, not a production portal.” Visible labels: `REVIEW → EXPLICIT SAVE`; `BROWSER localStorage`; `SAME BROWSER ONLY`; `READ-ONLY · PARTNER-SCOPED`; `SALESFORCE NOT CONNECTED`; `NO CRM WRITES`; `DEMO ROLE ≠ SECURE AUTHENTICATION`; `CURRENT IMPLEMENTATION`. Repository tabs: `src/partner_agent_graph/graph.py`, `src/partner_agent_graph/tools.py`, `src/partner_agent_graph/api.py`, `docs/partner-copilot-explainer/README.md`. Hold all final copy through 21.50s.
- **Composition:** Asymmetric split: parchment browser space occupies the left; deep teal server/review space occupies the right, with a visible gap between local support storage and any shared service. Final 7 seconds pull out to a compact repository index, on a light field distinct from earlier diagram shots. Caption rail remains legible in the lower fifth.
- **Artistic idea:** The support request only crosses into localStorage after an explicit save; it lands inside the browser outline, while the separate-device outline remains disconnected. The technical summary resolves into the files a reviewer can inspect.
- **Timed choreography:** 0.00–2.5s: amber line from the prior shot becomes a draft support card. 2.5–5.0s: `REVIEW → EXPLICIT SAVE` appears; only after that stamp does the card move into browser localStorage. 5.0–8.0s: a second device outline appears across a physical gap, labeled same browser only. 8.0–11.0s: read-only and partner-scoped tool labels return as compact implementation facts. 11.0–14.5s: Salesforce, CRM writes, and demo-role authentication limits stamp in sequence. 14.5–17.0s: camera pulls out; the architecture lines become repository paths. 17.0–20.0s: four source tabs settle in a review map; `CURRENT IMPLEMENTATION` holds. 20.0–22.0s: `DR-2841` returns in the opening position while the screenshot aperture begins to close, ready for a clean loop.
- **Transition contract:** Final request badge matches the opener's visible `DR-2841` token in position, scale, and angle. An actual screenshot aperture and teal plane match the opener; no empty dark frame is exposed.
- **Assets and technique:** CSS browser/device outlines, SVG human path and file tabs, and the listed existing screenshots. No new service or logo is implied.
- **Sound intent:** Existing instrumental bed resolves and loops with the image. Neutral synthesized narration finishes before the final loop match; no SFX or beat alignment is claimed.

## Audio spec

- **Runtime:** 118 s, equal to the six-scene duration sum.
- **Narration:** First-person English script above, generated locally with the neutral `slt` English synthetic voice; not cloned or imitative. Speech is lightly time-compressed for the 118-second cut. No TTS service call was available in this run.
- **Music:** Preserve the existing `public/audio/bg_music.mp3` instrumental. Extend it by looping the compatible existing bed under the full runtime; keep it quieter than speech. No new music or sound effects.
- **Captioning:** Each scene's exact narration is displayed in a high-contrast, persistent caption rail so the film remains understandable without sound.
- **Beat alignment:** Not claimed; no reliable onset analysis was completed.
