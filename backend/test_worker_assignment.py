import asyncio

from app.core.workforce import (
    assignment_engine,
    workforce_registry,
)
from app.workers.loader import worker_loader


async def main() -> None:
    workforce_registry.clear()

    loaded = worker_loader.load()

    print("Loaded workers:", loaded)

    selected_worker = (
        workforce_registry.find_by_capability(
            "copywriting"
        )
    )

    print(
        "Selected worker:",
        selected_worker.worker_id,
    )

    result = await assignment_engine.assign(
        capability="copywriting",
        title="Restaurant Facebook campaign",
        description=(
            "Create promotional content for "
            "a restaurant in Doha."
        ),
        payload={
            "business_type": "restaurant",
            "location": "Doha",
            "platform": "Facebook",
        },
        metadata={
            "requested_by": "marketing_director",
        },
    )

    print()
    print("=" * 60)
    print("WORKER RESULT")
    print("=" * 60)
    print("Success:", result.success)
    print("Summary:", result.summary)
    print("Output:", result.output)


if __name__ == "__main__":
    asyncio.run(main())