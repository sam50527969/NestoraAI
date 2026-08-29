from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.models import Base
from app.schemas.crm import LeadCreate
from app.services.crm_service import (
    create_lead,
    find_lead_by_name,
    get_lead,
    get_leads,
    get_pipeline_summary,
)


def test_crm_business_scope_isolation() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = Session()

    try:
        legacy = create_lead(
            db,
            LeadCreate(
                name="Shared Trading",
            ),
        )

        alpha = create_lead(
            db,
            LeadCreate(
                business_uid="biz-alpha",
                name="Shared Trading",
            ),
        )

        beta = create_lead(
            db,
            LeadCreate(
                business_uid="biz-beta",
                name="Shared Trading",
            ),
        )

        alpha_duplicate = create_lead(
            db,
            LeadCreate(
                business_uid="biz-alpha",
                name="  shared   trading  ",
                website="https://alpha.example",
            ),
        )

        assert len(
            {
                legacy.id,
                alpha.id,
                beta.id,
            }
        ) == 3

        assert alpha_duplicate.id == alpha.id
        assert (
            alpha_duplicate.website
            == "https://alpha.example"
        )

        legacy_leads = get_leads(db)

        alpha_leads = get_leads(
            db,
            business_uid="biz-alpha",
        )

        beta_leads = get_leads(
            db,
            business_uid="biz-beta",
        )

        assert [
            item.id
            for item in legacy_leads
        ] == [legacy.id]

        assert [
            item.id
            for item in alpha_leads
        ] == [alpha.id]

        assert [
            item.id
            for item in beta_leads
        ] == [beta.id]

        alpha_lookup = find_lead_by_name(
            db,
            "Shared Trading",
            business_uid="biz-alpha",
        )

        assert alpha_lookup is not None
        assert alpha_lookup.id == alpha.id

        cross_business = get_lead(
            db,
            beta.id,
            business_uid="biz-alpha",
        )

        assert cross_business is None

        alpha_summary = get_pipeline_summary(
            db,
            business_uid="biz-alpha",
        )

        assert alpha_summary["total_leads"] == 1

    finally:
        db.close()
        engine.dispose()
