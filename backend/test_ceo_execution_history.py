from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from app.database.database import Base
from app.execution_history.service import (
    get_execution_record,
    get_execution_record_by_approval,
    list_execution_records,
    save_execution_record,
)


@pytest.fixture
def db_session(
    tmp_path: Path,
) -> Generator[Session, None, None]:
    database_path = (
        tmp_path
        / "ceo-execution-history-test.db"
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


def create_execution(
    db: Session,
    *,
    approval_uid: str,
    objective: str,
    success: bool = True,
):
    return save_execution_record(
        db,
        approval_uid=approval_uid,
        business_uid="biz_atlas",
        objective=objective,
        execution_result={
            "status": (
                "completed"
                if success
                else "failed"
            ),
            "success": success,
            "mission_id": (
                f"mission_{approval_uid}"
            ),
            "workflow_id": (
                f"workflow_{approval_uid}"
            ),
            "completed_task_count": (
                2 if success else 0
            ),
            "failed_task_count": (
                0 if success else 1
            ),
        },
    )


def test_get_execution_record_by_uid(
    db_session,
):
    created = create_execution(
        db_session,
        approval_uid="apr_history_uid",
        objective="Increase revenue",
    )

    found = get_execution_record(
        db_session,
        created.execution_uid,
        business_uid="biz_atlas",
    )

    assert found is not None

    assert (
        found.execution_uid
        == created.execution_uid
    )

    assert (
        found.approval_uid
        == "apr_history_uid"
    )

    assert (
        found.objective
        == "Increase revenue"
    )


def test_get_execution_record_by_approval(
    db_session,
):
    created = create_execution(
        db_session,
        approval_uid="apr_history_approval",
        objective="Recover customers",
    )

    found = (
        get_execution_record_by_approval(
            db_session,
            "apr_history_approval",
            business_uid="biz_atlas",
        )
    )

    assert found is not None

    assert (
        found.execution_uid
        == created.execution_uid
    )


def test_missing_execution_returns_none(
    db_session,
):
    found = get_execution_record(
        db_session,
        "exec_missing",
        business_uid="biz_atlas",
    )

    assert found is None


def test_missing_approval_returns_none(
    db_session,
):
    found = (
        get_execution_record_by_approval(
            db_session,
            "apr_missing",
            business_uid="biz_atlas",
        )
    )

    assert found is None


def test_list_execution_records(
    db_session,
):
    create_execution(
        db_session,
        approval_uid="apr_history_1",
        objective="Objective 1",
    )

    create_execution(
        db_session,
        approval_uid="apr_history_2",
        objective="Objective 2",
    )

    create_execution(
        db_session,
        approval_uid="apr_history_3",
        objective="Objective 3",
        success=False,
    )

    records = list_execution_records(
        db_session,
        business_uid="biz_atlas",
    )

    assert len(records) == 3

    approval_uids = {
        record.approval_uid
        for record in records
    }

    assert approval_uids == {
        "apr_history_1",
        "apr_history_2",
        "apr_history_3",
    }


def test_list_execution_records_supports_pagination(
    db_session,
):
    for index in range(5):
        create_execution(
            db_session,
            approval_uid=(
                f"apr_page_{index}"
            ),
            objective=(
                f"Objective {index}"
            ),
        )

    first_page = list_execution_records(
        db_session,
        business_uid="biz_atlas",
        limit=2,
        offset=0,
    )

    second_page = list_execution_records(
        db_session,
        business_uid="biz_atlas",
        limit=2,
        offset=2,
    )

    assert len(first_page) == 2
    assert len(second_page) == 2

    first_ids = {
        record.execution_uid
        for record in first_page
    }

    second_ids = {
        record.execution_uid
        for record in second_page
    }

    assert first_ids.isdisjoint(
        second_ids
    )


def test_list_execution_records_limits_maximum(
    db_session,
):
    records = list_execution_records(
        db_session,
        business_uid="biz_atlas",
        limit=1000,
    )

    assert records == []


def test_list_execution_records_handles_negative_values(
    db_session,
):
    create_execution(
        db_session,
        approval_uid="apr_safe_values",
        objective="Safe pagination",
    )

    records = list_execution_records(
        db_session,
        business_uid="biz_atlas",
        limit=-10,
        offset=-50,
    )

    assert len(records) == 1