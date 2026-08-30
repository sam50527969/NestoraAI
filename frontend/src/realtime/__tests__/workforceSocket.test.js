import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  clearAccessToken,
  setAccessToken,
} from "../../auth/session";
import workforceSocket from "../workforceSocket";
import {
  clearActiveBusinessUid,
  setActiveBusinessUid,
} from "../../workspace/session";


class FakeWebSocket {
  static OPEN = 1;
  static CONNECTING = 0;
  static instances = [];

  constructor(url) {
    this.url = url;
    this.readyState = FakeWebSocket.CONNECTING;
    this.sent = [];
    this.closed = false;
    FakeWebSocket.instances.push(this);
  }

  send(value) {
    this.sent.push(value);
  }

  close() {
    this.closed = true;
    this.readyState = 3;
  }

  open() {
    this.readyState = FakeWebSocket.OPEN;
    this.onopen?.();
  }
}


beforeEach(() => {
  FakeWebSocket.instances = [];
  vi.stubGlobal("WebSocket", FakeWebSocket);
});

afterEach(() => {
  workforceSocket.disconnect();
  clearAccessToken();
  clearActiveBusinessUid();
  vi.unstubAllGlobals();
});


describe("workforce workspace socket", () => {
  it("authenticates with the active workspace", () => {
    setAccessToken("access-token");
    setActiveBusinessUid("biz_one");

    workforceSocket.connect();
    const socket = FakeWebSocket.instances[0];
    socket.open();

    expect(JSON.parse(socket.sent[0])).toEqual({
      event: "socket.authenticate",
      token: "access-token",
      business_uid: "biz_one",
    });
  });

  it("reconnects when the active workspace changes", () => {
    setAccessToken("access-token");
    setActiveBusinessUid("biz_one");
    workforceSocket.connect();
    const first = FakeWebSocket.instances[0];

    setActiveBusinessUid("biz_two");
    workforceSocket.connect();

    expect(first.closed).toBe(true);
    expect(FakeWebSocket.instances).toHaveLength(2);

    const second = FakeWebSocket.instances[1];
    second.open();
    expect(
      JSON.parse(second.sent[0]).business_uid,
    ).toBe("biz_two");
  });
});
