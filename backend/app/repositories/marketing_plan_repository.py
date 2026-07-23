import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import MarketingPlan


class MarketingPlanRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    def create(
        self,
        *,
        request_data: dict[str, Any],
        response_data: dict[str, Any],
    ) -> MarketingPlan:
        business = request_data.get(
            "business",
            {},
        )

        goal = request_data.get(
            "goal",
            {},
        )

        plan = MarketingPlan(
            business_id=str(
                business.get(
                    "business_id",
                    "",
                )
            ),
            business_name=str(
                business.get(
                    "business_name",
                    "",
                )
            ),
            industry=str(
                business.get(
                    "industry",
                    "",
                )
            ),
            location=business.get(
                "location",
            ),
            objective=str(
                goal.get(
                    "objective",
                    "",
                )
            ),
            status="draft",
            approval_required=bool(
                response_data.get(
                    "approval_required",
                    goal.get(
                        "approval_required",
                        True,
                    ),
                )
            ),
            currency=str(
                goal.get(
                    "currency",
                    "QAR",
                )
            ),
            monthly_budget=float(
                goal.get(
                    "monthly_budget",
                    0,
                )
                or 0
            ),
            timeline_days=int(
                goal.get(
                    "timeline_days",
                    30,
                )
                or 30
            ),
            request_data=self._serialize(
                request_data,
            ),
            response_data=self._serialize(
                response_data,
            ),
            analysis_data=self._serialize_optional(
                response_data.get(
                    "analysis",
                )
            ),
            strategy_data=self._serialize_optional(
                response_data.get(
                    "strategy",
                )
            ),
            budget_data=self._serialize_optional(
                response_data.get(
                    "budget",
                )
            ),
            campaign_data=self._serialize_optional(
                response_data.get(
                    "campaign",
                )
            ),
            prediction_data=self._serialize_optional(
                response_data.get(
                    "prediction",
                )
            ),
            memory_entries_created=int(
                response_data.get(
                    "memory_entries_created",
                    0,
                )
                or 0
            ),
        )

        try:
            self.db.add(plan)
            self.db.commit()
            self.db.refresh(plan)
        except Exception:
            self.db.rollback()
            raise

        return plan

    def get_by_id(
        self,
        plan_id: int,
    ) -> MarketingPlan | None:
        return (
            self.db.query(MarketingPlan)
            .filter(
                MarketingPlan.id == plan_id,
            )
            .first()
        )

    def get_by_uid(
        self,
        plan_uid: str,
    ) -> MarketingPlan | None:
        return (
            self.db.query(MarketingPlan)
            .filter(
                MarketingPlan.plan_uid == plan_uid,
            )
            .first()
        )

    def list_plans(
        self,
        *,
        business_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MarketingPlan]:
        query = self.db.query(
            MarketingPlan,
        )

        if business_id:
            query = query.filter(
                MarketingPlan.business_id
                == business_id,
            )

        if status:
            query = query.filter(
                MarketingPlan.status
                == status,
            )

        return (
            query.order_by(
                MarketingPlan.created_at.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_latest(
        self,
        *,
        business_id: str | None = None,
    ) -> MarketingPlan | None:
        query = self.db.query(
            MarketingPlan,
        )

        if business_id:
            query = query.filter(
                MarketingPlan.business_id
                == business_id,
            )

        return (
            query.order_by(
                MarketingPlan.created_at.desc(),
            )
            .first()
        )

    def approve(
        self,
        *,
        plan_uid: str,
        approved_by: str,
    ) -> MarketingPlan | None:
        plan = self.get_by_uid(
            plan_uid,
        )

        if plan is None:
            return None

        plan.status = "approved"
        plan.approved_by = approved_by
        plan.approved_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(plan)
        except Exception:
            self.db.rollback()
            raise

        return plan

    def archive(
        self,
        *,
        plan_uid: str,
    ) -> MarketingPlan | None:
        plan = self.get_by_uid(
            plan_uid,
        )

        if plan is None:
            return None

        plan.status = "archived"

        try:
            self.db.commit()
            self.db.refresh(plan)
        except Exception:
            self.db.rollback()
            raise

        return plan

    @staticmethod
    def to_dict(
        plan: MarketingPlan,
        *,
        include_payloads: bool = True,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": plan.id,
            "plan_uid": plan.plan_uid,
            "business_id": plan.business_id,
            "business_name": plan.business_name,
            "industry": plan.industry,
            "location": plan.location,
            "objective": plan.objective,
            "status": plan.status,
            "approval_required": (
                plan.approval_required
            ),
            "approved_by": plan.approved_by,
            "approved_at": (
                plan.approved_at.isoformat()
                if plan.approved_at
                else None
            ),
            "currency": plan.currency,
            "monthly_budget": (
                plan.monthly_budget
            ),
            "timeline_days": (
                plan.timeline_days
            ),
            "memory_entries_created": (
                plan.memory_entries_created
            ),
            "created_at": (
                plan.created_at.isoformat()
                if plan.created_at
                else None
            ),
            "updated_at": (
                plan.updated_at.isoformat()
                if plan.updated_at
                else None
            ),
        }

        if include_payloads:
            data.update(
                {
                    "request": (
                        MarketingPlanRepository
                        ._deserialize(
                            plan.request_data,
                        )
                    ),
                    "response": (
                        MarketingPlanRepository
                        ._deserialize(
                            plan.response_data,
                        )
                    ),
                    "analysis": (
                        MarketingPlanRepository
                        ._deserialize_optional(
                            plan.analysis_data,
                        )
                    ),
                    "strategy": (
                        MarketingPlanRepository
                        ._deserialize_optional(
                            plan.strategy_data,
                        )
                    ),
                    "budget": (
                        MarketingPlanRepository
                        ._deserialize_optional(
                            plan.budget_data,
                        )
                    ),
                    "campaign": (
                        MarketingPlanRepository
                        ._deserialize_optional(
                            plan.campaign_data,
                        )
                    ),
                    "prediction": (
                        MarketingPlanRepository
                        ._deserialize_optional(
                            plan.prediction_data,
                        )
                    ),
                }
            )

        return data

    @staticmethod
    def _serialize(
        value: Any,
    ) -> str:
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _serialize_optional(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        return MarketingPlanRepository._serialize(
            value,
        )

    @staticmethod
    def _deserialize(
        value: str,
    ) -> Any:
        return json.loads(
            value,
        )

    @staticmethod
    def _deserialize_optional(
        value: str | None,
    ) -> Any:
        if value is None:
            return None

        return MarketingPlanRepository._deserialize(
            value,
        )