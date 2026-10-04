import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import AdminExplorer from "../AdminExplorer";
import { clearAccessToken, setAccessToken } from "../../auth/session";
import { clearActiveBusinessUid, setActiveBusinessUid } from "../../workspace/session";

const workspace = vi.hoisted(() => ({ activeBusinessUid: "biz_a" }));
vi.mock("../../workspace/useWorkspace", () => ({ default: () => workspace }));
afterEach(() => {
  cleanup(); clearAccessToken(); clearActiveBusinessUid(); vi.unstubAllGlobals();
  workspace.activeBusinessUid = "biz_a";
});
const mission = { mission_uid: "mis_a", title: "Workspace A mission", status: "planned", priority: "medium", progress: 0 };

describe("Admin Explorer authenticated workspace records", () => {
  it("loads missions and tasks with the authenticated workspace headers", async () => {
    setAccessToken("synthetic-token"); setActiveBusinessUid("biz_a");
    const fetchMock = vi.fn(async (url) => ({ ok: true, json: async () =>
      url.endsWith("/tasks") ? { tasks: [] } : { missions: [mission] } }));
    vi.stubGlobal("fetch", fetchMock);
    render(<AdminExplorer />);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    for (const [, options] of fetchMock.mock.calls) {
      expect(options.headers).toEqual(expect.objectContaining({
        Authorization: "Bearer synthetic-token", "X-Business-Uid": "biz_a",
      }));
    }
    expect(fetchMock.mock.calls[1][0]).toContain("/missions/mis_a/tasks");
  });
  it("clears previous workspace records immediately and reloads after switching", async () => {
    setActiveBusinessUid("biz_a");
    vi.stubGlobal("fetch", vi.fn(async (url, options) => ({ ok: true, json: async () =>
      url.endsWith("/tasks") ? { tasks: [] } : {
        missions: options.headers["X-Business-Uid"] === "biz_a" ? [mission] : [],
      } })));
    const { rerender } = render(<AdminExplorer />);
    await screen.findAllByText("Workspace A mission");
    workspace.activeBusinessUid = "biz_b"; setActiveBusinessUid("biz_b");
    rerender(<AdminExplorer />);
    expect(screen.queryByText("Workspace A mission")).toBeNull();
    await screen.findByText("No persisted missions");
  });
  it("shows a recoverable request error without retaining records", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: false, text: async () => "Service unavailable" })));
    render(<AdminExplorer />);
    await screen.findByText("Service unavailable");
    expect(screen.getByRole("button", { name: "Refresh" })).toBeTruthy();
    expect(screen.queryByText("Workspace A mission")).toBeNull();
  });
});
