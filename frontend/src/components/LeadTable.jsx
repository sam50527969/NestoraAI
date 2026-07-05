import { useState } from "react";
import { saveLead } from "../api";

function getPriorityClass(priority) {
  if (priority === "High") return "badge priority-high";
  if (priority === "Medium") return "badge priority-medium";
  return "badge priority-low";
}

function LeadTable({ leads = [] }) {
  const [savedLeadIds, setSavedLeadIds] = useState({});

  function openMap(lead) {
    const query = encodeURIComponent(`${lead.businessName} ${lead.location}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, "_blank");
  }

  async function handleSaveLead(lead) {
    try {
      await saveLead({
        name: lead.businessName,
        category: lead.category,
        address: lead.location,
        phone: lead.phone,
        website: lead.website,
        source: "OpenStreetMap",
        status: lead.status || "New",
        priority: lead.priority || "Medium",
        notes: lead.aiRecommendation || "",
      });

      setSavedLeadIds((previous) => ({
        ...previous,
        [lead.id]: true,
      }));
    } catch (error) {
      console.error("Failed to save lead:", error);
      alert("Unable to save lead.");
    }
  }

  return (
    <section className="panel">
      <div className="table-header">
        <div>
          <h2>AI Research Results</h2>
          <p className="eyebrow">Enriched Business Leads</p>
        </div>
        <button className="secondary">Find More Leads</button>
      </div>

      <table className="lead-table">
        <thead>
          <tr>
            <th>Business</th>
            <th>Category</th>
            <th>Location</th>
            <th>Phone</th>
            <th>Website</th>
            <th>Score</th>
            <th>Quality</th>
            <th>Priority</th>
            <th>AI Recommendation</th>
            <th>Map</th>
            <th>CRM</th>
          </tr>
        </thead>

        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id}>
              <td>{lead.businessName}</td>
              <td>{lead.category}</td>
              <td>{lead.location}</td>
              <td>{lead.phoneAvailable ? lead.phone : "Not found"}</td>
              <td>
                {lead.websiteAvailable ? (
                  <a href={lead.website} target="_blank" rel="noreferrer">
                    Open Website
                  </a>
                ) : (
                  "Not found"
                )}
              </td>
              <td>
                <span className="badge">{lead.opportunityScore ?? 0}%</span>
              </td>
              <td>
                <span className="badge">{lead.contactQuality ?? 0}%</span>
              </td>
              <td>
                <span className={getPriorityClass(lead.priority)}>
                  {lead.priority || "Low"}
                </span>
              </td>
              <td>{lead.aiRecommendation || "Needs review"}</td>
              <td>
                <button className="small-btn" onClick={() => openMap(lead)}>
                  Open Map
                </button>
              </td>
              <td>
                <button
                  className="small-btn"
                  onClick={() => handleSaveLead(lead)}
                  disabled={savedLeadIds[lead.id]}
                >
                  {savedLeadIds[lead.id] ? "Saved" : "Save"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

export default LeadTable;