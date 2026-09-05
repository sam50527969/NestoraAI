from __future__ import annotations

import json
from typing import Any

from app.ai.finance_schema import FinanceReport
from app.workforce.runtime.base import BaseExecutive


class FinanceExecutive(BaseExecutive):
    """
    AI-powered Finance Executive.

    Reviews financial performance, budget allocation, cash flow,
    profitability, ROI and financial risk.
    """

    name = "Finance"

    response_model = FinanceReport

    @property
    def system_instruction(self) -> str:
        return (
            "You are Nestora's senior Finance Executive. "
            "Review the supplied business and mission data carefully. "
            "Provide practical financial analysis covering revenue, expenses, "
            "profitability, budget allocation, cash flow, ROI and financial "
            "risk. Never invent financial figures that were not supplied or "
            "clearly derived from supplied figures."
        )

    def build_prompt(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
    ) -> str:
        return f"""
You are the Finance Executive for Nestora.

TASK

{title}

DESCRIPTION

{description or "No description supplied."}

BUSINESS AND MISSION DATA

{json.dumps(input_data, indent=2, ensure_ascii=False)}

Create a professional Finance execution report.

Your report must include:

1. Executive summary

2. Financial assessment
   Review only financial information actually available.

3. Budget recommendations

4. Revenue opportunities

5. Cost controls

6. Cash-flow actions

7. Recommended actions
   Each action should contain:
   - Title
   - Description
   - Priority
   - Expected impact

8. KPIs
   Each KPI should contain:
   - Name
   - Target
   - Measurement

9. Financial risks

Important rules:

- Do not invent revenue, expense, profit, budget, ROI or cash-flow figures.
- Use the supplied currency when financial values are available.
- If important financial data is missing, state what should be measured
  rather than fabricating a value.
- Distinguish observed financial data from recommendations.
- Use previous executive outputs and experience_reasoning when relevant.

Return only the structured professional business report.
"""

    def fallback_output(
        self,
        *,
        title: str,
        description: str | None,
        input_data: dict[str, Any],
        error_message: str,
    ) -> dict[str, Any]:
        currency = self._clean_currency(
            input_data.get("currency")
        )

        monthly_revenue = self._as_number(
            input_data.get("monthly_revenue")
        )
        monthly_expenses = self._as_number(
            input_data.get("monthly_expenses")
        )
        marketing_budget = self._as_number(
            input_data.get("marketing_budget")
        )
        receivables = self._as_number(
            input_data.get("outstanding_receivables")
        )

        monthly_profit = None

        if (
            monthly_revenue is not None
            and monthly_expenses is not None
        ):
            monthly_profit = (
                monthly_revenue - monthly_expenses
            )

        observed = []

        if monthly_revenue is not None:
            observed.append(
                f"Monthly revenue: "
                f"{self._format_money(monthly_revenue, currency)}."
            )

        if monthly_expenses is not None:
            observed.append(
                f"Monthly expenses: "
                f"{self._format_money(monthly_expenses, currency)}."
            )

        if monthly_profit is not None:
            observed.append(
                f"Estimated monthly profit: "
                f"{self._format_money(monthly_profit, currency)}."
            )

        if marketing_budget is not None:
            observed.append(
                f"Marketing budget: "
                f"{self._format_money(marketing_budget, currency)}."
            )

        if receivables is not None:
            observed.append(
                f"Outstanding receivables: "
                f"{self._format_money(receivables, currency)}."
            )

        if observed:
            financial_assessment = " ".join(observed)
        else:
            financial_assessment = (
                "No verified revenue, expense, budget or receivables "
                "figures were supplied. Establish a financial baseline "
                "before making quantified decisions."
            )

        risks = []

        if monthly_profit is not None and monthly_profit < 0:
            risks.append(
                "Current supplied revenue and expense figures indicate "
                "negative monthly profitability."
            )

        if (
            receivables is not None
            and monthly_revenue is not None
            and monthly_revenue > 0
            and receivables > monthly_revenue
        ):
            risks.append(
                "Outstanding receivables exceed one month of supplied "
                "revenue and may create cash-flow pressure."
            )

        if not risks:
            risks.append(
                "Financial decisions may be unreliable if revenue, cost "
                "or cash-flow data is incomplete."
            )

        return {
            "executive": self.name,
            "task_title": title,
            "status": "completed",
            "executive_summary": (
                "Prepared a finance review using only verified values "
                "available in the mission context."
            ),
            "financial_assessment": financial_assessment,
            "budget_recommendations": [
                "Set spending limits using verified revenue and margin data.",
                "Review budget performance against measurable business outcomes.",
            ],
            "revenue_opportunities": [
                "Track revenue by customer segment, service or product.",
                "Prioritize opportunities with measurable contribution margin.",
            ],
            "cost_controls": [
                "Review recurring costs and identify avoidable expenditure.",
                "Compare planned spending with actual results each month.",
            ],
            "cash_flow_actions": [
                "Track receivables and expected collection dates.",
                "Maintain visibility of upcoming operating commitments.",
            ],
            "recommended_actions": [
                {
                    "title": "Establish financial baseline",
                    "description": (
                        "Maintain current revenue, expense, receivables "
                        "and budget figures for executive analysis."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "More reliable financial decisions and forecasting."
                    ),
                },
                {
                    "title": "Review profitability",
                    "description": (
                        "Compare revenue with operating expenses and "
                        "investigate material changes."
                    ),
                    "priority": "high",
                    "expected_impact": (
                        "Earlier detection of margin and cost problems."
                    ),
                },
            ],
            "kpis": [
                {
                    "name": "Monthly profit",
                    "target": "Positive and improving",
                    "measurement": (
                        "Monthly revenue minus monthly expenses"
                    ),
                },
                {
                    "name": "Outstanding receivables",
                    "target": "Reduce overdue balances",
                    "measurement": (
                        "Total unpaid customer balances"
                    ),
                },
            ],
            "risks": risks,
            "source_description": description,
            "input_data": input_data,
            "ai_provider": "Fallback",
            "ai_error": error_message,
        }

    @staticmethod
    def _clean_currency(value: Any) -> str:
        if value is None:
            return ""

        return str(value).strip().upper()

    @staticmethod
    def _as_number(value: Any) -> float | None:
        if value is None or isinstance(value, bool):
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_money(
        value: float,
        currency: str,
    ) -> str:
        amount = f"{value:,.2f}"

        if currency:
            return f"{currency} {amount}"

        return amount
