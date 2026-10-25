from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "artifacts"
    / "partner-status-agent"
    / "src"
    / "demo-records.json"
)


def load_demo_data() -> dict[str, Any]:
    with DATA_PATH.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def timestamp_days_ago(days: int) -> str:
    return (datetime.now(UTC) - timedelta(days=days)).isoformat()


def date_days_from_now(days: int) -> str:
    return (datetime.now(UTC) + timedelta(days=days)).date().isoformat()


def get_partner(partner_id: str) -> dict[str, Any] | None:
    return next(
        (partner for partner in load_demo_data()["partners"] if partner["id"] == partner_id),
        None,
    )


def is_salesforce_partner(partner_id: str) -> bool:
    return (get_partner(partner_id) or {}).get("dataSource") == "salesforce"


def get_lookup_deals(
    partner_id: str, salesforce_deals: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if is_salesforce_partner(partner_id):
        # A missing/unavailable CRM source must never become a local demo answer.
        return [record for record in (salesforce_deals or []) if record.get("partnerId") == partner_id]
    return get_partner_deals(partner_id)


def get_partner_deals(partner_id: str) -> list[dict[str, Any]]:
    data = load_demo_data()
    return [
        {
            **deal,
            "submittedAt": timestamp_days_ago(deal["submittedDaysAgo"]),
            "expectedClose": date_days_from_now(deal["expectedCloseDaysFromNow"]),
        }
        for deal in data["deals"]
        if deal["partnerId"] == partner_id
    ]


def get_partner_quotes(partner_id: str) -> list[dict[str, Any]]:
    data = load_demo_data()
    return [
        {
            **quote,
            "requestedAt": timestamp_days_ago(quote["requestedDaysAgo"]),
            "lastUpdatedAt": timestamp_days_ago(quote["lastUpdatedDaysAgo"]),
        }
        for quote in data["quotes"]
        if quote["partnerId"] == partner_id
    ]


def get_guides() -> list[dict[str, Any]]:
    data = load_demo_data()
    return [
        {
            **article,
            "updatedAt": timestamp_days_ago(article["updatedDaysAgo"]),
        }
        for article in data["articles"]
    ]


def find_local_fallback(
    partner_id: str, question: str, salesforce_deals: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """Return an exact-match answer from the selected partner's current source."""
    requested_ids = {value.upper() for value in re.findall(r"\b(?:DR-\d+|Q-\d+)\b", question, re.I)}

    for deal in get_lookup_deals(partner_id, salesforce_deals):
        if deal["id"] in requested_ids:
            live = is_salesforce_partner(partner_id)
            stage = f' Linked Opportunity stage: "{deal["opportunityStage"]}".' if live else ""
            return {
                "answer": (
                    f'{deal["title"]} ({deal["id"]}) is recorded as '
                    f'"{deal["status"]}" in this {"Salesforce demo registration" if live else "local demo record"}.'
                    f'{stage} '
                    f'{deal["nextStep"]}'
                ),
                "intent": "deal_status",
                "sources": [
                    {
                        "label": f'{deal["sourceLabel"]} · {deal["id"]} · {deal["title"]}',
                        "timestamp": deal.get("lastModifiedAt", deal["submittedAt"]),
                    }
                ],
            }

    for quote in get_partner_quotes(partner_id):
        if quote["id"] in requested_ids:
            return {
                "answer": (
                    f'{quote["product"]} ({quote["id"]}) is recorded as '
                    f'"{quote["status"]}" in this local demo record. '
                    f'{quote["nextStep"]}'
                ),
                "intent": "quote_status",
                "sources": [
                    {
                        "label": f'{quote["sourceLabel"]} · {quote["id"]} · {quote["product"]}',
                        "timestamp": quote["lastUpdatedAt"],
                    }
                ],
            }

    return None
