import {
  render,
  screen,
} from "@testing-library/react";
import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router-dom";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import ProtectedRoute from "../ProtectedRoute";
import useAuth from "../useAuth";

vi.mock("../useAuth", () => ({
  default: vi.fn(),
}));

function renderRoutes() {
  return render(
    <MemoryRouter
      initialEntries={["/crm"]}
    >
      <Routes>
        <Route
          path="/login"
          element={
            <div>Login page</div>
          }
        />

        <Route
          element={
            <ProtectedRoute />
          }
        >
          <Route
            path="/crm"
            element={
              <div>Protected CRM</div>
            }
          />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  useAuth.mockReset();
});

describe("ProtectedRoute", () => {
  it("shows a loading state while restoring a session", () => {
    useAuth.mockReturnValue({
      isLoading: true,
      isAuthenticated: false,
    });

    renderRoutes();

    expect(
      screen.getByText(
        "Restoring your Nestora session...",
      ),
    ).toBeInTheDocument();
  });

  it("redirects signed-out users to login", () => {
    useAuth.mockReturnValue({
      isLoading: false,
      isAuthenticated: false,
    });

    renderRoutes();

    expect(
      screen.getByText(
        "Login page",
      ),
    ).toBeInTheDocument();

    expect(
      screen.queryByText(
        "Protected CRM",
      ),
    ).not.toBeInTheDocument();
  });

  it("renders protected content for an authenticated user", () => {
    useAuth.mockReturnValue({
      isLoading: false,
      isAuthenticated: true,
    });

    renderRoutes();

    expect(
      screen.getByText(
        "Protected CRM",
      ),
    ).toBeInTheDocument();
  });
});