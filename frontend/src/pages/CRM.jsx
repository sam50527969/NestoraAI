import { useEffect, useMemo, useState } from "react";
import { getSavedLeads } from "../services/api";
import CRMToolbar from "../components/CRMToolbar";
import CRMTable from "../components/CRMTable";

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
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  return searchableText.includes(value);
}

export default function CRM() {
  const [leads, setLeads] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const loadSavedLeads = async () => {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await getSavedLeads();
      setLeads(normalizeLeadsResponse(response));
    } catch (error) {
      console.error("Failed to load saved leads", error);
      setErrorMessage("Unable to load saved leads. Please make sure the backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSavedLeads();
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

  return (
    <main className="crm-page">
      <div className="crm-page-header">
        <div>
          <p className="eyebrow">Nestora CRM</p>
          <h1>Saved Leads</h1>
          <p className="crm-page-subtitle">
            Manage businesses saved from lead discovery and prepare them for sales follow-up.
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

      <CRMTable leads={filteredLeads} isLoading={isLoading} />
    </main>
  );
}
