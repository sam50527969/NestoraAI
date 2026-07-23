import asyncio

from app.core.executives import ExecutiveContext
from app.core.workforce import workforce_registry
from app.executives.marketing.director import MarketingDirector
from app.workers.loader import worker_loader


async def main() -> None:
    workforce_registry.clear()
    loaded_workers = worker_loader.load()

    print("Loaded workers:", loaded_workers)
    print()

    director = MarketingDirector()

    result = await director.run(
        ExecutiveContext(
            mission=(
                "Create a Facebook campaign for "
                "a restaurant in Doha"
            ),
        )
    )

    print()
    print("=" * 60)
    print("MARKETING DIRECTOR RESULT")
    print("=" * 60)
    print("Success:", result.success)
    print("Summary:", result.summary)
    print("Data:", result.data)

    print()
    print("Recommendations:")

    for recommendation in result.recommendations:
        print("-", recommendation)


if __name__ == "__main__":
    asyncio.run(main())