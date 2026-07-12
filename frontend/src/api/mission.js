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