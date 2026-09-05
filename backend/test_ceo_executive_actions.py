import asyncio
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from app.approvals.executor import (
    execute_action,
)
from app.core.execution.execution_service import (
    execution_service,
)
from app.core.execution.executive_registry import (
    executive_registry,
)
from app.database.database import Base
from app.execution_history.models import (
    CEOExecutionRecord,
)
from app.executives.ceo.models import (
    ExecutiveAction,
    ExecutivePlan,
)
from app.executives.ceo.serialization import (
    serialize_executive_plan,
)


class FollowUpExecutive:
    async def execute(
        self,
        payload,
    ):
        return {
            "status": "completed",
            "department": "follow_up",
            "instruction": payload[
                "instruction"
            ],
        }


class MarketingExecutive:
    def execute(
        self,
        payload,
    ):
        return {
            "status": "completed",
            "department": "marketing",
            "instruction": payload[
                "instruction"
            ],
        }


@pytest.fixture
def db_session(
    tmp_path: Path,
) -> Generator[Session, None, None]:
    database_path = (
        tmp_path
        / "ceo-execution-test.db"
    )

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(
        bind=engine
    )

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = session_factory()

    try:
        yield db
    finally:
        db.close()

        Base.metadata.drop_all(
            bind=engine
        )

        engine.dispose()


def build_test_plan() -> ExecutivePlan:
    return ExecutivePlan(
        objective=(
            "Recover inactive customers"
        ),
        summary=(
            "Identify inactive customers "
            "and prepare a recovery campaign."
        ),
        actions=[
            ExecutiveAction(
                title=(
                    "Identify inactive "
                    "customers"
                ),
                department="Follow Up",
                instruction=(
                    "Find customers who have "
                    "not engaged recently."
                ),
                recommendation_score=92.0,
                requires_approval=True,
                metadata={
                    "priority_level": "high",
                },
            ),
            ExecutiveAction(
                title=(
                    "Prepare recovery campaign"
                ),
                department="Marketing",
                instruction=(
                    "Create a recovery "
                    "campaign for inactive "
                    "customers."
                ),
                recommendation_score=87.0,
                requires_approval=True,
                metadata={
                    "priority_level": "medium",
                },
            ),
        ],
    )


def setup_executives() -> None:
    execution_service.clear()
    executive_registry.clear()

    executive_registry.register(
        "follow_up",
        FollowUpExecutive(),
    )

    executive_registry.register(
        "marketing",
        MarketingExecutive(),
    )


def teardown_executives() -> None:
    execution_service.clear()
    executive_registry.clear()


def execute_test_plan(
    db: Session,
    approval_uid: str,
):
    plan = build_test_plan()

    payload = {
        "executive_plan": (
            serialize_executive_plan(
                plan
            )
        )
    }

    return asyncio.run(
        execute_action(
            "executive_action",
            db,
            payload,
            approval_uid,
            "biz_atlas",
        )
    )


def test_executive_action_executes_plan(
    db_session,
):
    setup_executives()

    try:
        result = execute_test_plan(
            db_session,
            "apr_test_execution",
        )

        assert (
            result["action_type"]
            == "executive_action"
        )

        assert (
            result["status"]
            == "completed"
        )

        assert result["success"] is True

        assert (
            result["completed_task_count"]
            == 2
        )

        assert (
            result["failed_task_count"]
            == 0
        )

        assert result["mission_id"]
        assert result["workflow_id"]
        assert result["execution_uid"]

    finally:
        teardown_executives()


def test_executive_action_builds_real_mission(
    db_session,
):
    setup_executives()

    try:
        result = execute_test_plan(
            db_session,
            "apr_test_mission",
        )

        mission = (
            execution_service.get_mission(
                result["mission_id"]
            )
        )

        assert mission is not None

        assert (
            mission.objective
            == "Recover inactive customers"
        )

        assert "follow_up" in (
            mission.assigned_to
        )

        assert "marketing" in (
            mission.assigned_to
        )

        assert (
            mission.metadata[
                "business_uid"
            ]
            == "biz_atlas"
        )

    finally:
        teardown_executives()


def test_executive_action_executes_departments(
    db_session,
):
    setup_executives()

    try:
        result = execute_test_plan(
            db_session,
            "apr_test_departments",
        )

        workflow = (
            execution_service.get_workflow(
                result["workflow_id"]
            )
        )

        executors = {
            task.executor
            for task in workflow.tasks
        }

        assert executors == {
            "follow_up",
            "marketing",
        }

        assert all(
            task.status.value
            == "completed"
            for task in workflow.tasks
        )

        assert (
            workflow.metadata[
                "business_uid"
            ]
            == "biz_atlas"
        )

    finally:
        teardown_executives()


def test_execution_result_is_persisted(
    db_session,
):
    setup_executives()

    try:
        result = execute_test_plan(
            db_session,
            "apr_test_persistence",
        )

        record = (
            db_session.query(
                CEOExecutionRecord
            )
            .filter(
                CEOExecutionRecord.approval_uid
                == "apr_test_persistence"
            )
            .one()
        )

        assert (
            record.execution_uid
            == result["execution_uid"]
        )

        assert (
            record.objective
            == "Recover inactive customers"
        )

        assert (
            record.mission_id
            == result["mission_id"]
        )

        assert (
            record.workflow_id
            == result["workflow_id"]
        )

        assert record.status == "completed"
        assert record.success is True

        assert (
            record.business_uid
            == "biz_atlas"
        )

        assert (
            record.completed_task_count
            == 2
        )

        assert (
            record.failed_task_count
            == 0
        )

        assert record.result_json

    finally:
        teardown_executives()


def test_duplicate_execution_record_is_not_created(
    db_session,
):
    setup_executives()

    try:
        first = execute_test_plan(
            db_session,
            "apr_test_duplicate",
        )

        second = execute_test_plan(
            db_session,
            "apr_test_duplicate",
        )

        records = (
            db_session.query(
                CEOExecutionRecord
            )
            .filter(
                CEOExecutionRecord.approval_uid
                == "apr_test_duplicate"
            )
            .all()
        )

        assert len(records) == 1

        assert (
            first["execution_uid"]
            == second["execution_uid"]
        )

    finally:
        teardown_executives()


def test_missing_executive_plan_is_rejected(
    db_session,
):
    setup_executives()

    try:
        with pytest.raises(
            ValueError,
            match=(
                "Executive action payload must "
                "contain an executive_plan."
            ),
        ):
            asyncio.run(
                execute_action(
                    "executive_action",
                    db_session,
                    {},
                    "apr_test_missing",
                    "biz_atlas",
                )
            )

    finally:
        teardown_executives()


def test_unregistered_department_fails_execution(
    db_session,
):
    execution_service.clear()
    executive_registry.clear()

    try:
        plan = ExecutivePlan(
            objective=(
                "Execute unsupported "
                "department action"
            ),
            summary=(
                "Test dispatcher failure."
            ),
            actions=[
                ExecutiveAction(
                    title="Run finance action",
                    department="Finance",
                    instruction=(
                        "Prepare financial "
                        "analysis."
                    ),
                    recommendation_score=90.0,
                    requires_approval=True,
                    metadata={
                        "priority_level": "high",
                    },
                )
            ],
        )

        payload = {
            "executive_plan": (
                serialize_executive_plan(
                    plan
                )
            )
        }

        result = asyncio.run(
            execute_action(
                "executive_action",
                db_session,
                payload,
                "apr_test_failure",
                "biz_atlas",
            )
        )

        assert result["success"] is False
        assert result["status"] == "failed"

        assert (
            result["completed_task_count"]
            == 0
        )

        assert (
            result["failed_task_count"]
            == 1
        )

        record = (
            db_session.query(
                CEOExecutionRecord
            )
            .filter(
                CEOExecutionRecord.approval_uid
                == "apr_test_failure"
            )
            .one()
        )

        assert record.success is False
        assert record.status == "failed"
        assert record.failed_task_count == 1

        assert (
            record.execution_uid
            == result["execution_uid"]
        )

    finally:
        execution_service.clear()
        executive_registry.clear()
