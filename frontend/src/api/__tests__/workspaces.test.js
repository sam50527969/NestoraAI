import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  request,
} from "../client";
import {
  getWorkspaces,
} from "../workspaces";

vi.mock("../client", () => ({
  request: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

describe("getWorkspaces", () => {
  it("loads authenticated business workspaces", async () => {
    request.mockResolvedValue({
      businesses: [
        {
          business_uid: "biz_one",
          name: "First Business",
        },
      ],
      offset: 0,
      limit: 100,
      count: 1,
    });

    const response =
      await getWorkspaces();

    expect(request).toHaveBeenCalledWith(
      "/businesses?offset=0&limit=100",
    );

    expect(
      response.businesses[0]
        .business_uid,
    ).toBe("biz_one");
  });

  it("preserves an empty workspace response", async () => {
    request.mockResolvedValue({
      businesses: [],
      offset: 0,
      limit: 100,
      count: 0,
    });

    const response =
      await getWorkspaces();

    expect(response.businesses).toEqual(
      [],
    );
    expect(response.count).toBe(0);
  });
});
