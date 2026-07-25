from __future__ import annotations

import asyncio

from dotenv import load_dotenv

# The environment must be loaded before importing modules
# that create the configured LLM provider.
load_dotenv()

from app.core.executives.context import ExecutiveContext
from app.executives.followup.executive import FollowupExecutive
from app.services.llm import llm


async def main() -> None:
    print(f"ACTIVE LLM PROVIDER: {type(llm).__name__}")

    executive = FollowupExecutive()

    context = ExecutiveContext(
        mission="Recommend the best follow-up action for this clinic lead.",
        objective="Convert the enquiry into a booked consultation.",
        business_name="Demo Dental Clinic",
        metadata={
            "lead_name": "Ahmed Khan",
            "service": "Dental Implant",
            "current_status": "New",
            "source": "WhatsApp",
            "days_since_last_contact": 0,
            "notes": "Requested an evening appointment.",
        },
    )

    result = await executive.run(context)

    print("\nSUCCESS:")
    print(result.success)

    print("\nSUMMARY:")
    print(result.summary)

    print("\nAI RESPONSE:")
    print(result.data.get("response"))

    print("\nRECOMMENDATIONS:")
    for recommendation in result.recommendations:
        print("-", recommendation)


if __name__ == "__main__":
    asyncio.run(main())