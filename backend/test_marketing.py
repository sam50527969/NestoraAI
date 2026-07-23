import asyncio

from app.executives.marketing import MarketingDirector
from app.core.executives import ExecutiveContext


async def main():
    director = MarketingDirector()

    result = await director.run(
        ExecutiveContext(
            mission="Increase restaurant sales",
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

    for recommendation in result.recommendations:
        print("-", recommendation)


asyncio.run(main())