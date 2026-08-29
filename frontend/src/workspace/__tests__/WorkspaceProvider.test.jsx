import {
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  getWorkspaces,
} from "../../api/workspaces";
import AuthContext from "../../auth/AuthContext";

import WorkspaceProvider from "../WorkspaceProvider";
import useWorkspace from "../useWorkspace";

vi.mock("../../api/workspaces", () => ({
  getWorkspaces: vi.fn(),
}));

const user = {
  user_uid: "usr_workspace",
  email: "owner@example.com",
};

const businesses = [
  {
    business_uid: "biz_first",
    name: "First Business",
    industry: "other",
    country: "Australia",
  },
  {
    business_uid: "biz_second",
    name: "Second Business",
    industry: "technology",
    country: "Canada",
  },
];

function WorkspaceProbe() {
  const {
    workspaces,
    activeBusinessUid,
    isLoading,
    error,
    selectWorkspace,
  } = useWorkspace();

  return (
    <div>
      <div data-testid="loading">
        {String(isLoading)}
      </div>

      <div data-testid="count">
        {workspaces.length}
      </div>

      <div data-testid="active">
        {activeBusinessUid || "none"}
      </div>

      <div data-testid="error">
        {error?.message || "none"}
      </div>

      <button
        type="button"
        onClick={() => {
          selectWorkspace(
            "biz_second",
          );
        }}
      >
        Select second
      </button>
    </div>
  );
}

function renderProvider() {
  return render(
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: true,
      }}
    >
      <WorkspaceProvider>
        <WorkspaceProbe />
      </WorkspaceProvider>
    </AuthContext.Provider>,
  );
}

beforeEach(() => {
  window.localStorage.clear();
  getWorkspaces.mockReset();
});

afterEach(() => {
  window.localStorage.clear();
  vi.clearAllMocks();
});

describe("WorkspaceProvider", () => {
  it("selects the first accessible workspace", async () => {
    getWorkspaces.mockResolvedValue({
      businesses,
      count: 2,
    });

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId("active"),
      ).toHaveTextContent(
        "biz_first",
      );
    });

    expect(
      screen.getByTestId("count"),
    ).toHaveTextContent("2");
  });

  it("restores a valid persisted workspace", async () => {
    window.localStorage.setItem(
      "nestora.active_workspace.usr_workspace",
      "biz_second",
    );

    getWorkspaces.mockResolvedValue({
      businesses,
      count: 2,
    });

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId("active"),
      ).toHaveTextContent(
        "biz_second",
      );
    });
  });

  it("replaces an inaccessible persisted workspace", async () => {
    window.localStorage.setItem(
      "nestora.active_workspace.usr_workspace",
      "biz_forbidden",
    );

    getWorkspaces.mockResolvedValue({
      businesses,
      count: 2,
    });

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId("active"),
      ).toHaveTextContent(
        "biz_first",
      );
    });

    expect(
      window.localStorage.getItem(
        "nestora.active_workspace.usr_workspace",
      ),
    ).toBe("biz_first");
  });

  it("persists an explicit workspace switch", async () => {
    getWorkspaces.mockResolvedValue({
      businesses,
      count: 2,
    });

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId("active"),
      ).toHaveTextContent(
        "biz_first",
      );
    });

    fireEvent.click(
      screen.getByRole(
        "button",
        {
          name: "Select second",
        },
      ),
    );

    expect(
      screen.getByTestId("active"),
    ).toHaveTextContent(
      "biz_second",
    );

    expect(
      window.localStorage.getItem(
        "nestora.active_workspace.usr_workspace",
      ),
    ).toBe("biz_second");
  });

  it("handles users without workspaces", async () => {
    getWorkspaces.mockResolvedValue({
      businesses: [],
      count: 0,
    });

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId("loading"),
      ).toHaveTextContent("false");
    });

    expect(
      screen.getByTestId("count"),
    ).toHaveTextContent("0");

    expect(
      screen.getByTestId("active"),
    ).toHaveTextContent("none");
  });

  it("exposes workspace loading failures", async () => {
    getWorkspaces.mockRejectedValue(
      new Error("Backend unavailable"),
    );

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId("error"),
      ).toHaveTextContent(
        "Backend unavailable",
      );
    });
  });
});
