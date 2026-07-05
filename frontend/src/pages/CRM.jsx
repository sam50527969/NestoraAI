import { useEffect, useMemo, useState } from "react";
import { getSavedLeads } from "../services/api";
import { updateLead } from "../services/crmApi";
import CRMToolbar from "../components/CRMToolbar";
import CRMTable from "../components/CRMTable";
import LeadDetailsPanel from "../components/LeadDetailsPanel";

function normalizeLeadsResponse(response) {
  if (Array.isArray(response)) return response;
  if (Array.isArray(response?.data)) return response.data;
  if (Array.isArray(response?.leads)) return response.leads;
  if (Array.isArray(response?.data?.leads)) return response.data.leads;
  return [];
}

function getLeadCategory(lead) {
  return lead.category || lead.type || lead.business_type || "Unknown";
}

function matchesSearch(lead, searchTerm) {
  const value = searchTerm.trim().toLowerCase();

  if (!value) return true;

  const searchableText = [
    lead.name,
    getLeadCategory(lead),
    lead.address,
    lead.phone,
    lead.website,
    lead.source,
    lead.status,
    lead.priority,
    lead.tags,
    lead.assigned_to,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  return searchableText.includes(value);
}

export default function CRM() {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingDetails, setIsSavingDetails] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadSavedLeads = async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await getSavedLeads();
      const loadedLeads = normalizeLeadsResponse(response);
      setLeads(loadedLeads);

      if (selectedLead) {
        const refreshedSelectedLead = loadedLeads.find((lead) => lead.id === selectedLead.id);
        setSelectedLead(refreshedSelectedLead || null);
      }
    } catch (error) {
      console.error("Failed to load saved leads", error);
      setErrorMessage("Unable to load saved leads. Please make sure the backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSavedLeads();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const categories = useMemo(() => {
    const uniqueCategories = new Set(leads.map(getLeadCategory).filter(Boolean));
    return ["All", ...Array.from(uniqueCategories).sort()];
  }, [leads]);

  const filteredLeads = useMemo(() => {
    return leads
      .filter((lead) => matchesSearch(lead, searchTerm))
      .filter((lead) => {
        if (categoryFilter === "All") return true;
        return getLeadCategory(lead) === categoryFilter;
      });
  }, [leads, searchTerm, categoryFilter]);

  const handleSaveLeadDetails = async (leadId, payload) => {
    setIsSavingDetails(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const updatedLead = await updateLead(leadId, payload);

      setLeads((currentLeads) =>
        currentLeads.map((lead) => (lead.id === updatedLead.id ? updatedLead : lead))
      );
      setSelectedLead(updatedLead);
      setSuccessMessage("Lead details saved successfully.");
    } catch (error) {
      console.error("Failed to update lead", error);
      setErrorMessage("Unable to save lead details. Please check the backend and try again.");
    } finally {
      setIsSavingDetails(false);
    }
  };

  return (
    <main className="crm-page">
      <div className="crm-page-header">
        <div>
          <p className="eyebrow">Nestora CRM</p>
          <h1>Saved Leads</h1>
          <p className="crm-page-subtitle">
            Manage saved businesses, track status, add notes, and prepare sales follow-ups.
          </p>
        </div>

        <button type="button" className="secondary-button" onClick={loadSavedLeads}>
          Refresh
        </button>
      </div>

      <CRMToolbar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        categoryFilter={categoryFilter}
        onCategoryChange={setCategoryFilter}
        categories={categories}
        totalLeads={leads.length}
        visibleLeads={filteredLeads.length}
      />

      {errorMessage && <div className="crm-alert error">{errorMessage}</div>}
      {successMessage && <div className="crm-alert success">{successMessage}</div>}

      <div className="crm-workspace">
        <CRMTable
          leads={filteredLeads}
          isLoading={isLoading}
          selectedLeadId={selectedLead?.id}
          onSelectLead={setSelectedLead}
        />

        <LeadDetailsPanel
          lead={selectedLead}
          onSave={handleSaveLeadDetails}
          onClose={() => setSelectedLead(null)}
          isSaving={isSavingDetails}
        />
      </div>
    </main>
  );
}
