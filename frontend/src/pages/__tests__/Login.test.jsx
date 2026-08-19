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

import useAuth from "../../auth/useAuth";

import Login from "../Login";

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
      initialEntries={["/login"]}
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
      "12345678",
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