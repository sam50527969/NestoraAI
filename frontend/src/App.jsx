import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";

import DashboardV2 from "./features/dashboard/DashboardV2";

import AdminExplorer from "./pages/AdminExplorer";
import AIMissionCreator from "./pages/AIMissionCreator";
import CEO from "./pages/CEO";
import CRM from "./pages/CRM";
import MarketingDirector from "./pages/MarketingDirector";
import MissionDashboard from "./pages/MissionDashboard";
import WorkforceDashboard from "./pages/WorkforceDashboard";

import "./App.css";

function PlaceholderPage({ title }) {
  return (
    <section className="panel">
      <p className="eyebrow">Coming Soon</p>

      <h2>{title}</h2>

      <p>
        This module will be added in the next sprints.
      </p>
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
            <Route
              path="/"
              element={<DashboardV2 />}
            />

            <Route
              path="/leads"
              element={<DashboardV2 />}
            />

            <Route
              path="/crm"
              element={<CRM />}
            />

            <Route
              path="/missions"
              element={<MissionDashboard />}
            />

            <Route
              path="/ai-missions"
              element={<AIMissionCreator />}
            />

            <Route
              path="/workforce"
              element={<WorkforceDashboard />}
            />

            <Route
              path="/admin-explorer"
              element={<AdminExplorer />}
            />

            <Route
              path="/ceo"
              element={<CEO />}
            />

            <Route
              path="/marketing"
              element={<MarketingDirector />}
            />

            <Route
              path="/proposal"
              element={
                <PlaceholderPage
                  title="Proposal Generator"
                />
              }
            />

            <Route
              path="/website-intelligence"
              element={
                <PlaceholderPage
                  title="Website Intelligence"
                />
              }
            />

            <Route
              path="/analytics"
              element={
                <PlaceholderPage
                  title="Analytics"
                />
              }
            />

            <Route
              path="/settings"
              element={
                <PlaceholderPage
                  title="Settings"
                />
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;