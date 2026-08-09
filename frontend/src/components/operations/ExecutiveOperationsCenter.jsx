import ConversationPanel from "../conversations/ConversationPanel";
import useExecutiveOperations from "../../hooks/useExecutiveOperations";
import ExecutiveStatusPanel from "./ExecutiveStatusPanel";
import "./ExecutiveOperationsCenter.css";

export default function ExecutiveOperationsCenter() {
  const {
    executives,
    operationsSummary,
    connectionStatus,
    lastEventAt,
    isLoading,
    isRefreshing,
    errorMessage,
    refresh,
    messages,
    isMessagesLoading,
    isMessagesRefreshing,
    messagesError,
    refreshMessages,
  } = useExecutiveOperations();

  return (
    <section className="executive-operations-center">
      <header className="executive-operations-header">
        <div>
          <p className="executive-operations-eyebrow">
            AI Business Operating System
          </p>
          <h1>Executive Operations Center</h1>
          <p className="executive-operations-description">
            Monitor your executive workforce, review internal communication,
            track collaboration, and oversee mission execution from one command center.
          </p>
        </div>
      </header>

      <div className="executive-operations-grid">
        <ExecutiveStatusPanel
          executives={executives}
          summary={operationsSummary}
          connectionStatus={connectionStatus}
          lastEventAt={lastEventAt}
          isLoading={isLoading}
          isRefreshing={isRefreshing}
          errorMessage={errorMessage}
          onRefresh={refresh}
        />

        <ConversationPanel
          messages={messages}
          isLoading={isMessagesLoading}
          isRefreshing={isMessagesRefreshing}
          errorMessage={messagesError}
          onRefresh={refreshMessages}
        />

        <div className="operations-placeholder">
          <h3>Mission Timeline</h3>
          <p>Mission events and execution milestones will appear here.</p>
        </div>

        <div className="operations-placeholder">
          <h3>Collaboration Sessions</h3>
          <p>Active executive collaboration will appear here.</p>
        </div>

        <div className="operations-placeholder">
          <h3>CEO Decisions</h3>
          <p>Approved, rejected, and pending decisions will appear here.</p>
        </div>
      </div>
    </section>
  );
}
