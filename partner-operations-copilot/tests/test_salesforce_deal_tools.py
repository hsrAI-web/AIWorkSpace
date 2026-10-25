import json
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from partner_agent_graph.demo_data import find_local_fallback
from partner_agent_graph.graph import build_graph, _safety_gate
from partner_agent_graph.tools import lookup_deal_status, lookup_quote_status


def registration(partner_id="p-red-valley"):
    return {
        "id": "DR-0001", "partnerId": partner_id,
        "title": "DEMO ONLY - Managed Network Rollout",
        "status": "In Review", "opportunityStage": "Qualify",
        "submittedAt": "2026-10-20T10:00:00Z", "expectedClose": "2026-11-24",
        "lastModifiedAt": "2026-10-25T11:12:18Z",
        "owner": "Hidden in public demo", "nextStep": "Validate demo account details.",
        "sourceLabel": "Salesforce · Deal_Registration__c · demo-only record",
    }


def test_salesforce_status_and_stage_are_distinct():
    record = registration()
    result = json.loads(lookup_deal_status.invoke({
        "query": "Status of DR-0001",
        "partner_id": "p-red-valley",
        "state": {"salesforce_deals": [record]},
    }))
    assert result["found"]
    assert result["record"]["status"] == "In Review"
    assert result["record"]["opportunityStage"] == "Qualify"
    assert result["sources"][0]["timestamp"] == record["lastModifiedAt"]
    assert "Salesforce" in result["sources"][0]["label"]


def test_salesforce_lookup_never_returns_another_partners_record():
    result = json.loads(lookup_deal_status.invoke({
        "query": "DR-0001",
        "partner_id": "p-bluewater",
        "state": {"salesforce_deals": [registration()]},
    }))
    assert not result["found"]
    assert result["sources"] == []


def test_missing_salesforce_source_never_substitutes_local_data():
    result = json.loads(lookup_deal_status.invoke({
        "query": "DR-2841", "partner_id": "p-red-valley",
    }))
    assert not result["found"]
    assert find_local_fallback("p-red-valley", "DR-2841") is None


def test_salesforce_exact_match_fallback_is_grounded_and_scoped():
    match = find_local_fallback("p-red-valley", "Status of DR-0001", [registration()])
    assert match
    assert "Salesforce demo registration" in match["answer"]
    assert '"In Review"' in match["answer"]
    assert 'Opportunity stage: "Qualify"' in match["answer"]
    assert find_local_fallback("p-bluewater", "Status of DR-0001", [registration()]) is None


def test_unavailable_native_quotes_are_not_opportunity_statuses():
    result = json.loads(lookup_quote_status.invoke({
        "query": "Q-73108", "partner_id": "p-red-valley",
    }))
    assert not result["found"]
    assert result["sources"] == []
    assert "Native Salesforce Quotes" in result["message"]


def test_graph_uses_fresh_salesforce_snapshot_on_each_turn():
    class SnapshotModel:
        def bind_tools(self, _tools, **_kwargs):
            return self

        def invoke(self, messages):
            tool = next(message for message in reversed(messages) if isinstance(message, ToolMessage))
            record = json.loads(tool.content)["record"]
            return AIMessage(content=f'{record["id"]} registration status is {record["status"]}. Opportunity stage is {record["opportunityStage"]}.')

    graph = build_graph(SnapshotModel(), InMemorySaver())
    config = {"configurable": {"thread_id": "p-red-valley-freshness"}, "recursion_limit": 12}
    record = registration()
    for status in ["In Review", "Submitted"]:
        current = {**record, "status": status}
        result = graph.invoke({
            "messages": [HumanMessage(content="What is the status of DR-0001?")],
            "partner_id": "p-red-valley", "salesforce_deals": [current],
            "tool_rounds": 0, "tool_calls": [], "trace": [], "sources": [],
        }, config=config)
        assert status in result["answer"]
        assert "Qualify" in result["answer"]
        assert result["tool_calls"] == ["lookup_deal_status"]
        assert "Salesforce" in result["sources"][0]["label"]


def test_known_renewal_deal_status_does_not_enable_renewal_policy_advice():
    record = {**registration(), "title": "DEMO ONLY - Secure Access Renewal"}
    state = {"partner_id": "p-red-valley", "salesforce_deals": [record]}
    status = _safety_gate({
        **state, "messages": [HumanMessage(content="What is the registration status of Secure Access Renewal?")],
    })
    assert not status["handoff_required"]
    policy = _safety_gate({
        **state, "messages": [HumanMessage(content="What is the renewal policy for Secure Access Renewal?")],
    })
    assert policy["handoff_required"]
