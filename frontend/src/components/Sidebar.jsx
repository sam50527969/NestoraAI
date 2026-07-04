import { NavLink } from "react-router-dom";

function Sidebar() {
  const navItems = [
    { label: "Dashboard", path: "/" },
    { label: "Lead Finder", path: "/leads" },
    { label: "CRM", path: "/crm" },
    { label: "CEO Agent", path: "/ceo" },
    { label: "Analytics", path: "/analytics" },
    { label: "Settings", path: "/settings" },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <h2>Nestora AI</h2>
        <p>Business OS</p>
      </div>

      <nav className="nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;