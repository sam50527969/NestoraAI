"""Create a synthetic local-only buyer demo without sending external messages."""
import os
from pathlib import Path


def seed_demo():
    if os.getenv("APP_ENV", "development").lower() != "development":
        raise RuntimeError("Demo seeding is allowed only in development.")

    url = os.getenv("DATABASE_URL", "")
    if not url.startswith("sqlite:///") or url == "sqlite:///:memory:":
        raise RuntimeError("Provide a dedicated local SQLite DATABASE_URL.")

    path = Path(url.removeprefix("sqlite:///"))
    if path.exists():
        raise RuntimeError(
            "Use a new demo database path; existing data is never overwritten."
        )

    if os.getenv("EMAIL_PROVIDER", "disabled") != "disabled":
        raise RuntimeError("Disable email delivery for this demo.")

    if os.getenv("LLM_PROVIDER", "mock") != "mock":
        raise RuntimeError("Use the mock provider for an offline demo.")

    password = os.getenv("NESTORA_DEMO_PASSWORD", "")
    if len(password) < 12:
        raise RuntimeError(
            "Set NESTORA_DEMO_PASSWORD to a private test password of at least 12 characters."
        )

    from prepare_production_database import prepare_database

    prepare_database()

    from app.auth.schemas import UserRegister
    from app.auth.service import create_user
    from app.database.database import SessionLocal
    from app.database.models import (
        AgentTask,
        Business,
        Lead,
        Mission,
    )
    from app.services.business_membership_service import create_membership

    with SessionLocal() as db:
        user = create_user(
            db,
            UserRegister(
                email="buyer-demo@nestora.test",
                full_name="Synthetic Buyer Demo",
                password=password,
            ),
        )

        workspaces = []

        for name in ("Demo Design Studio", "Demo Consulting Office"):
            business = Business(
                name=name,
                industry="other",
                country="Qatar",
                city="Doha",
                description=(
                    "Synthetic demonstration. No real clients or revenue."
                ),
                currency="USD",
            )

            db.add(business)
            db.flush()

            uid = business.business_uid

            create_membership(
                db,
                user_uid=user.user_uid,
                business_uid=uid,
                role="owner",
            )

            workspaces.append(uid)

            for number in range(1, 4):
                db.add(
                    Lead(
                        business_uid=uid,
                        name=f"Synthetic {name} Prospect {number}",
                        category="Demo",
                        email=f"prospect{number}@example.test",
                        source="Synthetic Demo",
                        source_id=f"demo-{uid}-{number}",
                        status=["New", "Contacted", "Qualified"][number - 1],
                        notes=(
                            "Fictional record for buyer demonstration only."
                        ),
                    )
                )

            mission = Mission(
                business_uid=uid,
                title="Synthetic demo review",
                objective="Review fictional CRM records",
                status="planned",
                metadata_json='{"synthetic": true}',
            )

            db.add(mission)
            db.flush()

            db.add(
                AgentTask(
                    mission_id=mission.mission_uid,
                    agent_name="CEO",
                    task_type="analysis",
                    title="Synthetic review task",
                    status="pending",
                    input_data='{"synthetic": true}',
                )
            )

        db.commit()

        return {
            "workspaces": len(workspaces),
            "leads": 6,
            "missions": 2,
            "tasks": 2,
            "email_delivery": "disabled",
            "data": "synthetic",
        }


if __name__ == "__main__":
    import json

    print(json.dumps(seed_demo()))
