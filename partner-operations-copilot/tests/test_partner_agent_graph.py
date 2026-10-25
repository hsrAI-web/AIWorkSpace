from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from partner_agent_graph.api import AgentRequest, _fallback_response
from partner_agent_graph.graph import _cite_sources, _finalize, build_graph
from partner_agent_graph.demo_data import find_local_fallback
from partner_agent_graph.tools import _match


class FakeModel:
    def __init__(self, responses: Iterable[AIMessage]):
        self.responses = list(responses)
        self.seen_messages: list[list[Any]] = []
        self.bind_options: list[dict[str, Any]] = []

    def bind_tools(self, _tools: list[Any], **options: Any) -> FakeModel:
        self.bind_options.append(options)
        return self

    def invoke(self, messages: list[Any]) -> AIMessage:
        self.seen_messages.append(messages)
        if not self.responses:
            raise AssertionError("The graph called the fake model more times than expected.")
        return self.responses.pop(0)


def tool_call(name: str, query: str, call_id: str) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": name,
                "args": {"query": query},
                "id": call_id,
                "type": "tool_call",
            }
        ],
    )


def invoke(graph: Any, question: str, partner_id: str, thread_id: str) -> dict[str, Any]:
    return graph.invoke(
        {
            "messages": [HumanMessage(content=question)],
            "partner_id": partner_id,
            "tool_rounds": 0,
            "tool_calls": [],
            "trace": [],
            "sources": [],
        },
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 12},
    )


def test_deal_lookup_uses_partner_scoped_tool_and_cites_record() -> None:
    model = FakeModel(
        [
            AIMessage(content="DR-2841 is in review; channel operations is validating the opportunity."),
        ]
    )
    graph = build_graph(model, InMemorySaver())

    result = invoke(graph, "What is the status of DR-2841?", "p-northstar", "p-northstar-test")

    assert result["mode"] == "ai"
    assert result["intent"] == "deal_status"
    assert "DR-2841" in result["answer"]
    assert result["sources"][0]["label"].endswith("DR-2841 · Northstar care navigation expansion")
    assert result["tool_calls"] == ["lookup_deal_status"]
    assert len(model.seen_messages) == 1
    assert any("Lookup planner" in step for step in result["trace"])
    assert {"tool_choice": "required"} in model.bind_options
    assert any("Safety gate" in step for step in result["trace"])
    assert any("Evidence check" in step for step in result["trace"])


def test_other_partner_cannot_receive_a_deal_from_northstar() -> None:
    model = FakeModel(
        [
            AIMessage(content="DR-2841 is in review."),
        ]
    )
    graph = build_graph(model, InMemorySaver())

    result = invoke(graph, "What is the status of DR-2841?", "p-meridian", "p-meridian-test")

    assert result["mode"] == "fallback"
    assert result["handoff_required"] is True
    assert result["sources"] == []
    assert "in review" not in result["answer"].lower()


def test_sensitive_pricing_question_routes_to_human_without_model_call() -> None:
    model = FakeModel([])
    graph = build_graph(model, InMemorySaver())

    result = invoke(
        graph,
        "Can you approve a special pricing discount?",
        "p-northstar",
        "p-northstar-safety-test",
    )

    assert result["intent"] == "human_review"
    assert result["handoff_required"] is True
    assert result["handoff_category"] == "Special pricing"
    assert model.seen_messages == []
    assert result["tool_calls"] == []
    assert "human review" in result["answer"].lower()


def test_unconnected_release_status_routes_to_human_without_model_call() -> None:
    model = FakeModel([])
    graph = build_graph(model, InMemorySaver())

    result = invoke(
        graph,
        "What is the release status of Q-73108?",
        "p-northstar",
        "p-northstar-release-scope-test",
    )

    assert result["intent"] == "human_review"
    assert result["handoff_category"] == "General"
    assert result["handoff_required"] is True
    assert model.seen_messages == []
    assert result["tool_calls"] == []
    assert "not connected" in result["answer"].lower()


def test_explicit_deal_and_quote_ids_are_planned_together() -> None:
    model = FakeModel(
        [
            AIMessage(content="DR-2841 is in review and Q-73108 is in pricing review."),
        ]
    )
    graph = build_graph(model, InMemorySaver())

    result = invoke(
        graph,
        "Compare DR-2841 and Q-73108 status.",
        "p-northstar",
        "p-northstar-multi-record-test",
    )

    assert result["mode"] == "ai"
    assert result["tool_calls"] == ["lookup_deal_status", "lookup_quote_status"]
    assert len(result["sources"]) == 2
    assert "DR-2841" in result["answer"] and "Q-73108" in result["answer"]
    assert len(model.seen_messages) == 1


def test_registration_question_without_id_uses_model_tool_selection() -> None:
    model = FakeModel(
        [
            tool_call("search_registration_guide", "registering a deal", "guide-call"),
            AIMessage(content="Submit the deal through the partner registration workflow."),
        ]
    )
    graph = build_graph(model, InMemorySaver())

    result = invoke(
        graph,
        "How do I register a deal?",
        "p-northstar",
        "p-northstar-guide-selection-test",
    )

    assert result["mode"] == "ai"
    assert result["tool_calls"] == ["search_registration_guide"]
    assert result["sources"]
    assert any("delegated source selection" in step for step in result["trace"])


def test_finalizer_withholds_a_partial_multi_record_answer() -> None:
    state = {
        "messages": [
            HumanMessage(content="What is the status of DR-2841 and Q-73108?"),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "lookup_deal_status",
                        "args": {"query": "DR-2841"},
                        "id": "partial-deal-call",
                        "type": "tool_call",
                    }
                ],
            ),
            ToolMessage(
                content=(
                    '{"ok":true,"found":true,"sources":[{"label":"Deal DR-2841 · Northstar",'
                    '"timestamp":"2026-10-25"}]}'
                ),
                tool_call_id="partial-deal-call",
                name="lookup_deal_status",
            ),
            AIMessage(content="DR-2841 is in review and Q-73108 is approved."),
        ],
        "partner_id": "p-northstar",
        "tool_calls": ["lookup_deal_status"],
        "trace": [],
    }

    result = _finalize(state)  # type: ignore[arg-type]

    assert result["handoff_required"] is True
    assert result["intent"] == "incomplete_evidence"
    assert "withheld the partial answer" in result["answer"]
    assert "approved" not in result["answer"].lower()
    assert "Q-73108" in result["answer"]
    assert len(result["sources"]) == 1


def test_offline_fallback_does_not_answer_release_status_from_a_quote_record() -> None:
    request = AgentRequest(
        question="What is the release status of Q-73108?",
        partnerId="p-northstar",
        threadId="p-northstar-offline-test",
    )

    result = _fallback_response(request, "Nebius is not configured.")

    assert result.handoff_required is True
    assert result.handoff_category == "General"
    assert result.sources == []
    assert "not connected" in result.answer.lower()


def test_postgres_style_thread_state_retains_prior_turns() -> None:
    model = FakeModel(
        [
            AIMessage(content="DR-2841 is in review."),
            AIMessage(content="Q-73108 is in pricing review."),
        ]
    )
    graph = build_graph(model, InMemorySaver())
    thread_id = "p-northstar-conversation-test"

    invoke(graph, "What is the status of DR-2841?", "p-northstar", thread_id)
    invoke(graph, "And what about Q-73108?", "p-northstar", thread_id)

    saved_state = graph.get_state({"configurable": {"thread_id": thread_id}})
    human_turns = [message for message in saved_state.values["messages"] if isinstance(message, HumanMessage)]
    assert len(human_turns) == 2
    assert "DR-2841" in str(human_turns[0].content)
    assert "Q-73108" in str(human_turns[1].content)


def test_explicit_unknown_id_does_not_fall_back_to_fuzzy_match() -> None:
    records = [{"id": "DR-2841", "title": "Northstar expansion in review"}]
    assert _match("DR-28411 Northstar expansion", records, ("title",)) is None
    assert _match("DR-9999 in review", records, ("title",)) is None
    assert find_local_fallback("p-northstar", "DR-28411") is None


def test_failed_tool_recovers_to_labeled_exact_match(monkeypatch: Any) -> None:
    def broken_lookup(_partner_id: str) -> list[Any]:
        raise RuntimeError("Simulated record service failure")

    monkeypatch.setattr("partner_agent_graph.tools.get_partner_deals", broken_lookup)
    model = FakeModel([
        AIMessage(content="An unsupported answer must not be shown."),
    ])
    graph = build_graph(model, InMemorySaver())
    result = invoke(graph, "Status of DR-2841?", "p-northstar", "p-northstar-failure-test")
    assert result["mode"] == "fallback"
    assert result["sources"]
    assert "unsupported answer" not in result["answer"]
    assert result["messages"][-1].content == result["answer"]


def test_repeated_tool_calls_stop_and_leave_valid_message_history() -> None:
    model = FakeModel([
        tool_call("lookup_deal_status", "DR-2841", f"repeat-{index}")
        for index in range(4)
    ])
    graph = build_graph(model, InMemorySaver())
    result = invoke(graph, "Status of DR-2841?", "p-northstar", "p-northstar-limit-test")
    assert result["mode"] == "fallback"
    assert len(result["tool_calls"]) == 3
    assert result["messages"][-2].tool_call_id == "repeat-2"
    assert result["messages"][-1].content == result["answer"]


def test_answer_cannot_display_unapproved_model_links() -> None:
    answer = _cite_sources(
        "Read [the guide](https://example.com/invented) or https://example.com/other. **Ready**",
        [{"label": "Local demo partner guide", "timestamp": "2026-10-25"}],
    )
    assert "https://" not in answer
    assert "example.com" not in answer
    assert "**" not in answer
    assert "Source: Local demo partner guide" in answer
