import CRMWorkspace from "../components/crm/workspace/CRMWorkspace";
import {
  getLeadCategory,
  matchesLeadSearch,
  normalizeLeadsResponse,
} from "../utils/crm";
import { useEffect, useMemo, useState } from "react";
import {
  getSavedLeads,
  updateLead,
  generateOutreach,
  analyzeLead,
  analyzeWebsite,
} from "../api";
import CRMToolbar from "../components/CRMToolbar";
import CRMTable from "../components/CRMTable";
import CRMBoard from "../components/crm/CRMBoard";
import CRMHeader from "../components/crm/CRMHeader";
import CRMSidePanel from "../components/crm/CRMSidePanel";



export default function CRM() {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [viewMode, setViewMode] = useState("board");

  const [isLoading, setIsLoading] = useState(true);
  const [isSavingDetails, setIsSavingDetails] = useState(false);
  const [isGeneratingOutreach, setIsGeneratingOutreach] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAnalyzingWebsite, setIsAnalyzingWebsite] = useState(false);

  const [outreach, setOutreach] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [websiteAnalysis, setWebsiteAnalysis] = useState(null);

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
        const refreshedSelectedLead = loadedLeads.find(
          (lead) => lead.id === selectedLead.id
        );
        setSelectedLead(refreshedSelectedLead || null);
      }
    } catch (error) {
      console.error("Failed to load saved leads", error);
      setErrorMessage(
        "Unable to load saved leads. Please make sure the backend is running."
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSavedLeads();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setOutreach(null);
    setWebsiteAnalysis(null);
  }, [selectedLead?.id]);

  useEffect(() => {
    if (!selectedLead) {
      setAnalysis(null);
      return;
    }

    async function runAnalysis() {
      setIsAnalyzing(true);

      try {
        const result = await analyzeLead({
          name: selectedLead.name,
          category: selectedLead.category,
          phone: selectedLead.phone,
          website: selectedLead.website,
          priority: selectedLead.priority,
          notes: selectedLead.notes,
        });

        setAnalysis(result);
      } catch (error) {
        console.error("Failed to analyze lead", error);
        setAnalysis(null);
      } finally {
        setIsAnalyzing(false);
      }
    }

    runAnalysis();
  }, [selectedLead]);

  const categories = useMemo(() => {
    const uniqueCategories = new Set(leads.map(getLeadCategory).filter(Boolean));
    return ["All", ...Array.from(uniqueCategories).sort()];
  }, [leads]);

  const filteredLeads = useMemo(() => {
    return leads
      .filter((lead) => matchesLeadSearch(lead, searchTerm))
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
        currentLeads.map((lead) =>
          lead.id === updatedLead.id ? updatedLead : lead
        )
      );

      setSelectedLead(updatedLead);
      setSuccessMessage("Lead details saved successfully.");
    } catch (error) {
      console.error("Failed to update lead", error);
      setErrorMessage(
        "Unable to save lead details. Please check the backend and try again."
      );
    } finally {
      setIsSavingDetails(false);
    }
  };

  const handleGenerateOutreach = async () => {
    if (!selectedLead) return;

    setIsGeneratingOutreach(true);
    setErrorMessage("");

    try {
      const response = await generateOutreach({
        name: selectedLead.name,
        category: selectedLead.category,
        phone: selectedLead.phone,
        website: selectedLead.website,
        priority: selectedLead.priority,
        notes: selectedLead.notes,
      });

      setOutreach(response);
      setSuccessMessage("Nestora Copilot generated outreach successfully.");
    } catch (error) {
      console.error("Failed to generate outreach", error);
      setErrorMessage("Unable to generate outreach. Please try again.");
    } finally {
      setIsGeneratingOutreach(false);
    }
  };

  const handleAnalyzeWebsite = async () => {
    if (!selectedLead?.website || selectedLead.website === "Not found") {
      alert("This lead doesn't have a website.");
      return;
    }

    setIsAnalyzingWebsite(true);
    setErrorMessage("");

    try {
      const result = await analyzeWebsite(selectedLead.website);
      setWebsiteAnalysis(result);
      setSuccessMessage("Website analysis completed.");
    } catch (error) {
      console.error("Website analysis failed", error);
      setErrorMessage("Website analysis failed. Please try again.");
    } finally {
      setIsAnalyzingWebsite(false);
    }
  };

  return (
    <main className="crm-page">
      <CRMHeader
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        onRefresh={loadSavedLeads}
      />
      <CRMWorkspace
  leads={filteredLeads}
  selectedLead={selectedLead}
  onSelectLead={setSelectedLead}
/>

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
        {viewMode === "board" ? (
          <CRMBoard leads={filteredLeads} onSelectLead={setSelectedLead} />
        ) : (
          <CRMTable
            leads={filteredLeads}
            isLoading={isLoading}
            selectedLeadId={selectedLead?.id}
            onSelectLead={setSelectedLead}
          />
        )}

        <CRMSidePanel
          selectedLead={selectedLead}
          onGenerateOutreach={handleGenerateOutreach}
          onAnalyzeWebsite={handleAnalyzeWebsite}
          isGeneratingOutreach={isGeneratingOutreach}
          isAnalyzingWebsite={isAnalyzingWebsite}
          onSaveLeadDetails={handleSaveLeadDetails}
          onCloseLead={() => setSelectedLead(null)}
          isSavingDetails={isSavingDetails}
          isAnalyzing={isAnalyzing}
          analysis={analysis}
          websiteAnalysis={websiteAnalysis}
          outreach={outreach}
        />
      </div>
    </main>
  );
}