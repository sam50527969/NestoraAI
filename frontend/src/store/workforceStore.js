import { create } from "zustand";

import workforceSocket from "../realtime/workforceSocket";


function normalizeName(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase();
}


function getExecutiveKey(executive) {
  return (
    executive?.id
    ?? executive?.key
    ?? executive?.name
    ?? null
  );
}


function getExecutiveAliases(executive) {
  const aliases = [
    executive?.id,
    executive?.key,
    executive?.name,
    executive?.department,
  ]
    .map(normalizeName)
    .filter(Boolean);

  const combined = aliases.join(" ");

  if (
    combined.includes("ceo")
    || combined.includes("executive")
  ) {
    aliases.push("ceo");
  }

  if (combined.includes("sales")) {
    aliases.push("sales");
  }

  if (combined.includes("marketing")) {
    aliases.push("marketing");
  }

  if (combined.includes("finance")) {
    aliases.push("finance");
  }

  if (
    combined.includes("reception")
    || combined.includes("operations")
  ) {
    aliases.push(
      "reception",
      "operations",
      "follow-up",
      "follow up",
      "research",
      "analytics",
      "quality control",
    );
  }

  return [...new Set(aliases)];
}


function matchesExecutive(
  executive,
  incomingExecutive,
) {
  const incomingName = normalizeName(
    incomingExecutive,
  );

  if (!incomingName) {
    return false;
  }

  return getExecutiveAliases(executive).some(
    (alias) =>
      alias === incomingName
      || alias.includes(incomingName)
      || incomingName.includes(alias),
  );
}


function normalizeExecutive(executive) {
  const status = normalizeName(
    executive?.status ?? "idle",
  );

  if (
    status === "idle"
    || status === "completed"
  ) {
    return {
      ...executive,
      status: "idle",
      task: "",
      current_task: "",
      progress: 0,
      mission_uid: null,
    };
  }

  return {
    ...executive,
    progress:
      Number(executive?.progress)
      || 0,
  };
}


function mergeWorkforceUpdate(
  executive,
  updatedExecutive,
) {
  const status = normalizeName(
    updatedExecutive?.status,
  );

  if (
    status === "idle"
    || status === "completed"
  ) {
    return {
      ...executive,
      ...updatedExecutive,
      status: "idle",
      task: "",
      current_task: "",
      progress: 0,
      mission_uid: null,
    };
  }

  return {
    ...executive,
    ...updatedExecutive,
    task:
      updatedExecutive?.task
      ?? updatedExecutive?.current_task
      ?? executive?.task
      ?? executive?.current_task
      ?? "",
    current_task:
      updatedExecutive?.current_task
      ?? updatedExecutive?.task
      ?? executive?.current_task
      ?? executive?.task
      ?? "",
    progress:
      Number(updatedExecutive?.progress)
      || 0,
  };
}


function applyMissionEvent(
  executive,
  event,
) {
  const eventType = normalizeName(
    event?.event_type,
  );

  const eventStatus = normalizeName(
    event?.status,
  );

  const isStarted =
    eventType.includes("started")
    || eventStatus === "running";

  const isCompleted =
    eventType.includes("completed")
    || eventStatus === "completed";

  const isFailed =
    eventType.includes("failed")
    || eventStatus === "failed";

  const isBlocked =
    eventType.includes("blocked")
    || eventStatus === "blocked";

  if (isFailed) {
    const taskMessage =
      event?.message
      ?? event?.title
      ?? "Task failed.";

    return {
      ...executive,
      status: "error",
      progress: 0,
      task: taskMessage,
      current_task: taskMessage,
      mission_uid:
        event?.mission_uid
        ?? null,
      event_type:
        event?.event_type
        ?? null,
      updated_at:
        event?.created_at
        ?? new Date().toISOString(),
    };
  }

  if (isBlocked) {
    const taskMessage =
      event?.message
      ?? "Waiting for input.";

    return {
      ...executive,
      status: "waiting",
      task: taskMessage,
      current_task: taskMessage,
      mission_uid:
        event?.mission_uid
        ?? null,
      event_type:
        event?.event_type
        ?? null,
      updated_at:
        event?.created_at
        ?? new Date().toISOString(),
    };
  }

  if (isCompleted) {
    return {
      ...executive,
      status: "idle",
      progress: 0,
      task: "",
      current_task: "",
      mission_uid: null,
      event_type:
        event?.event_type
        ?? null,
      updated_at:
        event?.created_at
        ?? new Date().toISOString(),
    };
  }

  if (isStarted) {
    const taskMessage =
      event?.message
      ?? event?.title
      ?? "Working on mission task...";

    return {
      ...executive,
      status: "working",
      progress: 25,
      task: taskMessage,
      current_task: taskMessage,
      mission_uid:
        event?.mission_uid
        ?? null,
      event_type:
        event?.event_type
        ?? null,
      updated_at:
        event?.created_at
        ?? new Date().toISOString(),
    };
  }

  return executive;
}


function calculateSummary(executives) {
  const summary = {
    total: executives.length,
    active: 0,
    idle: 0,
    waiting: 0,
    error: 0,
  };

  executives.forEach((executive) => {
    const status = normalizeName(
      executive?.status ?? "idle",
    );

    if (
      status === "working"
      || status === "running"
      || status === "thinking"
    ) {
      summary.active += 1;
      return;
    }

    if (
      status === "waiting"
      || status === "paused"
      || status === "blocked"
    ) {
      summary.waiting += 1;
      return;
    }

    if (
      status === "error"
      || status === "failed"
      || status === "offline"
    ) {
      summary.error += 1;
      return;
    }

    summary.idle += 1;
  });

  return summary;
}


let socketInitialized = false;
let socketUnsubscribe = null;
let activeBusinessUid = null;


export const useWorkforceStore = create(
  (set, get) => ({
    executives: [],
    connectionStatus: "connecting",
    lastEventAt: null,

    initialize: (businessUid) => {
      const cleanBusinessUid = String(
        businessUid || "",
      ).trim();

      if (
        socketInitialized
        && activeBusinessUid
          === cleanBusinessUid
      ) {
        return;
      }

      if (socketUnsubscribe) {
        socketUnsubscribe();
        socketUnsubscribe = null;
      }

      workforceSocket.disconnect();
      socketInitialized = false;
      activeBusinessUid = cleanBusinessUid || null;

      set({
        executives: [],
        connectionStatus:
          cleanBusinessUid
            ? "connecting"
            : "offline",
        lastEventAt: null,
      });

      if (!cleanBusinessUid) {
        return;
      }

      socketInitialized = true;

      socketUnsubscribe =
        workforceSocket.subscribe((message) => {
          if (
            !message
            || typeof message !== "object"
          ) {
            return;
          }

          if (
            message.event === "socket.connected"
          ) {
            set({
              connectionStatus: "connected",
            });

            return;
          }

          if (
            message.event ===
            "socket.disconnected"
          ) {
            set({
              connectionStatus: "reconnecting",
            });

            return;
          }

          if (
            message.event ===
            "workforce.snapshot"
          ) {
            const executives =
              Array.isArray(message.data)
                ? message.data.map(
                    normalizeExecutive,
                  )
                : [];

            set({
              executives,
              connectionStatus: "connected",
              lastEventAt:
                message.timestamp
                ?? new Date().toISOString(),
            });

            return;
          }

          if (
            message.event ===
            "workforce.updated"
          ) {
            const updatedExecutive =
              message.data;

            const updatedKey =
              getExecutiveKey(
                updatedExecutive,
              );

            if (!updatedKey) {
              return;
            }

            set((state) => {
              const existingIndex =
                state.executives.findIndex(
                  (executive) =>
                    getExecutiveKey(
                      executive,
                    ) === updatedKey,
                );

              if (existingIndex === -1) {
                return {
                  executives: [
                    ...state.executives,
                    normalizeExecutive(
                      updatedExecutive,
                    ),
                  ],
                  connectionStatus:
                    "connected",
                  lastEventAt:
                    message.timestamp
                    ?? new Date().toISOString(),
                };
              }

              return {
                executives:
                  state.executives.map(
                    (executive, index) =>
                      index === existingIndex
                        ? mergeWorkforceUpdate(
                            executive,
                            updatedExecutive,
                          )
                        : executive,
                  ),
                connectionStatus:
                  "connected",
                lastEventAt:
                  message.timestamp
                  ?? new Date().toISOString(),
              };
            });

            return;
          }

          if (
            message.event === "mission.event"
            && message.data
          ) {
            const event = message.data;

            set((state) => ({
              executives:
                state.executives.map(
                  (executive) => {
                    if (
                      !matchesExecutive(
                        executive,
                        event.executive,
                      )
                    ) {
                      return executive;
                    }

                    return applyMissionEvent(
                      executive,
                      event,
                    );
                  },
                ),
              connectionStatus: "connected",
              lastEventAt:
                message.timestamp
                ?? event.created_at
                ?? new Date().toISOString(),
            }));

            return;
          }

          if (message.event === "pong") {
            set({
              connectionStatus: "connected",
              lastEventAt:
                message.timestamp
                ?? new Date().toISOString(),
            });
          }
        });

      workforceSocket.connect();
    },

    reset: () => {
      set({
        executives: [],
        connectionStatus: "connecting",
        lastEventAt: null,
      });
    },

    disconnect: () => {
      if (socketUnsubscribe) {
        socketUnsubscribe();
        socketUnsubscribe = null;
      }

      workforceSocket.disconnect();
      socketInitialized = false;
      activeBusinessUid = null;

      set({
        connectionStatus: "offline",
      });
    },

    getSummary: () =>
      calculateSummary(
        get().executives,
      ),
  }),
);


export function selectWorkforceSummary(state) {
  return calculateSummary(
    state.executives,
  );
}
