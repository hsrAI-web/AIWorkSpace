from __future__ import annotations

import json
import re
from typing import Annotated, Any

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from partner_agent_graph.demo_data import (
    get_guides,
    get_partner_deals,
    get_partner_quotes,
    get_lookup_deals,
    is_salesforce_partner,
)


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _match(query: str, records: list[dict[str, Any]], searchable_fields: tuple[str, ...]) -> dict[str, Any] | None:
    normalized_query = _normalized(query)
    if not normalized_query:
        return None

    requested_ids = set(re.findall(r"\b(?:DR-\d+|Q-\d+)\b", query, flags=re.I))
    if requested_ids:
        normalized_ids = {record_id.upper() for record_id in requested_ids}
        return next((record for record in records if record["id"].upper() in normalized_ids), None)

    query_tokens = {
        token for token in normalized_query.split() if len(token) >= 4
    }
    scored = []
    for record in records:
        text = " ".join(str(record.get(field, "")) for field in searchable_fields)
        record_tokens = set(_normalized(text).split())
        score = len(query_tokens & record_tokens)
        if score:
            scored.append((score, record))
    if not scored:
        return None

    scored.sort(key=lambda item: item[0], reverse=True)
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    return scored[0][1]


def _serialize(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


@tool
def lookup_deal_status(
    query: str,
    partner_id: Annotated[str, InjectedState("partner_id")],
    state: Annotated[dict[str, Any] | None, InjectedState] = None,
) -> str:
    """Read registration status and the distinct Opportunity stage for the selected partner."""
    records = (
        get_lookup_deals(partner_id, (state or {}).get("salesforce_deals"))
        if is_salesforce_partner(partner_id)
        else get_partner_deals(partner_id)
    )
    deal = _match(query, records, ("title", "status", "nextStep"))
    if not deal:
        return _serialize(
            {
                "ok": True,
                "found": False,
                "kind": "deal",
                "message": "No matching registration was verified in the selected partner's current source.",
                "sources": [],
            }
        )
    return _serialize(
        {
            "ok": True,
            "found": True,
            "kind": "deal",
            "record": {
                "id": deal["id"],
                "title": deal["title"],
                "status": deal["status"],
                "submittedAt": deal["submittedAt"],
                "expectedClose": deal["expectedClose"],
                "owner": deal["owner"],
                "nextStep": deal["nextStep"],
                **({"opportunityStage": deal["opportunityStage"]} if "opportunityStage" in deal else {}),
            },
            "sources": [
                {
                    "label": f'{deal["sourceLabel"]} · {deal["id"]} · {deal["title"]}',
                    "timestamp": deal.get("lastModifiedAt", deal["submittedAt"]),
                }
            ],
        }
    )


@tool
def lookup_quote_status(
    query: str,
    partner_id: Annotated[str, InjectedState("partner_id")],
) -> str:
    """Look up a quote by quote ID or product for the selected demo partner."""
    if is_salesforce_partner(partner_id):
        return _serialize({
            "ok": True, "found": False, "kind": "quote",
            "message": "Native Salesforce Quotes are not enabled or configured in this test org. No live quote status is available.",
            "sources": [],
        })
    records = get_partner_quotes(partner_id)
    quote = _match(query, records, ("product", "status", "nextStep"))
    if not quote:
        return _serialize(
            {
                "ok": True,
                "found": False,
                "kind": "quote",
                "message": "No matching quote exists in the selected partner's demo records.",
                "sources": [],
            }
        )
    return _serialize(
        {
            "ok": True,
            "found": True,
            "kind": "quote",
            "record": {
                "id": quote["id"],
                "product": quote["product"],
                "status": quote["status"],
                "requestedAt": quote["requestedAt"],
                "lastUpdatedAt": quote["lastUpdatedAt"],
                "owner": quote["owner"],
                "nextStep": quote["nextStep"],
            },
            "sources": [
                {
                    "label": f'{quote["sourceLabel"]} · {quote["id"]} · {quote["product"]}',
                    "timestamp": quote["lastUpdatedAt"],
                }
            ],
        }
    )


@tool
def search_registration_guide(
    query: str,
    partner_id: Annotated[str, InjectedState("partner_id")],
) -> str:
    """Search the approved local demo guide for deal-registration steps and requirements."""
    _ = partner_id  # The injected value keeps all tools scoped to a selected demo partner.
    guide = next(
        (
            article
            for article in get_guides()
            if "registration" in query.lower()
            or "register" in query.lower()
            or "guide" in query.lower()
            or "submit" in query.lower()
            or article["title"].lower() in query.lower()
        ),
        None,
    )
    if not guide:
        return _serialize(
            {
                "ok": True,
                "found": False,
                "kind": "guide",
                "message": "No approved guide matches this question in the demo library.",
                "sources": [],
            }
        )
    return _serialize(
        {
            "ok": True,
            "found": True,
            "kind": "guide",
            "record": {
                "title": guide["title"],
                "summary": guide["summary"],
                "steps": guide["steps"],
            },
            "sources": [
                {
                    "label": f'{guide["sourceLabel"]} · {guide["title"]}',
                    "timestamp": guide["updatedAt"],
                }
            ],
        }
    )


TOOLS = [lookup_deal_status, lookup_quote_status, search_registration_guide]
TOOL_NAMES = {tool.name for tool in TOOLS}
