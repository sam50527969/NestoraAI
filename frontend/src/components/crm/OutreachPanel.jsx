import { useState } from "react";
import Button from "../ui/Button";

const SECTIONS = [
  { key: "email_body", label: "Email", icon: "📧" },
  { key: "whatsapp_message", label: "WhatsApp", icon: "💬" },
  { key: "cold_call_script", label: "Cold Call", icon: "📞" },
  { key: "proposal_summary", label: "Proposal", icon: "📄" },
];

function OutreachPanel({ outreach }) {
  const [activeTab, setActiveTab] = useState("email_body");
  const [copiedKey, setCopiedKey] = useState("");

  if (!outreach) return null;

  const activeSection = SECTIONS.find((section) => section.key === activeTab);
  const activeContent = outreach[activeTab];

  async function copyText(key, content) {
    await navigator.clipboard.writeText(content);
    setCopiedKey(key);

    setTimeout(() => {
      setCopiedKey("");
    }, 1800);
  }

  async function copyAll() {
    const fullContent = `
Email Subject:
${outreach.email_subject}

Email:
${outreach.email_body}

WhatsApp:
${outreach.whatsapp_message}

Cold Call:
${outreach.cold_call_script}

Proposal:
${outreach.proposal_summary}
`;

    await navigator.clipboard.writeText(fullContent.trim());
    setCopiedKey("all");

    setTimeout(() => {
      setCopiedKey("");
    }, 1800);
  }

  return (
    <div className="outreach-panel">
      <div className="outreach-title-row">
        <div>
          <p className="eyebrow">AI Sales Assistant</p>
          <h2>✨ Nestora Copilot</h2>
        </div>

        <Button variant="secondary" onClick={copyAll}>
          {copiedKey === "all" ? "Copied!" : "Copy All"}
        </Button>
      </div>

      <div className="outreach-subject">
        <span>Email Subject</span>
        <strong>{outreach.email_subject}</strong>
      </div>

      <div className="outreach-tabs">
        {SECTIONS.map((section) => (
          <button
            key={section.key}
            type="button"
            className={activeTab === section.key ? "active" : ""}
            onClick={() => setActiveTab(section.key)}
          >
            <span>{section.icon}</span>
            {section.label}
          </button>
        ))}
      </div>

      <div className="outreach-section">
        <div className="outreach-header">
          <h4>
            {activeSection.icon} {activeSection.label}
          </h4>

          <Button
            variant="secondary"
            onClick={() => copyText(activeTab, activeContent)}
          >
            {copiedKey === activeTab ? "Copied!" : "Copy"}
          </Button>
        </div>

        <pre>{activeContent}</pre>
      </div>
    </div>
  );
}

export default OutreachPanel;