import asyncio

from app.services.llm import llm


async def main():

    response = await llm.generate(
        system_prompt="You are an SEO expert.",
        user_prompt="Write five SEO keywords for a pizza restaurant.",
    )

    print(response)


asyncio.run(main())