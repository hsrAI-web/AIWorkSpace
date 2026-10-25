import { Router, type IRouter } from "express";
import {
  AnswerPartnerQuestionBody,
  AnswerPartnerQuestionResponse,
} from "@workspace/api-zod";
import { getSalesforceDemoData, isSalesforceDemoPartner } from "../lib/salesforce-demo";

const router: IRouter = Router();
const GRAPH_URL = process.env.PARTNER_AGENT_GRAPH_URL || "http://127.0.0.1:8000";
const PER_IP_WINDOW_MS = 60 * 60 * 1000;
const PER_IP_LIMIT = 10;
const GLOBAL_DAILY_LIMIT = 100;

const ipWindows = new Map<string, { startedAt: number; count: number }>();
let globalDay = new Date().toISOString().slice(0, 10);
let globalDayCount = 0;

router.get("/partner-agent/salesforce-data", async (req, res): Promise<void> => {
  res.setHeader("Cache-Control", "no-store");
  try {
    res.json(await getSalesforceDemoData());
  } catch {
    req.log.warn({ code: "SALESFORCE_DEMO_LOOKUP_FAILED" }, "Salesforce demo lookup unavailable");
    res.status(502).json({ error: "Salesforce demo records are unavailable. No local records have been substituted." });
  }
});

function isWithinDemoLimit(ip: string, now: number): boolean {
  const today = new Date(now).toISOString().slice(0, 10);
  if (today !== globalDay) {
    globalDay = today;
    globalDayCount = 0;
  }
  if (globalDayCount >= GLOBAL_DAILY_LIMIT) return false;

  const window = ipWindows.get(ip);
  if (!window || now - window.startedAt >= PER_IP_WINDOW_MS) {
    ipWindows.set(ip, { startedAt: now, count: 1 });
  } else if (window.count >= PER_IP_LIMIT) {
    return false;
  } else {
    window.count += 1;
  }

  globalDayCount += 1;
  return true;
}

router.post("/partner-agent/answer", async (req, res): Promise<void> => {
  const parsed = AnswerPartnerQuestionBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "Please provide a question, demo partner, and thread ID." });
    return;
  }

  if (!isWithinDemoLimit(req.ip || "unknown", Date.now())) {
    res.status(429).json({ error: "The demo assistant has reached its usage limit. Please try again later." });
    return;
  }

  try {
    const salesforceDeals = isSalesforceDemoPartner(parsed.data.partnerId)
      ? (await getSalesforceDemoData(true)).registrations.filter(record => record.partnerId === parsed.data.partnerId)
      : undefined;
    const graphResponse = await fetch(`${GRAPH_URL}/agent/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...parsed.data, salesforceDeals }),
      signal: AbortSignal.timeout(50_000),
    });

    if (!graphResponse.ok) {
      req.log.error(
        { statusCode: graphResponse.status },
        "Partner LangGraph service returned an error",
      );
      res.status(graphResponse.status === 422 ? 422 : 502).json({
        error: "The partner agent could not complete this request. Please retry or use the support form.",
      });
      return;
    }

    const response = AnswerPartnerQuestionResponse.parse(await graphResponse.json());
    res.json(response);
  } catch {
    req.log.error({ code: "PARTNER_AGENT_UNAVAILABLE" }, "Partner agent or required source is unavailable");
    res.status(502).json({
      error: "The partner agent service is unavailable. Please retry or use the support form.",
    });
  }
});

export default router;
