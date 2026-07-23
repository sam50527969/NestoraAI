from app.executives.ceo import (
    CEOBrain,
    CompanyState,
    DepartmentState,
)


def main():
    # Simulated company state
    state = CompanyState()

    state.crm = DepartmentState(
        department="CRM",
        status="warning",
        health_score=35,
        summary="Lead pipeline is shrinking.",
        risks=[
            "Only 12 active leads remain."
        ],
        opportunities=[
            "Import 250 new restaurant leads."
        ],
    )

    state.marketing = DepartmentState(
        department="Marketing",
        status="healthy",
        health_score=82,
        summary="Campaign performance improving.",
        opportunities=[
            "Launch new restaurant campaign."
        ],
    )

    state.critical_risks.append(
        "Sales pipeline may run dry within two weeks."
    )

    state.major_opportunities.append(
        "Expand into dental clinic market."
    )

    # Calculate overall company health
    state.calculate_overall_health()

    # Run CEO Brain
    ceo = CEOBrain()

    plan = ceo.evaluate(
        company_state=state,
        objective="Increase monthly revenue",
    )

    print("=" * 60)
    print("NESTORA CEO BRAIN")
    print("=" * 60)

    print(f"\nOverall Health: {state.overall_health_score}")

    print("\nExecutive Summary")
    print("-----------------")
    print(plan.summary)

    print("\nTop Recommendations")
    print("-------------------")

    for recommendation in plan.recommendations:
        print(
            f"[{recommendation.calculate_final_score():5.2f}] "
            f"{recommendation.department} | "
            f"{recommendation.title}"
        )

    print("\nExecutive Actions")
    print("-----------------")

    for action in plan.actions:
        print(
            f"→ {action.department}: {action.title}"
        )


if __name__ == "__main__":
    main()