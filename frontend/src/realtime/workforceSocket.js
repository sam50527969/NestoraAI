const WS_URL = "ws://127.0.0.1:8000/realtime/workforce";

class WorkforceSocket {
    constructor() {
        this.socket = null;
        this.listeners = new Set();
        this.connected = false;
        this.reconnectTimer = null;
        this.heartbeat = null;
    }

    connect() {
        if (
            this.socket &&
            (
                this.socket.readyState === WebSocket.OPEN ||
                this.socket.readyState === WebSocket.CONNECTING
            )
        ) {
            return;
        }

        this.socket = new WebSocket(WS_URL);

        this.socket.onopen = () => {
            console.log("✅ Workforce WebSocket connected");

            this.connected = true;

            this.notify({
                event: "socket.connected",
            });

            this.startHeartbeat();
        };

        this.socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);

                this.notify(message);

            } catch (err) {
                console.error(
                    "Realtime message error",
                    err,
                );
            }
        };

        this.socket.onerror = (err) => {
            console.error(err);
        };

        this.socket.onclose = () => {
            console.log(
                "❌ Workforce WebSocket disconnected",
            );

            this.connected = false;

            this.notify({
                event: "socket.disconnected",
            });

            this.stopHeartbeat();

            this.scheduleReconnect();
        };
    }

    notify(message) {
        this.listeners.forEach((listener) => {
            listener(message);
        });
    }

    scheduleReconnect() {
        if (this.reconnectTimer) return;

        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
        }, 3000);
    }

    startHeartbeat() {
        this.stopHeartbeat();

        this.heartbeat = setInterval(() => {
            if (
                this.socket &&
                this.socket.readyState === WebSocket.OPEN
            ) {
                this.socket.send("ping");
            }
        }, 30000);
    }

    stopHeartbeat() {
        if (this.heartbeat) {
            clearInterval(this.heartbeat);
            this.heartbeat = null;
        }
    }

    subscribe(listener) {
        this.listeners.add(listener);

        return () => {
            this.listeners.delete(listener);
        };
    }

    disconnect() {
        this.stopHeartbeat();

        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }

        this.connected = false;
    }
}

export default new WorkforceSocket();