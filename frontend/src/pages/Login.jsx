import {
  useState,
} from "react";
import {
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  confirmPasswordReset,
  requestPasswordReset,
} from "../api";
import useAuth from "../auth/useAuth";

import "./Login.css";


function getErrorMessage(error) {
  const fallback =
    "Authentication failed. Please try again.";

  if (!error?.message) {
    return fallback;
  }

  try {
    const parsed = JSON.parse(
      error.message,
    );

    const detail = parsed.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          if (
            typeof item === "string"
          ) {
            return item;
          }

          if (
            item &&
            typeof item.msg ===
              "string"
          ) {
            const field =
              Array.isArray(item.loc)
                ? item.loc
                    .filter(
                      (part) =>
                        part !== "body",
                    )
                    .join(".")
                : "";

            return field
              ? `${field}: ${item.msg}`
              : item.msg;
          }

          return null;
        })
        .filter(Boolean);

      return (
        messages.join(" ") ||
        fallback
      );
    }

    if (
      detail &&
      typeof detail === "object"
    ) {
      return (
        detail.message ||
        fallback
      );
    }

    return (
      parsed.message ||
      fallback
    );
  } catch {
    return error.message;
  }
}


function Login() {
  const navigate = useNavigate();
  const location = useLocation();

  const {
    login,
    register,
    isAuthenticated,
    isLoading,
  } = useAuth();

  const resetToken =
    new URLSearchParams(
      location.search,
    ).get("reset_token") || "";

  const [mode, setMode] =
    useState(
      resetToken
        ? "reset"
        : "login",
    );

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
  });

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  const destination =
    location.state?.from?.pathname ||
    "/";

  if (
    isAuthenticated &&
    !isLoading
  ) {
    return (
      <Navigate
        to={destination}
        replace
      />
    );
  }

  function updateField(event) {
    const {
      name,
      value,
    } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function changeMode(nextMode) {
    setMode(nextMode);
    setError("");
    setSuccess("");
  }

  async function submit(event) {
    event.preventDefault();

    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      if (mode === "register") {
        await register({
          full_name:
            form.full_name.trim(),
          email:
            form.email.trim(),
          password:
            form.password,
        });

        navigate(
          destination,
          {
            replace: true,
          },
        );

        return;
      }

      if (mode === "login") {
        await login({
          email:
            form.email.trim(),
          password:
            form.password,
        });

        navigate(
          destination,
          {
            replace: true,
          },
        );

        return;
      }

      if (mode === "forgot") {
        const response =
          await requestPasswordReset(
            form.email.trim(),
          );

        setSuccess(
          response.message ||
            (
              "If an account exists for "
              + "that email, a password "
              + "reset link has been sent."
            ),
        );

        return;
      }

      if (mode === "reset") {
        if (
          form.password !==
          form.confirm_password
        ) {
          setError(
            "The passwords do not match.",
          );

          return;
        }

        const response =
          await confirmPasswordReset({
            token: resetToken,
            password:
              form.password,
          });

        navigate(
          "/login",
          {
            replace: true,
          },
        );

        setMode("login");

        setForm((current) => ({
          ...current,
          password: "",
          confirm_password: "",
        }));

        setSuccess(
          response.message ||
            (
              "Password has been reset "
              + "successfully. You can "
              + "sign in now."
            ),
        );
      }
    } catch (submitError) {
      setError(
        getErrorMessage(
          submitError,
        ),
      );
    } finally {
      setSubmitting(false);
    }
  }

  const heading = {
    login: "Welcome back",
    register: "Create your account",
    forgot: "Reset your password",
    reset: "Choose a new password",
  }[mode];

  const description = {
    login:
      "Sign in to continue to your business dashboard.",
    register:
      "Set up your Nestora workspace credentials.",
    forgot:
      "Enter your email and we will send you a secure reset link.",
    reset:
      "Enter a new password for your Nestora account.",
  }[mode];

  return (
    <main className="auth-page">
      <section className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-logo">
            N
          </div>

          <p className="auth-eyebrow">
            Nestora AI
          </p>

          <h1>
            Your AI business command center
          </h1>

          <p className="auth-brand-description">
            Manage leads, execute missions,
            prepare outreach, and coordinate
            your AI workforce from one secure
            workspace.
          </p>

          <div className="auth-feature-list">
            <div>
              <span>01</span>
              AI-powered lead intelligence
            </div>

            <div>
              <span>02</span>
              CRM and pipeline automation
            </div>

            <div>
              <span>03</span>
              Secure executive approvals
            </div>
          </div>
        </div>
      </section>

      <section className="auth-form-panel">
        <div className="auth-card">
          <div className="auth-mobile-brand">
            <div className="auth-logo">
              N
            </div>

            <span>Nestora AI</span>
          </div>

          <div className="auth-card-heading">
            <p className="auth-eyebrow">
              Secure workspace
            </p>

            <h2>
              {heading}
            </h2>

            <p>
              {description}
            </p>
          </div>

          {(
            mode === "login" ||
            mode === "register"
          ) && (
            <div
              className="auth-mode-switch"
              role="group"
              aria-label="Authentication mode"
            >
              <button
                type="button"
                className={
                  mode === "login"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  changeMode("login")
                }
              >
                Sign in
              </button>

              <button
                type="button"
                className={
                  mode === "register"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  changeMode("register")
                }
              >
                Register
              </button>
            </div>
          )}

          <form
            className="auth-form"
            onSubmit={submit}
          >
            {mode === "register" && (
              <label>
                Full name

                <input
                  type="text"
                  name="full_name"
                  value={
                    form.full_name
                  }
                  onChange={
                    updateField
                  }
                  autoComplete="name"
                  minLength={2}
                  maxLength={120}
                  required
                />
              </label>
            )}

            {mode !== "reset" && (
              <label>
                Email address

                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={updateField}
                  autoComplete="email"
                  placeholder="you@example.com"
                  required
                />
              </label>
            )}

            {(
              mode === "login" ||
              mode === "register" ||
              mode === "reset"
            ) && (
              <label>
                {mode === "reset"
                  ? "New password"
                  : "Password"}

                <input
                  type="password"
                  name="password"
                  value={form.password}
                  onChange={updateField}
                  autoComplete={
                    mode === "login"
                      ? "current-password"
                      : "new-password"
                  }
                  minLength={
                    mode === "login"
                      ? 1
                      : 12
                  }
                  maxLength={128}
                  placeholder={
                    mode === "login"
                      ? "Your password"
                      : "Minimum 12 characters"
                  }
                  required
                />
              </label>
            )}

            {mode === "reset" && (
              <label>
                Confirm new password

                <input
                  type="password"
                  name="confirm_password"
                  value={
                    form.confirm_password
                  }
                  onChange={updateField}
                  autoComplete="new-password"
                  minLength={12}
                  maxLength={128}
                  placeholder="Repeat your new password"
                  required
                />
              </label>
            )}

            {error && (
              <div
                className="auth-error"
                role="alert"
              >
                {error}
              </div>
            )}

            {success && (
              <div
                className="auth-success"
                role="status"
              >
                {success}
              </div>
            )}

            <button
              type="submit"
              className="auth-submit"
              disabled={submitting}
            >
              {submitting
                ? "Please wait..."
                : mode === "login"
                  ? "Sign in to Nestora"
                  : mode === "register"
                    ? "Create account"
                    : mode === "forgot"
                      ? "Send reset link"
                      : "Reset password"}
            </button>
          </form>

          {mode === "login" && (
            <button
              type="button"
              className="auth-inline-action"
              onClick={() =>
                changeMode("forgot")
              }
            >
              Forgot password?
            </button>
          )}

          {(
            mode === "forgot" ||
            mode === "reset"
          ) && (
            <button
              type="button"
              className="auth-inline-action"
              onClick={() => {
                navigate(
                  "/login",
                  {
                    replace: true,
                  },
                );

                changeMode("login");
              }}
            >
              Back to sign in
            </button>
          )}

          <p className="auth-security-note">
            Your session is stored only for
            the current browser session.
          </p>
        </div>
      </section>
    </main>
  );
}

export default Login;
