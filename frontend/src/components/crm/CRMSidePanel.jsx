import Button from "../ui/Button";
import LeadDetailsPanel from "../LeadDetailsPanel";
import OutreachPanel from "./OutreachPanel";
import SalesAnalysisPanel from "./SalesAnalysisPanel";
import WebsiteAnalysisPanel from "./WebsiteAnalysisPanel";

function CRMSidePanel({
  selectedLead,
  onGenerateOutreach,
  onAnalyzeWebsite,
  isGeneratingOutreach,
  isAnalyzingWebsite,
  onSaveLeadDetails,
  onCloseLead,
  isSavingDetails,
  isAnalyzing,
  analysis,
  websiteAnalysis,
  outreach,
}) {
  return (
    <div className="crm-side-panel">
      {selectedLead && (
        <div className="copilot-action">
          <Button onClick={onGenerateOutreach} disabled={isGeneratingOutreach}>
            {isGeneratingOutreach ? "Generating..." : "✨ Open Nestora Copilot"}
          </Button>

          <Button
            variant="secondary"
            onClick={onAnalyzeWebsite}
            disabled={isAnalyzingWebsite}
          >
            {isAnalyzingWebsite ? "Analyzing..." : "🔍 Analyze Website"}
          </Button>
        </div>
      )}

      <LeadDetailsPanel
        lead={selectedLead}
        onSave={onSaveLeadDetails}
        onClose={onCloseLead}
        isSaving={isSavingDetails}
      />

      {isAnalyzing ? (
        <div className="crm-alert">Analyzing lead...</div>
      ) : (
        <SalesAnalysisPanel analysis={analysis} />
      )}

      <WebsiteAnalysisPanel analysis={websiteAnalysis} />

      <OutreachPanel outreach={outreach} />
    </div>
  );
}

export default CRMSidePanel;