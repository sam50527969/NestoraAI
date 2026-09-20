import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

import {
  confirmPasswordReset,
  requestPasswordReset,
} from "../../api";
import useAuth from "../../auth/useAuth";

import Login from "../Login";

vi.mock("../../api", () => ({
  confirmPasswordReset: vi.fn(),
  requestPasswordReset: vi.fn(),
}));

vi.mock(
  "../../auth/useAuth",
  () => ({
    default: vi.fn(),
  }),
);

const login = vi.fn();
const register = vi.fn();

function renderLogin(
  authOverrides = {},
  initialEntry = "/login",
) {
  useAuth.mockReturnValue({
    login,
    register,
    isAuthenticated: false,
    isLoading: false,
    ...authOverrides,
  });

  return render(
    <MemoryRouter
      initialEntries={[initialEntry]}
    >
      <Routes>
        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/"
          element={
            <div>
              Dashboard page
            </div>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  login.mockReset();
  register.mockReset();
  useAuth.mockReset();
  confirmPasswordReset.mockReset();
  requestPasswordReset.mockReset();
});

describe("Login", () => {
  it("renders the sign-in form", () => {
    renderLogin();

    expect(
      screen.getByRole(
        "heading",
        {
          name: "Welcome back",
        },
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByLabelText(
        "Email address",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByLabelText(
        "Password",
      ),
    ).toBeInTheDocument();
  });

  it("submits login credentials", async () => {
    const user =
      userEvent.setup();

    login.mockResolvedValue({
      email: "sam@example.com",
    });

    renderLogin();

    await user.type(
      screen.getByLabelText(
        "Email address",
      ),
      "sam@example.com",
    );

    await user.type(
      screen.getByLabelText(
        "Password",
      ),
      "Password123!",
    );

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Sign in to Nestora",
        },
      ),
    );

    await waitFor(() => {
      expect(
        login,
      ).toHaveBeenCalledWith({
        email: "sam@example.com",
        password: "Password123!",
      });
    });

    expect(
      screen.getByText(
        "Dashboard page",
      ),
    ).toBeInTheDocument();
  });

  it("registers a new account", async () => {
    const user =
      userEvent.setup();

    register.mockResolvedValue({
      email: "new@example.com",
    });

    renderLogin();

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Register",
        },
      ),
    );

    await user.type(
      screen.getByLabelText(
        "Full name",
      ),
      "New User",
    );

    await user.type(
      screen.getByLabelText(
        "Email address",
      ),
      "new@example.com",
    );

    await user.type(
      screen.getByLabelText(
        "Password",
      ),
      "Password123!",
    );

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Create account",
        },
      ),
    );

    await waitFor(() => {
      expect(
        register,
      ).toHaveBeenCalledWith({
        full_name: "New User",
        email: "new@example.com",
        password: "Password123!",
      });
    });
  });

  it("requests a password reset without exposing account state", async () => {
    const user =
      userEvent.setup();

    requestPasswordReset.mockResolvedValue({
      message:
        "If an account exists for that email, a password reset link has been sent.",
    });

    renderLogin();

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Forgot password?",
        },
      ),
    );

    await user.type(
      screen.getByLabelText(
        "Email address",
      ),
      "sam@example.com",
    );

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Send reset link",
        },
      ),
    );

    await waitFor(() => {
      expect(
        requestPasswordReset,
      ).toHaveBeenCalledWith(
        "sam@example.com",
      );
    });

    expect(
      screen.getByRole("status"),
    ).toHaveTextContent(
      "If an account exists",
    );
  });

  it("resets a password from a reset token", async () => {
    const user =
      userEvent.setup();

    confirmPasswordReset.mockResolvedValue({
      message:
        "Password has been reset successfully.",
    });

    const token = "a".repeat(40);

    renderLogin(
      {},
      `/login?reset_token=${token}`,
    );

    expect(
      screen.getByRole(
        "heading",
        {
          name:
            "Choose a new password",
        },
      ),
    ).toBeInTheDocument();

    await user.type(
      screen.getByLabelText(
        "New password",
      ),
      "NewPassword456!",
    );

    await user.type(
      screen.getByLabelText(
        "Confirm new password",
      ),
      "NewPassword456!",
    );

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Reset password",
        },
      ),
    );

    await waitFor(() => {
      expect(
        confirmPasswordReset,
      ).toHaveBeenCalledWith({
        token,
        password:
          "NewPassword456!",
      });
    });

    expect(
      screen.getByRole(
        "heading",
        {
          name: "Welcome back",
        },
      ),
    ).toBeInTheDocument();
  });

  it("requires 12 characters for new account passwords", async () => {
    const user =
      userEvent.setup();

    renderLogin();

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Register",
        },
      ),
    );

    expect(
      screen.getByLabelText(
        "Password",
      ),
    ).toHaveAttribute(
      "minlength",
      "12",
    );
  });


  it("renders backend validation arrays safely", async () => {
    const user =
      userEvent.setup();

    register.mockRejectedValue(
      new Error(
        JSON.stringify({
          detail: [
            {
              loc: [
                "body",
                "password",
              ],
              msg:
                "Password is too short",
              type:
                "string_too_short",
            },
          ],
        }),
      ),
    );

    renderLogin();

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Register",
        },
      ),
    );

    await user.type(
      screen.getByLabelText(
        "Full name",
      ),
      "New User",
    );

    await user.type(
      screen.getByLabelText(
        "Email address",
      ),
      "new@example.com",
    );

    await user.type(
      screen.getByLabelText(
        "Password",
      ),
      "123456789012",
    );

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Create account",
        },
      ),
    );

    expect(
      await screen.findByRole(
        "alert",
      ),
    ).toHaveTextContent(
      "password: Password is too short",
    );
  });
});