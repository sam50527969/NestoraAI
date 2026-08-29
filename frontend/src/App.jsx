import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";

import ProtectedRoute from "./auth/ProtectedRoute";
import WorkspaceBoundary from "./workspace/WorkspaceBoundary";

import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";

import DashboardV2 from "./features/dashboard/DashboardV2";

import AdminExplorer from "./pages/AdminExplorer";
import AIMissionCreator from "./pages/AIMissionCreator";
import BusinessAnalysis from "./pages/BusinessAnalysis";
import CEO from "./pages/CEO";
import CRM from "./pages/CRM";
import Login from "./pages/Login";
import MarketingDirector from "./pages/MarketingDirector";
import MissionDashboard from "./pages/MissionDashboard";
import WorkforceDashboard from "./pages/WorkforceDashboard";

import "./App.css";

function PlaceholderPage({
  title,
}) {
  return (
    <section className="placeholder-page">
      <span className="eyebrow">
        Coming Soon
      </span>

      <h2>{title}</h2>

      <p>
        This module will be added in the
        next sprints.
      </p>
    </section>
  );
}

function ApplicationShell() {
  return (
    <div className="app">
      <Sidebar />

      <main className="main">
        <TopBar activePage="Nestora AI" />
        <WorkspaceBoundary>
          <Outlet />
        </WorkspaceBoundary>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          element={<ProtectedRoute />}
        >
          <Route
            element={
              <ApplicationShell />
            }
          >
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
              element={
                <MissionDashboard />
              }
            />

            <Route
              path="/ai-missions"
              element={
                <AIMissionCreator />
              }
            />

            <Route
              path="/workforce"
              element={
                <WorkforceDashboard />
              }
            />

            <Route
              path="/admin-explorer"
              element={
                <AdminExplorer />
              }
            />

            <Route
              path="/ceo"
              element={<CEO />}
            />

            <Route
              path="/marketing"
              element={
                <MarketingDirector />
              }
            />

            <Route
              path="/business-analysis"
              element={
                <BusinessAnalysis />
              }
            />

            <Route
              path="/proposal"
              element={
                <PlaceholderPage
                  title={
                    "Proposal Generator"
                  }
                />
              }
            />

            <Route
              path="/website-intelligence"
              element={
                <PlaceholderPage
                  title={
                    "Website Intelligence"
                  }
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
          </Route>
        </Route>

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;