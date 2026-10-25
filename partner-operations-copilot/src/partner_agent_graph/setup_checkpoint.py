from __future__ import annotations

import asyncio
import os

os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


async def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to set up LangGraph checkpoint tables.")
    async with AsyncPostgresSaver.from_conn_string(database_url) as checkpointer:
        await checkpointer.setup()
    print("LangGraph checkpoint tables are ready in the development database.")


if __name__ == "__main__":
    asyncio.run(main())
