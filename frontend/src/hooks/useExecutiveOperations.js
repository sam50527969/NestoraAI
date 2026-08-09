import { useCallback, useEffect, useMemo, useState } from "react";
import { getExecutiveInbox, getExecutiveOutbox } from "../api";
import useWorkforce from "./useWorkforce";

const CONVERSATION_REFRESH_MS = 15000;

function normalizeStatus(value) {
  return String(value || "idle").trim().toLowerCase();
}

function normalizeExecutive(executive, index) {
  const status = normalizeStatus(executive?.status);
  const progressValue = Number(executive?.progress);
  return {
    id: executive?.id ?? executive?.key ?? executive?.name ?? `executive-${index}`,
    name: executive?.name || "AI Executive",
    department: executive?.department || "Executive Operations",
    status,
    currentTask: executive?.current_task || executive?.task || "Waiting for assignment...",
    progress: Number.isFinite(progressValue) ? Math.min(Math.max(progressValue, 0), 100) : 0,
    missionsToday: Number(executive?.missions_today) || 0,
    successRate: Number(executive?.success_rate) || 0,
    missionUid: executive?.mission_uid || null,
    eventType: executive?.event_type || null,
    updatedAt: executive?.updated_at || null,
  };
}

function getMessageKey(message) {
  return message?.message_uid ?? message?.id ?? [
    message?.sender,
    message?.recipient,
    message?.created_at,
    message?.subject,
  ].join(":");
}

function mergeMessages(...groups) {
  const map = new Map();
  groups.flat().filter(Boolean).forEach((message) => {
    map.set(getMessageKey(message), message);
  });
  return Array.from(map.values())
    .sort((a, b) => new Date(b?.created_at || 0).getTime() - new Date(a?.created_at || 0).getTime())
    .slice(0, 30);
}

export default function useExecutiveOperations() {
  const {
    executives: workforceExecutives,
    connectionStatus,
    lastEventAt,
    workforceSummary,
  } = useWorkforce();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [isMessagesLoading, setIsMessagesLoading] = useState(true);
  const [isMessagesRefreshing, setIsMessagesRefreshing] = useState(false);
  const [messagesError, setMessagesError] = useState("");

  const executives = useMemo(
    () => workforceExecutives.map(normalizeExecutive),
    [workforceExecutives],
  );

  const operationsSummary = useMemo(() => {
    const active = executives.filter((e) =>
      ["working", "running", "thinking", "executing", "reviewing"].includes(e.status)
    ).length;
    const waiting = executives.filter((e) =>
      ["waiting", "paused", "blocked"].includes(e.status)
    ).length;
    const issues = executives.filter((e) =>
      ["error", "failed", "offline"].includes(e.status)
    ).length;
    const completedToday = executives.reduce((total, e) => total + e.missionsToday, 0);
    return {
      total: workforceSummary?.total ?? executives.length,
      active: workforceSummary?.active ?? active,
      idle: workforceSummary?.idle ?? executives.filter((e) => e.status === "idle").length,
      waiting: workforceSummary?.waiting ?? waiting,
      issues: workforceSummary?.error ?? issues,
      completedToday,
    };
  }, [executives, workforceSummary]);

  const activeExecutives = useMemo(
    () => executives.filter((e) =>
      ["working", "running", "thinking", "executing", "reviewing"].includes(e.status)
    ),
    [executives],
  );

  const loadMessages = useCallback(async ({ initial = false, refreshing = false } = {}) => {
    if (initial) setIsMessagesLoading(true);
    if (refreshing) setIsMessagesRefreshing(true);
    setMessagesError("");
    try {
      const [inboxResponse, outboxResponse] = await Promise.all([
        getExecutiveInbox("CEO", { limit: 30 }),
        getExecutiveOutbox("CEO", { limit: 30 }),
      ]);
      setMessages(
        mergeMessages(
          Array.isArray(inboxResponse?.messages) ? inboxResponse.messages : [],
          Array.isArray(outboxResponse?.messages) ? outboxResponse.messages : [],
        ),
      );
    } catch (error) {
      console.error("Executive conversation loading failed:", error);
      setMessagesError(error?.message || "Unable to load executive conversations.");
    } finally {
      setIsMessagesLoading(false);
      setIsMessagesRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadMessages({ initial: true });
    const intervalId = window.setInterval(() => loadMessages(), CONVERSATION_REFRESH_MS);
    return () => window.clearInterval(intervalId);
  }, [loadMessages]);

  const refresh = useCallback(async () => {
    setIsRefreshing(true);
    setErrorMessage("");
    try {
      await loadMessages({ refreshing: true });
    } catch (error) {
      console.error("Executive operations refresh failed:", error);
      setErrorMessage(error?.message || "Unable to refresh executive operations.");
    } finally {
      setIsRefreshing(false);
    }
  }, [loadMessages]);

  const refreshMessages = useCallback(
    () => loadMessages({ refreshing: true }),
    [loadMessages],
  );

  return {
    executives,
    activeExecutives,
    operationsSummary,
    connectionStatus,
    isConnected: connectionStatus === "connected",
    isLoading: connectionStatus === "connecting" && executives.length === 0,
    isRefreshing,
    lastEventAt,
    errorMessage,
    refresh,
    messages,
    isMessagesLoading,
    isMessagesRefreshing,
    messagesError,
    refreshMessages,
  };
}
