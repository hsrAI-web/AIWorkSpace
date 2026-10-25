# Week 3 demo script — under five minutes

## 0:00–0:30 — Problem and scope
“Partners wait for routine answers because status and process information are fragmented and depend on individual representatives. I built Partner Operations Copilot to answer registration questions, find general partner guidance, and route sensitive cases to a person. This public demo reads a small, allowlisted set of sample registrations from a Salesforce Developer Edition org; it does not use production partner data.”

## 0:30–1:20 — Salesforce-backed tool use
Open Partner Help with Red Valley selected. Ask “What is the status of DR-0001?” Show the Salesforce source label, timestamp, and expanded Agent run trace. Explain that a standard Connected App/API integration retrieves the allowlisted record; LangGraph scopes it to the selected demo partner, and the model summarizes the returned evidence. The AI does not create the Salesforce connection or write to CRM.

## 1:20–2:00 — Cited partner knowledge
Click “What should a co-sell partner know before starting an opportunity?” Explain that Nebius embeddings retrieve relevant passages from a curated public-reference snapshot, then the model summarizes them with a source link. This is general public guidance—not company policy, approved internal assets, or live release information.

## 2:00–2:30 — Registration guidance
Ask “What information should I include when registering a deal?” Show the local registration guide. Distinguish the guide from a company-approved policy or an actual Salesforce registration submission.

## 2:30–3:00 — Quote-data boundary
Switch to a synthetic partner and ask “What is the status of Q-73108?” if that sample record is present. Explain that quote examples are local synthetic data; native Salesforce Quotes are not enabled in the connected org.

## 3:00–3:50 — Human boundary
Ask “Can you approve a special pricing discount?” Show the safety route with no model or CRM write. Prepare the support request, review it, and explicitly save it. Switch to Staff demo and update the local request. Explain that this queue is browser-local and no message or Salesforce change is sent.

## 3:50–4:20 — Scope and safety
Switch to another partner and request the Red Valley sample registration. Explain that the graph injects the selected partner scope and does not return the other partner's record. Point out that the role switch is a demo control, not secure authentication.

## 4:20–4:55 — Architecture and learning
Show the four read-only tools, LangGraph safety/evidence flow, PostgreSQL checkpoints, Nebius chat and embedding models, and the Salesforce connector boundary. “The AI interprets the question, chooses a tool, and summarizes grounded evidence. The Salesforce connection itself is standard API integration. Pricing, credit, eligibility, approvals, CRM writes, and internal assets remain human-controlled or out of scope.”

Before sharing: hide account/billing pages, never open Secrets, use a fresh conversation, keep the recording under five minutes, and describe the 8/10 completion figure as a target rather than a measured result.
