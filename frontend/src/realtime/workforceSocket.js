import {
  API_BASE_URL,
} from "../api/client";

import {
  getAccessToken,
} from "../auth/session";

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
  }

  connect() {
    const token = getAccessToken();

    if (!token) {
      this.notify({
        event:
          "socket.authentication_required",
      });

      return;
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

    this.socket = new WebSocket(
      WS_URL
    );

    this.socket.onopen = () => {
      const currentToken =
        getAccessToken();

      if (!currentToken) {
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
      this.socket.close();
      this.socket = null;
    }

    this.connected = false;
  }
}

export default new WorkforceSocket();