import { BrowserRouter, Route, Routes } from "react-router-dom";
import MissionCenter from "./pages/MissionCenter";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import DashboardV2 from "./features/dashboard/DashboardV2";
import CRM from "./pages/CRM";
import CEO from "./pages/CEO";

import "./App.css";

function PlaceholderPage({ title }) {
  return (
    <section className="panel">
      <p className="eyebrow">Coming Soon</p>
      <h2>{title}</h2>
      <p>This module will be added in the next sprints.</p>
    </section>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />

        <main className="main">
          <TopBar activePage="Nestora AI" />

          <Routes>
            <Route path="/" element={<DashboardV2 />} />
            <Route path="/leads" element={<DashboardV2 />} />
            <Route path="/crm" element={<CRM />} />
            <Route path="/missions" element={<MissionCenter />} />
            <Route path="/ceo" element={<CEO />} />
            
            <Route
              path="/proposal"
              element={<PlaceholderPage title="Proposal Generator" />}
            />
            <Route
              path="/website-intelligence"
              element={<PlaceholderPage title="Website Intelligence" />}
            />
            <Route
              path="/analytics"
              element={<PlaceholderPage title="Analytics" />}
            />
            <Route
              path="/settings"
              element={<PlaceholderPage title="Settings" />}
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;