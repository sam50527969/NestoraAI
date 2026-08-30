import {
  API_BASE_URL,
} from "../api/client";

import {
  getAccessToken,
} from "../auth/session";
import {
  getActiveBusinessUid,
} from "../workspace/session";

const WS_URL = (
  API_BASE_URL
    .replace(
      /^http/,
      "ws",
    )
    .replace(
      /\/+$/,
      "",
    )
  + "/realtime/workforce"
);

class WorkforceSocket {
  constructor() {
    this.socket = null;
    this.listeners = new Set();
    this.connected = false;
    this.reconnectTimer = null;
    this.heartbeat = null;
    this.manuallyClosed = false;
    this.businessUid = null;
  }

  connect() {
    const token = getAccessToken();
    const businessUid = getActiveBusinessUid();

    if (!token || !businessUid) {
      this.notify({
        event:
          "socket.authentication_required",
      });

      return;
    }

    if (
      this.socket
      && this.businessUid !== businessUid
    ) {
      this.disconnect();
    }

    if (
      this.socket &&
      (
        this.socket.readyState
          === WebSocket.OPEN ||
        this.socket.readyState
          === WebSocket.CONNECTING
      )
    ) {
      return;
    }

    this.manuallyClosed = false;
    this.businessUid = businessUid;

    this.socket = new WebSocket(
      WS_URL
    );

    this.socket.onopen = () => {
      const currentToken =
        getAccessToken();
      const currentBusinessUid =
        getActiveBusinessUid();

      if (
        !currentToken
        || !currentBusinessUid
        || currentBusinessUid
          !== this.businessUid
      ) {
        this.socket.close(
          4401,
          "Authentication required",
        );

        return;
      }

      this.socket.send(
        JSON.stringify({
          event:
            "socket.authenticate",
          token: currentToken,
          business_uid:
            currentBusinessUid,
        }),
      );
    };

    this.socket.onmessage = (
      event,
    ) => {
      try {
        const message = JSON.parse(
          event.data
        );

        if (
          message.event
          === "socket.authenticated"
        ) {
          this.connected = true;

          this.notify({
            event:
              "socket.connected",
          });

          this.startHeartbeat();

          return;
        }

        this.notify(message);
      } catch (error) {
        console.error(
          "Realtime message error",
          error,
        );
      }
    };

    this.socket.onerror = (
      error,
    ) => {
      console.error(
        "Workforce WebSocket error",
        error,
      );
    };

    this.socket.onclose = (
      event,
    ) => {
      this.connected = false;
      this.socket = null;

      this.stopHeartbeat();

      if (event.code === 4401) {
        this.notify({
          event:
            "socket.unauthorized",
        });

        return;
      }

      this.notify({
        event:
          "socket.disconnected",
      });

      if (!this.manuallyClosed) {
        this.scheduleReconnect();
      }
    };
  }

  notify(message) {
    this.listeners.forEach(
      (listener) => {
        listener(message);
      },
    );
  }

  scheduleReconnect() {
    if (
      this.reconnectTimer ||
      !getAccessToken()
    ) {
      return;
    }

    this.reconnectTimer =
      setTimeout(() => {
        this.reconnectTimer = null;
        this.connect();
      }, 3000);
  }

  startHeartbeat() {
    this.stopHeartbeat();

    this.heartbeat =
      setInterval(() => {
        if (
          this.socket &&
          this.socket.readyState
            === WebSocket.OPEN &&
          this.connected
        ) {
          this.socket.send(
            "ping"
          );
        }
      }, 30000);
  }

  stopHeartbeat() {
    if (this.heartbeat) {
      clearInterval(
        this.heartbeat
      );

      this.heartbeat = null;
    }
  }

  subscribe(listener) {
    this.listeners.add(
      listener
    );

    return () => {
      this.listeners.delete(
        listener
      );
    };
  }

  disconnect() {
    this.manuallyClosed = true;

    if (this.reconnectTimer) {
      clearTimeout(
        this.reconnectTimer
      );

      this.reconnectTimer = null;
    }

    this.stopHeartbeat();

    if (this.socket) {
      const socket = this.socket;
      this.socket = null;
      socket.onopen = null;
      socket.onmessage = null;
      socket.onerror = null;
      socket.onclose = null;
      socket.close();
    }

    this.connected = false;
    this.businessUid = null;
  }
}

export default new WorkforceSocket();
