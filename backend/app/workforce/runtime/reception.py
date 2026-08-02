from typing import Any


class ReceptionExecutive:
    """
    Executes reception and customer-handling tasks.
    """

    name = "Reception"

    def execute(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "executive": self.name,
            "task_title": title,
            "status": "completed",
            "summary": (
                "Prepared a customer response and booking "
                "handling process."
            ),
            "response_process": [
                "Confirm the customer's interest.",
                "Collect the required booking information.",
                "Offer the earliest suitable appointment or service.",
                "Send confirmation and reminder details.",
            ],
            "sample_response": (
                "Thank you for getting back to us. We would be "
                "happy to assist you. Please share your preferred "
                "date and time so we can confirm your booking."
            ),
            "source_description": description,
            "input_data": input_data,
        }