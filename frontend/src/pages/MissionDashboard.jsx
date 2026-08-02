import { useCallback, useEffect, useState } from "react";

import Card from "../components/ui/Card";
import MissionDetails from "../components/mission/MissionDetails";
import MissionKPICards from "../components/mission/MissionKPICards";
import MissionList from "../components/mission/MissionList";
import MissionTaskList from "../components/mission/MissionTaskList";
import MissionTimeline from "../components/mission/MissionTimeline";

import {
  getMissionTimeline,
  getPersistedMissions,
  getPersistedMissionTasks,
} from "../api/mission";

import "../styles/mission-dashboard.css";

function getMissionUid(mission) {
  return (
    mission?.mission_uid ||
    mission?.uid ||
    mission?.id ||
    ""
  );
}

function getErrorMessage(error, fallbackMessage) {
  return (
    error?.message ||
    error?.detail ||
    fallbackMessage
  );
}

export default function MissionDashboard() {
  const [missions, setMissions] = useState([]);
  const [selectedMission, setSelectedMission] =
    useState(null);

  const [missionLoading, setMissionLoading] =
    useState(true);
  const [missionError, setMissionError] =
    useState("");

  const [tasks, setTasks] = useState([]);
  const [tasksLoading, setTasksLoading] =
    useState(false);
  const [tasksError, setTasksError] =
    useState("");

  const [events, setEvents] = useState([]);
  const [eventsLoading, setEventsLoading] =
    useState(false);
  const [eventsError, setEventsError] =
    useState("");

  const selectedMissionUid =
    getMissionUid(selectedMission);

  const loadMissions = useCallback(async () => {
    setMissionLoading(true);
    setMissionError("");

    try {
      const response = await getPersistedMissions({
        limit: 100,
        offset: 0,
      });

      const missionItems = Array.isArray(
        response?.missions,
      )
        ? response.missions
        : [];

      setMissions(missionItems);

      setSelectedMission((currentMission) => {
        const currentUid =
          getMissionUid(currentMission);

        const existingMission =
          missionItems.find(
            (mission) =>
              getMissionUid(mission) === currentUid,
          );

        return (
          existingMission ||
          missionItems[0] ||
          null
        );
      });
    } catch (error) {
      setMissionError(
        getErrorMessage(
          error,
          "Unable to load persisted missions.",
        ),
      );

      setMissions([]);
      setSelectedMission(null);
    } finally {
      setMissionLoading(false);
    }
  }, []);

  const loadMissionTasks = useCallback(
    async (missionUid) => {
      if (!missionUid) {
        setTasks([]);
        setTasksError("");
        return;
      }

      setTasksLoading(true);
      setTasksError("");

      try {
        const response =
          await getPersistedMissionTasks(
            missionUid,
          );

        setTasks(
          Array.isArray(response?.tasks)
            ? response.tasks
            : [],
        );
      } catch (error) {
        setTasks([]);

        setTasksError(
          getErrorMessage(
            error,
            "Unable to load mission tasks.",
          ),
        );
      } finally {
        setTasksLoading(false);
      }
    },
    [],
  );

  const loadMissionEvents = useCallback(
    async (missionUid) => {
      if (!missionUid) {
        setEvents([]);
        setEventsError("");
        return;
      }

      setEventsLoading(true);
      setEventsError("");

      try {
        const response =
          await getMissionTimeline(missionUid);

        setEvents(
          Array.isArray(response?.events)
            ? response.events
            : [],
        );
      } catch (error) {
        const errorMessage = getErrorMessage(
          error,
          "Unable to load mission timeline.",
        );

        const noEventsFound =
          errorMessage
            .toLowerCase()
            .includes("no mission events found");

        setEvents([]);

        setEventsError(
          noEventsFound ? "" : errorMessage,
        );
      } finally {
        setEventsLoading(false);
      }
    },
    [],
  );

  const refreshSelectedMission = useCallback(
    async () => {
      if (!selectedMissionUid) {
        return;
      }

      await Promise.all([
        loadMissionTasks(selectedMissionUid),
        loadMissionEvents(selectedMissionUid),
      ]);
    },
    [
      selectedMissionUid,
      loadMissionTasks,
      loadMissionEvents,
    ],
  );

  useEffect(() => {
    loadMissions();
  }, [loadMissions]);

  useEffect(() => {
    if (!selectedMissionUid) {
      setTasks([]);
      setEvents([]);
      setTasksError("");
      setEventsError("");
      return;
    }

    loadMissionTasks(selectedMissionUid);
    loadMissionEvents(selectedMissionUid);
  }, [
    selectedMissionUid,
    loadMissionTasks,
    loadMissionEvents,
  ]);

  function handleSelectMission(mission) {
    setSelectedMission(mission);
  }

  return (
    <main className="mission-dashboard-page">
      <Card className="mission-dashboard-header">
        <div>
          <p className="eyebrow">
            AI Workforce
          </p>

          <h1>Mission Dashboard</h1>

          <p>
            Monitor autonomous AI missions,
            review executive activity, inspect
            execution timelines and manage every
            mission from a single workspace.
          </p>
        </div>

        <div className="mission-dashboard-header-actions">
          <button
            type="button"
            className="mission-dashboard-refresh-button"
            onClick={loadMissions}
            disabled={missionLoading}
          >
            {missionLoading
              ? "Refreshing..."
              : "Refresh Missions"}
          </button>

          <button
            type="button"
            className="mission-dashboard-refresh-button secondary"
            onClick={refreshSelectedMission}
            disabled={
              !selectedMissionUid ||
              tasksLoading ||
              eventsLoading
            }
          >
            Refresh Selected
          </button>
        </div>
      </Card>

      <MissionKPICards
        missions={missions}
        loading={missionLoading}
      />

      <div className="mission-dashboard-grid">
        <Card className="mission-dashboard-panel mission-dashboard-missions">
          <MissionList
            missions={missions}
            selectedMissionUid={
              selectedMissionUid
            }
            loading={missionLoading}
            error={missionError}
            onSelectMission={
              handleSelectMission
            }
            onRefresh={loadMissions}
          />
        </Card>

        <Card className="mission-dashboard-panel mission-dashboard-timeline">
          <MissionTimeline
            missionUid={selectedMissionUid}
            events={events}
            loading={eventsLoading}
            error={eventsError}
            onRefresh={() =>
              loadMissionEvents(
                selectedMissionUid,
              )
            }
          />
        </Card>

        <Card className="mission-dashboard-panel mission-dashboard-tasks">
          <MissionTaskList
            tasks={tasks}
            loading={tasksLoading}
            error={tasksError}
            onRefresh={() =>
              loadMissionTasks(
                selectedMissionUid,
              )
            }
          />
        </Card>

        <Card className="mission-dashboard-panel mission-dashboard-details">
          <MissionDetails
            mission={selectedMission}
          />
        </Card>
      </div>
    </main>
  );
}