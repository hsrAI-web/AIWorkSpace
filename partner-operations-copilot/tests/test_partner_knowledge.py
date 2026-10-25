from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

import partner_agent_graph.knowledge as knowledge
import partner_agent_graph.tools as agent_tools
from partner_agent_graph.graph import _required_tools, _safety_gate, build_graph


class FakeEmbeddings:
    def embed_query(self, _query: str) -> list[float]:
        return [1.0, 0.0]


def test_semantic_search_returns_only_relevant_sources(monkeypatch: Any) -> None:
    first = {
        "id": "nist",
        "title": "NIST guide",
        "publisher": "NIST",
        "url": "https://www.nist.gov/example",
        "publishedAt": "2024-02-26",
        "reviewedAt": "2026-10-26",
        "content": "Risk management guidance.",
    }
    second = {
        **first,
        "id": "changelog",
        "title": "Partner enablement",
        "publisher": "Training Industry",
        "url": "https://trainingindustry.com/articles/learning-services-and-outsourcing/partner-enablement-using-training-for-channel-success/",
    }
    monkeypatch.setattr(knowledge, "_embeddings", lambda: FakeEmbeddings())
    monkeypatch.setattr(
        knowledge,
        "_document_vectors",
        lambda: ((first, (1.0, 0.0)), (second, (0.0, 1.0))),
    )
    monkeypatch.setattr(knowledge, "SIMILARITY_THRESHOLD", 0.8)

    result = knowledge.search_public_knowledge("SMB cybersecurity risk management")

    assert result["ok"] is True
    assert result["found"] is True
    assert [item["title"] for item in result["documents"]] == ["NIST guide"]
    assert result["sources"][0]["url"] == "https://www.nist.gov/example"
    assert "not the company's policy" in result["disclaimer"]


def test_semantic_search_withholds_low_similarity_matches(monkeypatch: Any) -> None:
    document = {
        "id": "doc",
        "title": "Reference",
        "publisher": "Example",
        "url": "https://example.org/",
        "publishedAt": None,
        "reviewedAt": "2026-10-26",
        "content": "Reference content.",
    }
    monkeypatch.setattr(knowledge, "_embeddings", lambda: FakeEmbeddings())
    monkeypatch.setattr(knowledge, "_document_vectors", lambda: ((document, (0.0, 1.0)),))
    monkeypatch.setattr(knowledge, "SIMILARITY_THRESHOLD", 0.8)

    result = knowledge.search_public_knowledge("unrelated query")

    assert result["ok"] is True
    assert result["found"] is False
    assert result["sources"] == []


def test_semantic_search_fails_closed_when_embedding_service_is_unavailable(monkeypatch: Any) -> None:
    def unavailable() -> tuple[()]:
        raise RuntimeError("embedding endpoint unavailable")

    monkeypatch.setattr(knowledge, "_document_vectors", unavailable)

    result = knowledge.search_public_knowledge("partner enablement")

    assert result["ok"] is False
    assert result["found"] is False
    assert result["sources"] == []
    assert "Do not answer from model memory" in result["message"]


def test_partner_knowledge_tool_returns_vetted_public_source(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        agent_tools,
        "search_public_knowledge",
        lambda _query: {
            "ok": True,
            "found": True,
            "documents": [{"title": "A public guide", "content": "A short paraphrase."}],
            "sources": [{
                "label": "Public reference · NIST · A public guide",
                "timestamp": "2026-10-26",
                "url": "https://www.nist.gov/example",
            }],
        },
    )

    result = json.loads(agent_tools.search_partner_knowledge.invoke({
        "query": "How do I start?",
        "partner_id": "p-red-valley",
    }))

    assert result["kind"] == "public_knowledge"
    assert result["sources"][0]["url"] == "https://www.nist.gov/example"


def test_public_knowledge_answers_require_the_semantic_search_tool() -> None:
    assert "search_partner_knowledge" in _required_tools(
        "What should SMB buyers consider about product security?"
    )
    assert "search_partner_knowledge" in _required_tools(
        "What does partner enablement typically include?"
    )
    assert "search_partner_knowledge" in _required_tools(
        "What should a co-sell partner know before starting an opportunity?"
    )
    assert _required_tools("What should a deal registration policy clarify?") == {"search_partner_knowledge"}
    assert _required_tools("What does the NIST guide say?") == {"search_partner_knowledge"}
    assert _required_tools("What information should I include when registering a deal?") == {
        "search_registration_guide"
    }


def test_safety_gate_allows_bounded_public_guidance_but_not_internal_assets_or_release_status() -> None:
    def gate(question: str) -> dict[str, object]:
        return _safety_gate({"messages": [HumanMessage(content=question)]})

    security = gate("What should SMB buyers consider about product security?")
    enablement = gate("What does partner enablement typically include?")
    release_notes = gate("How should I structure release notes?")
    internal_assets = gate("Where can I find approved training assets?")
    release_status = gate("What is the current product release status?")
    mixed_assets = gate("Find our pitch deck and explain NIST.")
    mixed_count = gate("How should I structure release notes and how many deals do we have?")

    assert security["handoff_required"] is False
    assert enablement["handoff_required"] is False
    assert internal_assets["handoff_required"] is True
    assert release_status["handoff_required"] is True
    assert release_notes["handoff_required"] is True
    assert mixed_assets["handoff_required"] is True
    assert mixed_count["handoff_required"] is True


def test_public_knowledge_graph_answers_with_clickable_source_metadata(monkeypatch: Any) -> None:
    source_url = "https://www.nist.gov/publications/nist-cybersecurity-framework-20-small-business-quick-start-guide"
    monkeypatch.setattr(
        agent_tools,
        "search_public_knowledge",
        lambda _query: {
            "ok": True,
            "found": True,
            "disclaimer": "Public guidance only.",
            "documents": [{
                "title": "NIST Cybersecurity Framework 2.0: Small Business Quick-Start Guide",
                "publisher": "NIST",
                "content": "It helps smaller organizations begin cybersecurity risk management using CSF 2.0.",
            }],
            "sources": [{
                "label": "Public reference · NIST · Small Business Quick-Start Guide",
                "timestamp": "2026-10-26",
                "url": source_url,
            }],
        },
    )

    class KnowledgeModel:
        def __init__(self) -> None:
            self.responses = [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "search_partner_knowledge",
                        "args": {"query": "SMB buyers product security"},
                        "id": "knowledge-call",
                        "type": "tool_call",
                    }],
                ),
                AIMessage(
                    content="NIST SP 1300 can help a small organization start risk management with CSF 2.0. It is general guidance, not product approval."
                )
            ]

        def bind_tools(self, _tools: list[Any], **_options: Any) -> KnowledgeModel:
            return self

        def invoke(self, _messages: list[Any]) -> AIMessage:
            if self.responses:
                return self.responses.pop(0)
            raise AssertionError("The graph should use the required knowledge tool before answering.")

    model = KnowledgeModel()
    graph = build_graph(model, InMemorySaver())
    result = graph.invoke(
        {
            "messages": [HumanMessage(content="What should SMB buyers consider about product security?")],
            "partner_id": "p-red-valley",
            "tool_rounds": 0,
            "tool_calls": [],
            "trace": [],
            "sources": [],
        },
        config={"configurable": {"thread_id": "public-knowledge-test"}, "recursion_limit": 12},
    )

    assert result["intent"] == "public_knowledge"
    assert result["tool_calls"] == ["search_partner_knowledge"]
    assert result["handoff_required"] is False
    assert result["sources"][0]["url"] == source_url
    assert "Source: Public reference · NIST" in result["answer"]
