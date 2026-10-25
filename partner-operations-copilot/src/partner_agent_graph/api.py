from __future__ import annotations

import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Any, Literal

os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")

from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.errors import GraphRecursionError
from pydantic import BaseModel, ConfigDict, Field

from partner_agent_graph.demo_data import find_local_fallback, get_partner, is_salesforce_partner
from partner_agent_graph.graph import (
    _handoff_message,
    _sensitive_category,
    _unsupported_data_category,
    build_graph,
    create_model,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("partner_agent_graph")
PARTNER_ID_PATTERN = re.compile(r"^p-[a-z0-9-]+$")


class AgentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    question: str = Field(min_length=1, max_length=1000)
    partner_id: str = Field(alias="partnerId", min_length=3, max_length=64)
    thread_id: str = Field(alias="threadId", min_length=8, max_length=120)
    salesforce_deals: list[dict[str, Any]] | None = Field(default=None, alias="salesforceDeals", max_length=50)


class Source(BaseModel):
    label: str
    timestamp: str
    url: str | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    answer: str
    mode: Literal["ai", "fallback"]
    provider: str
    thread_id: str = Field(alias="threadId")
    intent: str
    handoff_required: bool = Field(alias="handoffRequired")
    handoff_category: str = Field(alias="handoffCategory")
    sources: list[Source]
    trace: list[str]
    tool_calls: list[str] = Field(alias="toolCalls")


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for persistent LangGraph checkpoints.")
    async with AsyncPostgresSaver.from_conn_string(database_url) as checkpointer:
        app.state.agent_graph = build_graph(create_model(), checkpointer)
        yield


app = FastAPI(
    title="Partner Operations Agent Graph",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "agent": "langgraph"}


def _fallback_response(request: AgentRequest, reason: str) -> AgentResponse:
    category = _sensitive_category(request.question) or _unsupported_data_category(request.question)
    if category:
        return AgentResponse(
            answer=_handoff_message(category),
            mode="fallback",
            provider="Local demo safety route",
            threadId=request.thread_id,
            intent="human_review",
            handoffRequired=True,
            handoffCategory=category,
            sources=[],
            trace=[
                "Safety or scope gate: routed to human review without using an unsupported source.",
                reason,
            ],
            toolCalls=[],
        )
    match = find_local_fallback(request.partner_id, request.question, request.salesforce_deals)
    if match:
        return AgentResponse(
            answer=match["answer"],
            mode="fallback",
            provider="Salesforce exact-match fallback" if is_salesforce_partner(request.partner_id) else "Local demo exact-match fallback",
            threadId=request.thread_id,
            intent=match["intent"],
            handoffRequired=False,
            handoffCategory="",
            sources=match["sources"],
            trace=["Recovery: returned an exact-match answer from the current partner-scoped source.", reason],
            toolCalls=[],
        )
    return AgentResponse(
        answer="I couldn't verify this from the selected partner's demo records. Please check the ID or use the support form for a human review.",
        mode="fallback",
        provider="Local demo fallback",
        threadId=request.thread_id,
        intent="unknown",
        handoffRequired=True,
        handoffCategory="General",
        sources=[],
        trace=["Recovery: no grounded local answer was available.", reason],
        toolCalls=[],
    )


@app.post("/agent/run", response_model=AgentResponse, response_model_exclude_none=True)
async def run_agent(request: AgentRequest) -> AgentResponse:
    if not PARTNER_ID_PATTERN.fullmatch(request.partner_id) or not get_partner(request.partner_id):
        raise HTTPException(status_code=422, detail="Unknown demo partner.")
    if not request.thread_id.startswith(f"{request.partner_id}-"):
        raise HTTPException(status_code=422, detail="Thread ID must be scoped to the selected demo partner.")
    if any(record.get("partnerId") != request.partner_id for record in (request.salesforce_deals or [])):
        raise HTTPException(status_code=422, detail="Salesforce records must be scoped to the selected demo partner.")

    if not os.getenv("NEBIUS_API_KEY"):
        return _fallback_response(request, "Nebius is not configured.")

    try:
        result = await app.state.agent_graph.ainvoke(
            {
                "messages": [HumanMessage(content=request.question.strip())],
                "partner_id": request.partner_id,
                "salesforce_deals": request.salesforce_deals,
                "tool_rounds": 0,
                "tool_calls": [],
                "trace": [],
                "sources": [],
            },
            config={
                "configurable": {"thread_id": request.thread_id},
                "recursion_limit": 12,
            },
        )
        return AgentResponse(
            answer=result.get("answer", "The agent did not return an answer."),
            mode=result.get("mode", "fallback"),
            provider=(
                "Nebius Token Factory"
                if result.get("mode") == "ai"
                else "Local demo agent"
            ),
            threadId=request.thread_id,
            intent=result.get("intent", "unknown"),
            handoffRequired=bool(result.get("handoff_required", False)),
            handoffCategory=result.get("handoff_category", ""),
            sources=result.get("sources", []),
            trace=result.get("trace", []),
            toolCalls=result.get("tool_calls", []),
        )
    except GraphRecursionError:
        logger.exception("Partner agent exceeded its graph step limit")
        return _fallback_response(request, "The graph reached its safe step limit.")
    except Exception:
        logger.exception("Partner agent graph execution failed")
        return _fallback_response(request, "The agent or provider was unavailable.")
