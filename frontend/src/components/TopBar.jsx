function TopBar({ activePage }) {
  const compactPages = [
    "AI Mission Creator",
    "AI Workforce",
    "Mission Dashboard",
  ];

  const isCompact = compactPages.includes(activePage);

  return (
    <header className={`topbar ${isCompact ? "topbar-compact" : ""}`}>
      <div>
        {!isCompact && (
          <>
            <p className="eyebrow">
              AI Business Operating System
            </p>

            <h1>{activePage}</h1>

            <p className="topbar-subtitle">
              Your command center for leads, CRM activity,
              AI agents, and business growth.
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
        <button
          className="icon-button"
          title="Notifications"
        >
          🔔
        </button>

        <div className="profile-button">
          <span className="profile-avatar">S</span>
          <span>Sam</span>
        </div>
      </div>
    </header>
  );
}

export default TopBar;