function TopBar({ activePage }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">AI Business Operating System</p>
        <h1>{activePage}</h1>
        <p className="topbar-subtitle">
          Your command center for leads, CRM activity, AI agents, and business growth.
        </p>
      </div>

      <div className="topbar-actions">
        <button className="icon-button" title="Notifications">
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