from __future__ import annotations

from sqlalchemy.orm import Session

from app.executives.ceo.state import CompanyState, DepartmentState
from app.memory.service import ExecutiveMemoryService
from app.repositories.business_repository import BusinessRepository
from app.repositories.mission_repository import MissionRepository
from app.services.dashboard_service import get_dashboard_summary


class CEOCompanyStateBuilder:
    """Build a CEO company state from live Nestora data."""

    def __init__(
        self,
        db: Session,
        *,
        business_uid: str,
    ) -> None:
        self._db = db
        self._business_uid = business_uid
        self._business_repository = BusinessRepository(db)
        self._mission_repository = MissionRepository(db)
        self._memory_service = ExecutiveMemoryService(db)

    def build(self) -> CompanyState:
        business = self._business_repository.get_by_uid(
            self._business_uid
        )

        if business is None:
            raise ValueError(
                f"Business '{self._business_uid}' was not found."
            )

        currency = business.finances.currency

        state = CompanyState(
            metadata={
                "business_uid": self._business_uid,
                "currency": currency,
            }
        )

        state.crm = self._build_crm_state(
            currency=currency,
        )
        state.missions = self._build_mission_state()
        state.memory = self._build_memory_state()

        state.calculate_overall_health()

        state.critical_risks = self._collect_critical_risks(state)
        state.major_opportunities = self._collect_major_opportunities(state)

        state.metadata.update(
            {
                "source": "live_nestora_data",
                "departments_loaded": [
                    department.department
                    for department in state.available_departments()
                ],
            }
        )

        return state

    def _build_crm_state(
        self,
        *,
        currency: str,
    ) -> DepartmentState:
        dashboard = get_dashboard_summary(
            self._db,
            business_uid=self._business_uid,
        )
        kpis = dashboard.kpis

        health_score = self._calculate_crm_health(
            total_leads=kpis.total_leads,
            qualified_leads=kpis.qualified_leads,
            won_leads=kpis.won_leads,
            ai_score=kpis.ai_score,
        )

        risks: list[str] = []
        opportunities: list[str] = []

        if kpis.total_leads == 0:
            risks.append("CRM has no active leads.")

        if kpis.total_leads > 0 and kpis.qualified_leads == 0:
            risks.append("CRM has leads but none are qualified.")

        if kpis.high_priority_leads > 0:
            opportunities.append(
                f"{kpis.high_priority_leads} high-priority lead(s) "
                "are available for immediate follow-up."
            )

        if kpis.pipeline_value > 0:
            opportunities.append(
                f"Current CRM pipeline value is "
                f"{kpis.pipeline_value} {currency}."
            )

        return DepartmentState(
            department="CRM",
            status=self._health_status(health_score),
            health_score=health_score,
            summary=(
                f"{kpis.total_leads} total leads, "
                f"{kpis.qualified_leads} qualified, "
                f"{kpis.won_leads} won."
            ),
            metrics={
                "total_leads": kpis.total_leads,
                "high_priority_leads": kpis.high_priority_leads,
                "qualified_leads": kpis.qualified_leads,
                "won_leads": kpis.won_leads,
                "pipeline_value": kpis.pipeline_value,
                "ai_score": kpis.ai_score,
            },
            risks=risks,
            opportunities=opportunities,
        )

    def _build_mission_state(self) -> DepartmentState:
        missions = self._mission_repository.list_by_business(
            self._business_uid,
            limit=100,
        )

        total = len(missions)
        running = sum(
            1
            for mission in missions
            if str(mission.status).lower() == "running"
        )
        completed = sum(
            1
            for mission in missions
            if str(mission.status).lower() == "completed"
        )
        failed = sum(
            1
            for mission in missions
            if str(mission.status).lower() == "failed"
        )

        average_progress = (
            round(
                sum(
                    max(0, min(int(mission.progress or 0), 100))
                    for mission in missions
                )
                / total,
                2,
            )
            if total
            else 0.0
        )

        health_score = self._calculate_mission_health(
            total=total,
            completed=completed,
            failed=failed,
            average_progress=average_progress,
        )

        risks: list[str] = []
        opportunities: list[str] = []

        if failed:
            risks.append(
                f"{failed} mission(s) have failed and require review."
            )

        if running:
            opportunities.append(
                f"{running} mission(s) are currently running."
            )

        if completed:
            opportunities.append(
                f"{completed} mission(s) have been completed."
            )

        return DepartmentState(
            department="Missions",
            status=self._health_status(health_score),
            health_score=health_score,
            summary=(
                f"{total} missions: {running} running, "
                f"{completed} completed, {failed} failed."
            ),
            metrics={
                "total": total,
                "running": running,
                "completed": completed,
                "failed": failed,
                "average_progress": average_progress,
            },
            risks=risks,
            opportunities=opportunities,
        )

    def _build_memory_state(self) -> DepartmentState:
        memories = self._memory_service.list_memories(
            executive="CEO",
            limit=10,
        )

        total = len(memories)

        if not memories:
            return DepartmentState(
                department="Memory",
                status="healthy",
                health_score=100.0,
                summary="No prior CEO executive memories are available.",
                metrics={
                    "total": 0,
                    "high_importance": 0,
                },
            )

        high_importance = sum(
            1
            for memory in memories
            if int(memory.importance or 0) >= 8
        )

        opportunities = [
            (
                f"Prior CEO memory [{memory.category}]: "
                f"{memory.memory}"
            )
            for memory in memories
        ]

        return DepartmentState(
            department="Memory",
            status="healthy",
            health_score=100.0,
            summary=(
                f"{total} prior CEO executive "
                f"memory record(s) loaded."
            ),
            metrics={
                "total": total,
                "high_importance": high_importance,
            },
            opportunities=opportunities,
        )

    @staticmethod
    def _calculate_crm_health(
        *,
        total_leads: int,
        qualified_leads: int,
        won_leads: int,
        ai_score: int,
    ) -> float:
        if total_leads == 0:
            return 20.0

        qualification_rate = min(
            qualified_leads / total_leads,
            1.0,
        )

        win_rate = min(
            won_leads / total_leads,
            1.0,
        )

        score = (
            30.0
            + qualification_rate * 25.0
            + win_rate * 25.0
            + (ai_score / 100.0) * 20.0
        )

        return round(min(score, 100.0), 2)

    @staticmethod
    def _calculate_mission_health(
        *,
        total: int,
        completed: int,
        failed: int,
        average_progress: float,
    ) -> float:
        if total == 0:
            return 50.0

        completion_rate = completed / total
        failure_rate = failed / total

        score = (
            50.0
            + completion_rate * 35.0
            + (average_progress / 100.0) * 15.0
            - failure_rate * 40.0
        )

        return round(
            max(0.0, min(score, 100.0)),
            2,
        )

    @staticmethod
    def _health_status(score: float) -> str:
        if score >= 75:
            return "healthy"

        if score >= 40:
            return "warning"

        return "critical"

    @staticmethod
    def _collect_critical_risks(
        state: CompanyState,
    ) -> list[str]:
        risks: list[str] = []

        for department in state.available_departments():
            if department.health_score < 40:
                risks.extend(department.risks)

        return risks

    @staticmethod
    def _collect_major_opportunities(
        state: CompanyState,
    ) -> list[str]:
        opportunities: list[str] = []

        for department in state.available_departments():
            opportunities.extend(department.opportunities)

        return opportunities