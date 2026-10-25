from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "partner_agent_graph.api:app",
        host="127.0.0.1",
        port=int(os.getenv("PARTNER_AGENT_PORT", "8000")),
        log_level="info",
    )
