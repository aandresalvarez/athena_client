#!/usr/bin/env python3
"""Example demonstrating concept set generation."""

import asyncio

from athena_client import Athena


async def main() -> None:
    client = Athena()
    result = await client.generate_concept_set(
        "hypertension",
        db_connection_string="postgresql://user:pass@localhost/omop",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
