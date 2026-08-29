import {
  useNavigate,
} from "react-router-dom";

import useAuth from "../auth/useAuth";
import WorkspaceSelector from "../workspace/WorkspaceSelector";

function getInitials(user) {
  const name =
    user?.full_name?.trim();

  if (name) {
    return name
      .split(/\s+/)
      .slice(0, 2)
      .map((part) =>
        part.charAt(0),
      )
      .join("")
      .toUpperCase();
  }

  return (
    user?.email
      ?.charAt(0)
      .toUpperCase() ||
    "U"
  );
}

function TopBar({
  activePage,
}) {
  const navigate = useNavigate();

  const {
    user,
    logout,
  } = useAuth();

  const compactPages = [
    "AI Mission Creator",
    "AI Workforce",
    "Mission Dashboard",
  ];

  const isCompact =
    compactPages.includes(
      activePage,
    );

  function signOut() {
    logout();

    navigate(
      "/login",
      {
        replace: true,
      },
    );
  }

  return (
    <header
      className={
        `topbar ${
          isCompact
            ? "topbar-compact"
            : ""
        }`
      }
    >
      <div>
        {!isCompact && (
          <>
            <span className="eyebrow">
              AI Business Operating System
            </span>

            <h1>{activePage}</h1>

            <p className="topbar-subtitle">
              Your command center for leads,
              CRM activity, AI agents, and
              business growth.
            </p>
          </>
        )}

        {isCompact && (
          <h1 className="topbar-compact-title">
            {activePage}
          </h1>
        )}
      </div>

      <div className="topbar-actions">
        <WorkspaceSelector />

        <button
          type="button"
          className="icon-button"
          title="Notifications"
          aria-label="Notifications"
        >
          ●
        </button>

        <div
          className="profile-button"
          title={user?.email}
        >
          <span className="profile-avatar">
            {getInitials(user)}
          </span>

          <span>
            {user?.full_name ||
              user?.email ||
              "Nestora User"}
          </span>
        </div>

        <button
          type="button"
          className="icon-button"
          title="Sign out"
          aria-label="Sign out"
          onClick={signOut}
        >
          ↪
        </button>
      </div>
    </header>
  );
}

export default TopBar;