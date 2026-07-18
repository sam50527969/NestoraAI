import uuid
from typing import Any, Dict, List, Optional


MISSIONS: Dict[str, Dict[str, Any]] = {}


def build_default_agents() -> List[Dict[str, Any]]:
    """
    Create the default visible AI workforce for a new mission.
    """
    return [
        {
            "name": "CEO Agent",
            "role": "Mission planning",
            "icon": "🧠",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting to plan mission",
        },
        {
            "name": "Research Agent",
            "role": "Business discovery",
            "icon": "🔍",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for mission",
        },
        {
            "name": "CRM Agent",
            "role": "Lead storage",
            "icon": "💾",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for businesses",
        },
        {
            "name": "Sales Agent",
            "role": "Lead scoring",
            "icon": "📈",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for CRM records",
        },
        {
            "name": "Website Agent",
            "role": "Website intelligence",
            "icon": "🌐",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for websites",
        },
        {
            "name": "Outreach Agent",
            "role": "Message generation",
            "icon": "📧",
            "status": "waiting",
            "progress": 0,
            "current_task": "Waiting for analysis",
        },
        {
            "name": "Proposal Agent",
            "role": "Proposal preparation",
            "icon": "📝",
            "status": "waiting",
            "progress": 0,
            "current_task": "Not enabled for this mission",
        },
    ]


def create_mission() -> Dict[str, Any]:
    """
    Create a new in-memory mission and return its initial state.
    """
    mission_id = str(uuid.uuid4())

    mission = {
        "mission_id": mission_id,
        "status": "queued",
        "progress": 0,
        "current_step": "Waiting",
        "searched": 0,
        "analyzed": 0,
        "outreach_generated": 0,
        "task_count": 0,
        "agents": build_default_agents(),
        "activity": [],
    }

    MISSIONS[mission_id] = mission

    return mission


def get_mission(
    mission_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Return a mission from the runtime store.
    """
    return MISSIONS.get(mission_id)


def mission_exists(
    mission_id: str,
) -> bool:
    """
    Check whether a mission exists in the runtime store.
    """
    return mission_id in MISSIONS


def update_mission(
    mission_id: str,
    **kwargs: Any,
) -> Optional[Dict[str, Any]]:
    """
    Update selected mission state fields.
    """
    mission = MISSIONS.get(mission_id)

    if mission is None:
        return None

    mission.update(kwargs)

    return mission


def update_agent(
    mission_id: str,
    agent_name: str,
    *,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    current_task: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Update one visible agent inside a mission.
    """
    mission = MISSIONS.get(mission_id)

    if mission is None:
        return None

    for agent in mission.get("agents", []):
        if agent.get("name") != agent_name:
            continue

        if status is not None:
            agent["status"] = status

        if progress is not None:
            agent["progress"] = max(
                0,
                min(int(progress), 100),
            )

        if current_task is not None:
            agent["current_task"] = current_task

        return agent

    return None


def fail_running_agents(
    mission_id: str,
    *,
    message: str = "Agent stopped because mission failed",
) -> None:
    """
    Mark every currently running visible agent as failed.
    """
    mission = MISSIONS.get(mission_id)

    if mission is None:
        return

    for agent in mission.get("agents", []):
        if agent.get("status") == "running":
            agent["status"] = "failed"
            agent["current_task"] = message


def reset_agent(
    mission_id: str,
    agent_name: str,
) -> Optional[Dict[str, Any]]:
    """
    Reset one agent to its initial waiting state.
    """
    mission = MISSIONS.get(mission_id)

    if mission is None:
        return None

    default_agents = build_default_agents()

    default_agent = next(
        (
            agent
            for agent in default_agents
            if agent["name"] == agent_name
        ),
        None,
    )

    if default_agent is None:
        return None

    for index, current_agent in enumerate(
        mission.get("agents", [])
    ):
        if current_agent.get("name") == agent_name:
            mission["agents"][index] = default_agent
            return default_agent

    return None


def remove_mission(
    mission_id: str,
) -> bool:
    """
    Remove a mission from runtime memory.
    """
    if mission_id not in MISSIONS:
        return False

    del MISSIONS[mission_id]

    return True


def clear_missions() -> None:
    """
    Clear all runtime missions.

    Intended mainly for local development and automated testing.
    """
    MISSIONS.clear()