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
        raise RuntimeError("Use a new demo database path; existing data is never overwritten.")
    if os.getenv("EMAIL_PROVIDER", "disabled") != "disabled":
        raise RuntimeError("Disable email delivery for this demo.")
    if os.getenv("LLM_PROVIDER", "mock") != "mock":
        raise RuntimeError("Use the mock provider for an offline demo.")
    password = os.getenv("NESTORA_DEMO_PASSWORD", "")
    if len(password) < 12:
        raise RuntimeError("Set NESTORA_DEMO_PASSWORD to a private test password of at least 12 characters.")

    from prepare_production_database import prepare_database
    prepare_database()
    from fastapi.testclient import TestClient
    from main import app
    from app.database.database import SessionLocal
    from app.database.models import AgentTask, Mission

    with TestClient(app) as client:
        registration = client.post("/auth/register", json={"email": "buyer-demo@nestora.test", "full_name": "Synthetic Buyer Demo", "password": password})
        registration.raise_for_status()
        login = client.post("/auth/login", json={"email": "buyer-demo@nestora.test", "password": password})
        login.raise_for_status()
        headers = {"Authorization": "Bearer " + login.json()["access_token"]}
        workspaces = []
        for name in ("Demo Design Studio", "Demo Consulting Office"):
            response = client.post("/businesses", headers=headers, json={"name": name, "industry": "other", "country": "Qatar", "city": "Doha", "description": "Synthetic demonstration. No real clients or revenue.", "finances": {"currency": "USD"}})
            response.raise_for_status()
            uid = response.json()["business_uid"]
            workspaces.append(uid)
            headers["X-Business-Uid"] = uid
            for number in range(1, 4):
                response = client.post("/crm/leads", headers=headers, json={"name": f"Synthetic {name} Prospect {number}", "category": "Demo", "email": f"prospect{number}@example.test", "source": "Synthetic Demo", "source_id": f"demo-{uid}-{number}"})
                response.raise_for_status()
                lead_id = response.json()["id"]
                response = client.put(f"/crm/leads/{lead_id}", headers=headers, json={"status": ["New", "Contacted", "Qualified"][number-1], "notes": "Fictional record for buyer demonstration only."})
                response.raise_for_status()
            with SessionLocal() as db:
                mission = Mission(business_uid=uid, title="Synthetic demo review", objective="Review fictional CRM records", status="planned", metadata_json='{"synthetic": true}')
                db.add(mission)
                db.flush()
                db.add(AgentTask(mission_id=mission.mission_uid, agent_name="CEO", task_type="analysis", title="Synthetic review task", status="pending", input_data='{"synthetic": true}'))
                db.commit()
        return {"workspaces": len(workspaces), "leads": 6, "missions": 2, "tasks": 2, "email_delivery": "disabled", "data": "synthetic"}


if __name__ == "__main__":
    import json
    print(json.dumps(seed_demo()))
