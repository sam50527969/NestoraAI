import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  clearAccessToken,
  setAccessToken,
} from "../../auth/session";
import {
  clearActiveBusinessUid,
  setActiveBusinessUid,
} from "../../workspace/session";
import { createObjectiveMission } from "../ceo";
import { executePersistedMission } from "../mission";

afterEach(() => {
  clearAccessToken();
  clearActiveBusinessUid();
  vi.unstubAllGlobals();
});

function successfulFetch(data = {}) {
  return vi.fn(async () => ({
    ok: true,
    json: async () => data,
  }));
}

describe("CEO and mission workspace requests", () => {
  it("uses the active workspace header instead of payload identity", async () => {
    setAccessToken("access-token");
    setActiveBusinessUid("biz_active");
    const fetchMock = successfulFetch();
    vi.stubGlobal("fetch", fetchMock);

    await createObjectiveMission({
      objective: "Grow qualified revenue",
    });

    const [, options] = fetchMock.mock.calls[0];
    expect(options.headers).toEqual(
      expect.objectContaining({
        Authorization: "Bearer access-token",
        "X-Business-Uid": "biz_active",
      }),
    );
    expect(JSON.parse(options.body)).toEqual({
      objective: "Grow qualified revenue",
    });
  });

  it("executes missions through the shared workspace client", async () => {
    setActiveBusinessUid("biz_active");
    const fetchMock = successfulFetch({
      status: "completed",
    });
    vi.stubGlobal("fetch", fetchMock);

    await executePersistedMission("mis_123");

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        "/missions/mis_123/execute",
      ),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "X-Business-Uid": "biz_active",
        }),
      }),
    );
  });
});
