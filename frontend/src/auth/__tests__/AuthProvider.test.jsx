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
  getCurrentAccount,
  loginAccount,
  registerAccount,
} from "../../api";

import AuthProvider from "../AuthProvider";
import useAuth from "../useAuth";

vi.mock("../../api", () => ({
  getCurrentAccount: vi.fn(),
  loginAccount: vi.fn(),
  registerAccount: vi.fn(),
}));

const testUser = {
  user_uid: "usr_test123",
  email: "sam@example.com",
  full_name: "Sam",
  role: "user",
  is_active: true,
};

function AuthenticationProbe() {
  const {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
  } = useAuth();

  return (
    <div>
      <div data-testid="loading">
        {String(isLoading)}
      </div>

      <div data-testid="authenticated">
        {String(isAuthenticated)}
      </div>

      <div data-testid="email">
        {user?.email || "none"}
      </div>

      <button
        type="button"
        onClick={() => {
          login({
            email: "sam@example.com",
            password: "Password123!",
          });
        }}
      >
        Log in
      </button>

      <button
        type="button"
        onClick={() => {
          register({
            email: "sam@example.com",
            full_name: "Sam",
            password: "Password123!",
          });
        }}
      >
        Register
      </button>

      <button
        type="button"
        onClick={logout}
      >
        Log out
      </button>
    </div>
  );
}

function renderProvider() {
  return render(
    <AuthProvider>
      <AuthenticationProbe />
    </AuthProvider>,
  );
}

beforeEach(() => {
  window.sessionStorage.clear();

  getCurrentAccount.mockReset();
  loginAccount.mockReset();
  registerAccount.mockReset();
});

afterEach(() => {
  window.sessionStorage.clear();
  vi.clearAllMocks();
});

describe("AuthProvider", () => {
  it("starts unauthenticated without a stored token", () => {
    renderProvider();

    expect(
      screen.getByTestId(
        "loading",
      ),
    ).toHaveTextContent(
      "false",
    );

    expect(
      screen.getByTestId(
        "authenticated",
      ),
    ).toHaveTextContent(
      "false",
    );

    expect(
      screen.getByTestId(
        "email",
      ),
    ).toHaveTextContent(
      "none",
    );

    expect(
      getCurrentAccount,
    ).not.toHaveBeenCalled();
  });

  it("restores a valid stored session", async () => {
    window.sessionStorage.setItem(
      "nestora.access_token",
      "stored-token",
    );

    getCurrentAccount.mockResolvedValue(
      testUser,
    );

    renderProvider();

    expect(
      screen.getByTestId(
        "loading",
      ),
    ).toHaveTextContent(
      "true",
    );

    await waitFor(() => {
      expect(
        screen.getByTestId(
          "authenticated",
        ),
      ).toHaveTextContent(
        "true",
      );
    });

    expect(
      screen.getByTestId(
        "email",
      ),
    ).toHaveTextContent(
      "sam@example.com",
    );

    expect(
      getCurrentAccount,
    ).toHaveBeenCalledTimes(1);
  });

  it("clears an invalid stored session", async () => {
    window.sessionStorage.setItem(
      "nestora.access_token",
      "invalid-token",
    );

    getCurrentAccount.mockRejectedValue(
      new Error(
        "Invalid token",
      ),
    );

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId(
          "loading",
        ),
      ).toHaveTextContent(
        "false",
      );
    });

    expect(
      screen.getByTestId(
        "authenticated",
      ),
    ).toHaveTextContent(
      "false",
    );

    expect(
      window.sessionStorage.getItem(
        "nestora.access_token",
      ),
    ).toBeNull();
  });

  it("logs in and stores the access token", async () => {
    loginAccount.mockResolvedValue({
      access_token:
        "new-access-token",
      token_type: "bearer",
      user: testUser,
    });

    getCurrentAccount.mockResolvedValue(
      testUser,
    );

    renderProvider();

    fireEvent.click(
      screen.getByRole(
        "button",
        {
          name: "Log in",
        },
      ),
    );

    await waitFor(() => {
      expect(
        screen.getByTestId(
          "authenticated",
        ),
      ).toHaveTextContent(
        "true",
      );
    });

    expect(
      loginAccount,
    ).toHaveBeenCalledWith({
      email: "sam@example.com",
      password: "Password123!",
    });

    expect(
      window.sessionStorage.getItem(
        "nestora.access_token",
      ),
    ).toBe(
      "new-access-token",
    );
  });

  it("registers and automatically logs in", async () => {
    registerAccount.mockResolvedValue(
      testUser,
    );

    loginAccount.mockResolvedValue({
      access_token:
        "registered-token",
      token_type: "bearer",
      user: testUser,
    });

    getCurrentAccount.mockResolvedValue(
      testUser,
    );

    renderProvider();

    fireEvent.click(
      screen.getByRole(
        "button",
        {
          name: "Register",
        },
      ),
    );

    await waitFor(() => {
      expect(
        screen.getByTestId(
          "authenticated",
        ),
      ).toHaveTextContent(
        "true",
      );
    });

    expect(
      registerAccount,
    ).toHaveBeenCalledWith({
      email: "sam@example.com",
      full_name: "Sam",
      password: "Password123!",
    });

    expect(
      loginAccount,
    ).toHaveBeenCalledWith({
      email: "sam@example.com",
      password: "Password123!",
    });

    expect(
      window.sessionStorage.getItem(
        "nestora.access_token",
      ),
    ).toBe(
      "registered-token",
    );
  });

  it("logs out and removes the session", async () => {
    window.sessionStorage.setItem(
      "nestora.access_token",
      "stored-token",
    );

    getCurrentAccount.mockResolvedValue(
      testUser,
    );

    renderProvider();

    await waitFor(() => {
      expect(
        screen.getByTestId(
          "authenticated",
        ),
      ).toHaveTextContent(
        "true",
      );
    });

    fireEvent.click(
      screen.getByRole(
        "button",
        {
          name: "Log out",
        },
      ),
    );

    expect(
      screen.getByTestId(
        "authenticated",
      ),
    ).toHaveTextContent(
      "false",
    );

    expect(
      screen.getByTestId(
        "email",
      ),
    ).toHaveTextContent(
      "none",
    );

    expect(
      window.sessionStorage.getItem(
        "nestora.access_token",
      ),
    ).toBeNull();
  });
});