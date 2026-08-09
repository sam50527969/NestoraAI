import { MessageCircle, RefreshCw } from "lucide-react";
import ConversationMessage from "./ConversationMessage";
import "./ConversationPanel.css";

export default function ConversationPanel({
  messages = [],
  isLoading = false,
  isRefreshing = false,
  errorMessage = "",
  onRefresh,
}) {
  return (
    <section className="conversation-panel">
      <header className="conversation-panel-header">
        <div>
          <div className="conversation-panel-eyebrow">
            <MessageCircle size={15} strokeWidth={2.2} />
            Executive Communication
          </div>
          <h2>Executive Conversations</h2>
          <p>Recent messages exchanged across Nestora&apos;s executive team.</p>
        </div>

        <button
          type="button"
          className="conversation-refresh-button"
          onClick={onRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw
            size={15}
            className={isRefreshing ? "conversation-spin" : ""}
          />
          Refresh
        </button>
      </header>

      {errorMessage && (
        <div className="conversation-panel-error">{errorMessage}</div>
      )}

      {isLoading ? (
        <div className="conversation-panel-state">
          Loading executive conversations...
        </div>
      ) : messages.length === 0 ? (
        <div className="conversation-panel-state">
          <MessageCircle size={24} strokeWidth={1.8} />
          <strong>No conversations yet</strong>
          <span>
            Executive messages will appear here once communication begins.
          </span>
        </div>
      ) : (
        <div className="conversation-panel-list">
          {messages.map((message, index) => (
            <ConversationMessage
              key={message.message_uid || message.id || `${message.sender}-${index}`}
              message={message}
            />
          ))}
        </div>
      )}
    </section>
  );
}
