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
  createWorkspace,
  getWorkspaces,
  updateWorkspace,
} from "../workspaces";

vi.mock("../client", () => ({
  request: vi.fn(),
}));

afterEach(() => {
  vi.clearAllMocks();
});

describe("workspace API", () => {
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

  it("creates an authenticated workspace", async () => {
    request.mockResolvedValue({
      business_uid: "biz_created",
    });

    const payload = {
      name: "Created Business",
    };

    await createWorkspace(payload);

    expect(request).toHaveBeenCalledWith(
      "/businesses",
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  });

  it("updates an authenticated workspace", async () => {
    request.mockResolvedValue({
      business_uid: "biz_updated",
    });

    const payload = {
      name: "Updated Business",
    };

    await updateWorkspace(
      "biz_updated",
      payload,
    );

    expect(request).toHaveBeenCalledWith(
      "/businesses/biz_updated",
      {
        method: "PUT",
        body: JSON.stringify(payload),
      },
    );
  });
});
