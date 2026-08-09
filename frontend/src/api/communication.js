import { request } from "./client";

function buildQuery(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    query.set(key, String(value));
  });
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

export function getExecutiveInbox(recipient = "CEO", { unreadOnly = false, missionUid = null, limit = 25 } = {}) {
  const query = buildQuery({ unread_only: unreadOnly, mission_uid: missionUid, limit });
  return request(`/communication/inbox/${encodeURIComponent(recipient)}${query}`);
}

export function getExecutiveOutbox(sender = "CEO", { missionUid = null, limit = 25 } = {}) {
  const query = buildQuery({ mission_uid: missionUid, limit });
  return request(`/communication/outbox/${encodeURIComponent(sender)}${query}`);
}

export function getMissionMessages(missionUid, { limit = 100 } = {}) {
  if (!missionUid) return Promise.resolve({ count: 0, messages: [] });
  const query = buildQuery({ limit });
  return request(`/communication/missions/${encodeURIComponent(missionUid)}/messages${query}`);
}

export function getConversation(conversationUid, { limit = 100 } = {}) {
  if (!conversationUid) return Promise.resolve({ conversation_uid: "", count: 0, messages: [] });
  const query = buildQuery({ limit });
  return request(`/communication/conversations/${encodeURIComponent(conversationUid)}${query}`);
}

export function sendExecutiveMessage(payload) {
  return request("/communication/messages", { method: "POST", body: JSON.stringify(payload) });
}

export function replyToExecutiveMessage(messageUid, payload) {
  return request(`/communication/messages/${encodeURIComponent(messageUid)}/reply`, { method: "POST", body: JSON.stringify(payload) });
}

export function markExecutiveMessageRead(messageUid) {
  return request(`/communication/messages/${encodeURIComponent(messageUid)}/read`, { method: "PATCH" });
}
