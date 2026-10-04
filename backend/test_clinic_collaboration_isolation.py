"""Exercise real authenticated requests across two owners and workspaces."""
import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.bootstrap.routes import register_routes
from app.database.database import get_db
from app.database.metadata import metadata
from app.clinic.models import ClinicLead
from app.collaboration.models import CollaborationSession
from app.database.models import Mission


@pytest.fixture
def environment():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    app = FastAPI()
    register_routes(app)
    def db_override():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = db_override
    with TestClient(app) as client:
        headers = []
        workspaces = []
        for name in ("alpha", "beta"):
            email = f"{name}-{uuid.uuid4().hex}@nestora.test"
            assert client.post("/auth/register", json={"email": email, "full_name": name, "password": "SyntheticTest123!"}).status_code == 201
            token = client.post("/auth/login", json={"email": email, "password": "SyntheticTest123!"}).json()["access_token"]
            h = {"Authorization": f"Bearer {token}"}
            response = client.post("/businesses", headers=h, json={"name": name, "industry": "other", "country": "Qatar"})
            assert response.status_code == 201, response.text
            uid = response.json()["business_uid"]
            h["X-Business-Uid"] = uid
            headers.append(h)
            workspaces.append(uid)
        yield client, factory, headers, workspaces
    engine.dispose()


def test_clinic_cross_account_read_write_and_legacy_isolation(environment):
    client, factory, (a, b), _ = environment
    response = client.post("/clinic/leads", headers=a, json={"patient_name": "Synthetic Alpha", "phone": "00000000", "treatment": "Demo"})
    assert response.status_code == 201
    lead_id = response.json()["id"]
    assert len(client.get("/clinic/leads", headers=a).json()) == 1
    assert client.get("/clinic/leads", headers=b).json() == []
    for action in ("contacted", "appointment-booked"):
        assert client.patch(f"/clinic/leads/{lead_id}/{action}", headers=b).status_code == 404
    assert client.patch(f"/clinic/leads/{lead_id}/contacted", headers=a).status_code == 200
    with factory() as db:
        db.add(ClinicLead(patient_name="Unassigned", phone="000", treatment="Demo"))
        db.commit()
    assert len(client.get("/clinic/leads", headers=a).json()) == 1
    assert client.get("/clinic/followups/due", headers=b).json() == []
    spoofed = {**b, "X-Business-Uid": a["X-Business-Uid"]}
    assert client.get("/clinic/leads", headers=spoofed).status_code == 403


def test_collaboration_cross_account_all_operations(environment):
    client, factory, (a, b), _ = environment
    response = client.post("/collaboration/sessions", headers=a, json={"title": "Synthetic plan", "objective": "Review demo"})
    assert response.status_code == 201
    uid = response.json()["session_uid"]
    path = f"/collaboration/sessions/{uid}"
    assert client.get(path, headers=a).status_code == 200
    assert client.get(path, headers=b).status_code == 404
    assert client.get("/collaboration/sessions", headers=b).json()["sessions"] == []
    assert client.post(path + "/contributions", headers=b, json={"executive": "CMO", "content": "Foreign"}).status_code == 404
    assert client.post(path + "/decision", headers=b, json={"decision": "Foreign", "status": "approved"}).status_code == 404
    assert client.delete(path, headers=b).status_code == 404
    assert client.post(path + "/contributions", headers=a, json={"executive": "CMO", "content": "Demo"}).status_code == 201
    assert client.get(path, headers=a).json()["contribution_count"] == 1
    with factory() as db:
        db.add(CollaborationSession(title="Legacy", objective="Unassigned"))
        db.commit()
    assert client.get("/collaboration/sessions", headers=a).json()["count"] == 1
    assert client.post(path + "/decision", headers=a, json={"decision": "Approved demo", "status": "approved"}).status_code == 200
    assert client.delete(path, headers=a).status_code == 200


def test_collaboration_rejects_foreign_mission(environment):
    client, factory, (a, b), workspaces = environment
    with factory() as db:
        db.add(Mission(mission_uid="foreign-demo", business_uid=workspaces[1], title="Demo", objective="Demo"))
        db.commit()
    payload = {"title": "Demo", "objective": "Demo", "mission_uid": "foreign-demo"}
    assert client.post("/collaboration/sessions", headers=a, json=payload).status_code == 404
    assert client.post("/collaboration/sessions", headers=b, json=payload).status_code == 201


def test_ownership_migration_preserves_unassigned_records(tmp_path):
    import importlib.util
    from pathlib import Path
    from unittest.mock import patch
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import inspect, text
    path = Path(__file__).parent / "alembic/versions/86b4d920a001_scope_clinic_collaboration.py"
    spec = importlib.util.spec_from_file_location("ownership_revision", path)
    revision = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(revision)
    engine = create_engine(f"sqlite:///{tmp_path / 'migration.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE clinic_leads (id INTEGER PRIMARY KEY, patient_name TEXT)"))
        connection.execute(text("INSERT INTO clinic_leads VALUES (1, 'Synthetic legacy')"))
        connection.execute(text("CREATE TABLE collaboration_sessions (id INTEGER PRIMARY KEY, title TEXT)"))
        connection.execute(text("INSERT INTO collaboration_sessions VALUES (1, 'Synthetic legacy')"))
        operations = Operations(MigrationContext.configure(connection))
        with patch.object(revision, "op", operations):
            revision.upgrade()
            revision.upgrade()
        for name in ("clinic_leads", "collaboration_sessions"):
            assert connection.execute(text(f"SELECT business_uid FROM {name}")).scalar_one() is None
            assert len(inspect(connection).get_indexes(name)) == 1
    engine.dispose()


def test_pipeline_history_is_scoped_to_lead_workspace(environment):
    from app.database.models import Lead
    from app.pipeline_activity.models import PipelineActivity
    client, factory, (a, b), workspaces = environment
    with factory() as db:
        lead = Lead(name="Synthetic private lead", business_uid=workspaces[0])
        db.add(lead)
        db.flush()
        lead_id = lead.id
        db.add(PipelineActivity(lead_id=lead_id, lead_name=lead.name, previous_status="New", new_status="Contacted", notes="Synthetic confidential notes"))
        db.commit()
    assert len(client.get("/pipeline-activities", headers=a).json()) == 1
    assert client.get("/pipeline-activities", headers=b).json() == []
    assert client.get(f"/pipeline-activities?lead_id={lead_id}", headers=b).json() == []
    assert client.get("/pipeline-activities").status_code == 401
