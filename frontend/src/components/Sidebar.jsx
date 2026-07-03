function Sidebar({ activePage, setActivePage }) {
  const pages = [
    "Dashboard",
    "CEO Agent",
    "Sales",
    "CRM",
    "Marketing",
    "Finance",
  ];

  return (
    <aside className="sidebar">
      <div>
        <h2>Nestora AI</h2>
        <p className="sidebar-subtitle">
          Business command center
        </p>
      </div>

      <nav>
        {pages.map((page) => (
          <button
            key={page}
            className={activePage === page ? "active" : ""}
            onClick={() => setActivePage(page)}
          >
            {page}
          </button>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;