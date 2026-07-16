from datetime import datetime

MAX_ACTIVITY_ITEMS = 100


def add_activity(mission, agent, message):
    """
    Adds a timestamped activity entry to a mission.
    """

    if "activity" not in mission:
        mission["activity"] = []

    mission["activity"].append(
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "message": message,
        }
    )

    if len(mission["activity"]) > MAX_ACTIVITY_ITEMS:
        mission["activity"] = mission["activity"][-MAX_ACTIVITY_ITEMS:]


def get_activity(mission):
    return mission.get("activity", [])