function TopBar({ activePage }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">AI Business Operating System</p>
        <h1>{activePage}</h1>
        <p>Your command center for leads, revenue, and daily priorities.</p>
      </div>

      <div className="topbar-actions">
        <button className="icon-button">🔔</button>
        <button className="profile-button">Sam</button>
      </div>
    </header>
  );
}

export default TopBar;