import {
  useState,
} from "react";
import {
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

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

  const [mode, setMode] =
    useState("login");

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
  });

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [error, setError] =
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
  }

  async function submit(event) {
    event.preventDefault();

    setSubmitting(true);
    setError("");

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
      } else {
        await login({
          email:
            form.email.trim(),
          password:
            form.password,
        });
      }

      navigate(
        destination,
        {
          replace: true,
        },
      );
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
              {mode === "login"
                ? "Welcome back"
                : "Create your account"}
            </h2>

            <p>
              {mode === "login"
                ? (
                    "Sign in to continue to "
                    + "your business dashboard."
                  )
                : (
                    "Set up your Nestora "
                    + "workspace credentials."
                  )}
            </p>
          </div>

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

            <label>
              Password

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
                minLength={8}
                placeholder="Minimum 8 characters"
                required
              />
            </label>

            {error && (
              <div
                className="auth-error"
                role="alert"
              >
                {error}
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
                  : "Create account"}
            </button>
          </form>

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