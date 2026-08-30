import {
  useEffect,
  useMemo,
} from "react";

import {
  useWorkforceStore,
} from "../store/workforceStore";
import useWorkspace from "../workspace/useWorkspace";


function normalizeName(value) {
  return String(value ?? "")
    .trim()
    .toLowerCase();
}


export default function useWorkforce() {
  const { activeWorkspace } = useWorkspace();
  const activeBusinessUid =
    activeWorkspace?.business_uid || "";
  const executives = useWorkforceStore(
    (state) => state.executives,
  );

  const connectionStatus = useWorkforceStore(
    (state) => state.connectionStatus,
  );

  const lastEventAt = useWorkforceStore(
    (state) => state.lastEventAt,
  );

  const initialize = useWorkforceStore(
    (state) => state.initialize,
  );

  useEffect(() => {
    initialize(activeBusinessUid);
  }, [activeBusinessUid, initialize]);

  const workforceSummary = useMemo(() => {
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
  }, [executives]);

  return {
    executives,
    connectionStatus,
    lastEventAt,
    workforceSummary,
  };
}
