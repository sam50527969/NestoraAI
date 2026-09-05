import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  clearActiveBusinessUid,
  setActiveBusinessUid,
} from "../../workspace/session";
import { generateOutreach } from "../outreach";

afterEach(() => {
  clearActiveBusinessUid();
  vi.unstubAllGlobals();
});

function successfulFetch(data = {}) {
  return vi.fn(async () => ({
    ok: true,
    json: async () => data,
  }));
}

describe("outreach API", () => {
  it("uses the active workspace and does not invent a priced offer", async () => {
    setActiveBusinessUid("biz_atlas");

    const fetchMock = successfulFetch({
      email_subject: "Atlas outreach",
    });

    vi.stubGlobal("fetch", fetchMock);

    await generateOutreach({
      name: "Atlas Auto Care",
      category: "auto repair",
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);

    const [, options] = fetchMock.mock.calls[0];

    expect(options.headers).toEqual(
      expect.objectContaining({
        "X-Business-Uid": "biz_atlas",
      }),
    );

    const payload = JSON.parse(options.body);

    expect(payload).toEqual({
      lead: {
        name: "Atlas Auto Care",
        category: "auto repair",
      },
    });

    expect(payload.offer).toBeUndefined();

    const serialized = JSON.stringify(payload);

    expect(serialized).not.toContain("99 QAR");
    expect(serialized).not.toContain("99 AED");
    expect(serialized).not.toContain("99 USD");
  });
});
