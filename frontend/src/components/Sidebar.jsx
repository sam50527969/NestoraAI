import { NavLink } from "react-router-dom";

function Sidebar() {
  const navSections = [
    {
      title: "Business OS",
      items: [
        { label: "Dashboard", path: "/", icon: "🏠" },
        { label: "Lead Finder", path: "/leads", icon: "🔍" },
        { label: "CRM", path: "/crm", icon: "📇" },
      ],
    },
    {
      title: "AI Agents",
      items: [
        { label: "CEO Agent", path: "/ceo", icon: "🧠" },
        { label: "Analytics", path: "/analytics", icon: "📊" },
      ],
    },
    {
      title: "System",
      items: [{ label: "Settings", path: "/settings", icon: "⚙️" }],
    },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">N</div>
        <div>
          <h2>Nestora AI</h2>
          <p>Business Operating System</p>
        </div>
      </div>

      <nav className="nav">
        {navSections.map((section) => (
          <div className="nav-section" key={section.title}>
            <p className="nav-section-title">{section.title}</p>

            {section.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  isActive ? "nav-item active" : "nav-item"
                }
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p>Current Plan</p>
        <strong>Founder Build</strong>
      </div>
    </aside>
  );
}

export default Sidebar;