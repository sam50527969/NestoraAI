import { NavLink } from "react-router-dom";
import {
  BarChart3,
  Brain,
  Building2,
  Home,
  Rocket,
  Search,
  Settings,
} from "lucide-react";

function Sidebar() {
  const navSections = [
    {
      title: "Business OS",
      items: [
        { label: "Dashboard", path: "/", icon: Home },
        { label: "Lead Finder", path: "/leads", icon: Search },
        { label: "CRM", path: "/crm", icon: Building2 },
        { label: "Mission Center", path: "/missions", icon: Rocket },
      ],
    },
    {
      title: "AI Agents",
      items: [
        { label: "CEO Agent", path: "/ceo", icon: Brain },
        { label: "Analytics", path: "/analytics", icon: BarChart3 },
      ],
    },
    {
      title: "System",
      items: [
        { label: "Settings", path: "/settings", icon: Settings },
      ],
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

            {section.items.map((item) => {
              const Icon = item.icon;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    isActive ? "nav-item active" : "nav-item"
                  }
                >
                  <Icon size={18} strokeWidth={2.2} />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
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