import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import "./styles/theme.css";
import App from './App.jsx'
import "./components/crm/workspace/workspace.css";
import "./components/agents/ceo/ceo-chat.css";
import "./components/dashboard/executive-header.css";
import "./components/dashboard/executive-brief.css";

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
