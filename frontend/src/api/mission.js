import { request } from "./client";

export function startMission(payload) {
  return request("/missions/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMissionStatus(missionId) {
  return request(`/missions/${missionId}`);
}

export function getPersistedMissions({
  limit = 100,
  offset = 0,
} = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  return request(`/missions?${params.toString()}`);
}

export function executePersistedMission(missionUid) {
  if (!missionUid) {
    throw new Error("Mission UID is required.");
  }

  return request(`/missions/${missionUid}/execute`, {
    method: "POST",
  });
}

export function getPersistedMissionTasks(missionUid) {
  if (!missionUid) {
    throw new Error("Mission UID is required.");
  }

  return request(`/missions/${missionUid}/tasks`);
}

export function getMissionTimeline(missionUid) {
  if (!missionUid) {
    throw new Error("Mission UID is required.");
  }

  return request(`/missions/${missionUid}/events`);
}