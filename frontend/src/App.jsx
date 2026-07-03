import TopBar from "./components/TopBar";
import { useState } from "react";
import "./App.css";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  return (
    <div className="app">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      <main className="main">
        <TopBar activePage={activePage} />

        {activePage === "Dashboard" ? (
          <Dashboard />
        ) : (
          <section className="panel">
            <p className="eyebrow">{activePage}</p>
            <h2>{activePage} module coming next</h2>
            <p>
              This section will be built as part of the next milestones.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;