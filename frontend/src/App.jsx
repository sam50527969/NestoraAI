import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";
import Dashboard from "./pages/Dashboard";
import CRM from "./pages/CRM";
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
            <Route path="/" element={<Dashboard />} />
            <Route path="/leads" element={<Dashboard />} />
            <Route path="/crm" element={<CRM />} />
            <Route path="/ceo" element={<PlaceholderPage title="CEO Agent" />} />
            <Route path="/analytics" element={<PlaceholderPage title="Analytics" />} />
            <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;