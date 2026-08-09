import {
  ArrowRight,
  Bot,
  CheckCircle2,
  Clock3,
  MessageCircle,
} from "lucide-react";

import "./ConversationMessage.css";


function formatTime(value) {
  if (!value) {
    return "Just now";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Just now";
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}


function getMessageIcon(type) {
  const normalizedType = String(
    type || "message",
  )
    .trim()
    .toLowerCase();

  if (
    normalizedType === "response"
    || normalizedType === "reply"
  ) {
    return (
      <CheckCircle2
        size={15}
        strokeWidth={2.2}
      />
    );
  }

  if (
    normalizedType === "handoff"
    || normalizedType === "request"
  ) {
    return (
      <ArrowRight
        size={15}
        strokeWidth={2.2}
      />
    );
  }

  return (
    <MessageCircle
      size={15}
      strokeWidth={2.2}
    />
  );
}


export default function ConversationMessage({
  message,
}) {
  if (!message) {
    return null;
  }

  const sender =
    message.sender
    || message.executive
    || "AI Executive";

  const recipient =
    message.recipient
    || "Executive Team";

  const content =
    message.message
    || message.content
    || "No message content.";

  const subject =
    message.subject
    || "Executive update";

  const messageType =
    message.message_type
    || message.type
    || "message";

  const priority = String(
    message.priority || "normal",
  )
    .trim()
    .toLowerCase();

  const isRead =
    Boolean(message.is_read)
    || message.status === "read";

  return (
    <article
      className={`conversation-message priority-${priority}`}
    >
      <div className="conversation-message-avatar">
        <Bot
          size={17}
          strokeWidth={2.1}
        />
      </div>

      <div className="conversation-message-body">
        <div className="conversation-message-header">
          <div>
            <div className="conversation-message-route">
              <strong>{sender}</strong>

              <ArrowRight
                size={13}
                strokeWidth={2.2}
              />

              <span>{recipient}</span>
            </div>

            <h4>{subject}</h4>
          </div>

          <span
            className={`conversation-message-type type-${messageType}`}
          >
            {getMessageIcon(messageType)}

            {messageType}
          </span>
        </div>

        <p>{content}</p>

        <footer className="conversation-message-footer">
          <span>
            <Clock3
              size={12}
              strokeWidth={2.1}
            />

            {formatTime(
              message.created_at
              || message.createdAt,
            )}
          </span>

          <span
            className={
              isRead
                ? "message-read"
                : "message-unread"
            }
          >
            {isRead ? "Read" : "Unread"}
          </span>
        </footer>
      </div>
    </article>
  );
}
