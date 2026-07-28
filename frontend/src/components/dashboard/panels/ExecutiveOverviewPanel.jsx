import ExecutiveBrief from "../ExecutiveBrief";
import OpportunityPanel from "../OpportunityPanel";

function ExecutiveOverviewPanel({ lead }) {
  return (
    <>
      <ExecutiveBrief />
      <OpportunityPanel lead={lead} />
    </>
  );
}

export default ExecutiveOverviewPanel;