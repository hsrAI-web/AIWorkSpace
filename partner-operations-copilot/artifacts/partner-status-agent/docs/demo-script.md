# Week 3 demo script — under five minutes

## 0:00–0:35 — Problem and scope
“Partners wait for routine answers because status and process information are fragmented and depend on individual representatives. I built Partner Operations Copilot for deal registration and quote progress, with a staff handoff for exceptions. This public demo uses synthetic data; it is not connected to Salesforce.”

## 0:35–1:30 — Live tool use
Open Partner Help with Northstar selected. Ask “What is the status of DR-2841?” Show the answer, source timestamp, and expanded Agent run trace. Explain that the model chooses a read-only LangChain tool inside LangGraph, rather than receiving all records in one prompt.

## 1:30–2:10 — Memory and second tool
Ask “Who owns that deal?” Explain that the thread ID connects to PostgreSQL-backed graph state, while the agent retrieves status again rather than trusting old facts. Then ask “What is the status of Q-73108?” and show the quote tool.

## 2:10–2:40 — Workflow guidance
Ask “How do I submit a deal registration?” Show the guide citation and practical steps.

## 2:40–3:35 — Human boundary
Ask “Can you approve a special pricing discount?” Show the safety route with zero tool calls. Click Prepare support request, review the text, then explicitly Save support request. Switch to Staff view, open Support requests, and assign or update the request. Explain that the queue is browser-local and no message or CRM change is sent.

## 3:35–4:15 — Failure and scope
Switch partner to Meridian and ask for DR-2841. Explain that injected partner scope prevents the Northstar record from being returned. Show the tool-failure test and labeled fallback path; do not pretend that the recorded demonstration disconnected a real CRM.

## 4:15–4:55 — Build and learning
Show the graph code, three tools, checkpoint setup, and tests. “I used AI coding assistance for the interface, contract, graph, tests, and documentation. The key lesson was to separate model decisions from safety, evidence, and human writes. Real Salesforce access, secure roles, and a shared support queue are future pilot requirements.”

Before sharing: hide account/billing pages, never open Secrets, use a fresh conversation, keep the recording under five minutes, and describe the 8/10 metric as a target rather than a measured result.
