import asyncio

from app.core.executives import (
    ExecutiveContext,
)
from app.executives.marketing import (
    MarketingDirector,
)


async def main() -> None:
    director = MarketingDirector()

    result = await director.run(
        ExecutiveContext(
            mission=(
                "Increase restaurant sales"
            ),
        )
    )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(result.summary)

    print()
    print("=" * 60)
    print("DATA")
    print("=" * 60)
    print(result.data)

    print()
    print("=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    for recommendation in (
        result.recommendations
    ):
        print(
            "-",
            recommendation,
        )


if __name__ == "__main__":
    asyncio.run(main())