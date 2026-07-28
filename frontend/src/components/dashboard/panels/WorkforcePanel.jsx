import AgentStatus from "../AgentStatus";
import CEOChat from "../../agents/ceo/CEOChat";

function WorkforcePanel() {
  return (
    <>
      <AgentStatus />
      <CEOChat />
    </>
  );
}

export default WorkforcePanel;